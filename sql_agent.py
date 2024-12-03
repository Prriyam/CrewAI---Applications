from dotenv import load_dotenv
from textwrap import dedent
from crewai import Agent, Crew, Process, Task
from crewai_tools import tool
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
)
from langchain_community.chat_models import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
load_dotenv() 

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

db_user = "root"
db_password = quote_plus(os.getenv('PASSWORD'))
db_host = os.getenv('HOST')
port = os.getenv('PORT')
db_name = os.getenv('DBNAME')
db_url= f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{port}/{db_name}"

db = SQLDatabase.from_uri(db_url)

llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-4o"
)

@tool("list_tables")
def list_tables() -> str:
    """List all tables in the database."""
    return ListSQLDatabaseTool(db=db).invoke("")

@tool("tables_schema")
def tables_schema(tables: str) -> str:
    """Retrieve the schema for the specified tables."""
    tool = InfoSQLDatabaseTool(db=db)
    return tool.invoke(tables)

@tool("execute_sql")
def execute_sql(sql_query: str) -> str:
    """Execute the provided SQL query and return the results."""
    return QuerySQLDataBaseTool(db=db).invoke(sql_query)

sql_agent = Agent(
    role='MySQL Database Expert',
    goal='Execute precise SQL queries and extract meaningful data',
    backstory=dedent("""
        You are an expert database analyst with multiple specializations:
        1. Table Analysis: You thoroughly examine database structure to identify relevant tables
        2. Schema Understanding: You deeply understand table relationships and data types
        3. Query Crafting: You write optimized SQL queries that target exactly what's needed
        4. Query Validation: You carefully check queries for accuracy and efficiency
        5. Result Focus: You ensure query execution provides clear, relevant results
        
        Your primary focus is getting accurate data while hiding technical complexity.
    """),
    verbose=True,
    tools=[list_tables, tables_schema, execute_sql],
    llm=llm
)

report_writer = Agent(
    role="Data Storyteller",
    goal="Transform database results into clear, meaningful insights",
    backstory=dedent("""
        You are a skilled communicator who:
        1. Takes raw database results and presents them in plain language
        2. Focuses solely on the information requested
        3. Avoids technical jargon and database terminology
        4. Presents results as if having a conversation
        5. Ensures accuracy while maintaining simplicity
        
        You craft responses that anyone can understand, regardless of technical background.
    """),
    llm=llm,
    allow_delegation=False
)

list_tables_task = Task(
    description=dedent("""
        1. Identify and analyze tables needed for query: {query}
        2. Extract required data using optimized SQL
        3. Focus on getting precise results
        4. Ensure data accuracy and completeness
        5. Return only the relevant query results
    """),
    expected_output=dedent("""
        Clear and focused query results without technical details or database information.
        Results should be raw data ready for the report writer to process.
    """),
    agent=sql_agent
)

write_report = Task(
    description=dedent("""
        Present the database findings in 2-3 clear, informative sentences that:
        1. Directly answer the question asked
        2. Present facts from the database in natural language
        3. Connect related information when relevant
        4. Focus on what the data shows without extra context
        5. Write the Final answer in bullet points
        
        For example, instead of just:
        "Karl Berry won Emmy, Oscar, and Tony awards."
        
        Write:
        "Our database reveals that Karl Berry has achieved recognition across the entertainment industry with three major awards. His accomplishments include winning an Emmy, an Oscar, and a Tony award, demonstrating his versatility as a performer."
    """),
    expected_output="2-3 clear sentences that present database findings in an informative way",
    agent=report_writer,
    context=[list_tables_task]
)

crew = Crew(
    agents=[sql_agent,report_writer],
    tasks=[list_tables_task,write_report],
    process=Process.sequential,
    verbose=True,
    #memory=True,
    cache=True,
    max_rpm=100,
    share_crew=True,
    output_log_file="crew.log",
)

#inputs = {
#    "query": "Who is the main chair on the advisor board??"
#}

#result = crew.kickoff(inputs=inputs)