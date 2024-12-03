from crewai import Agent
from crewai import Task
from crewai import Crew,Process
from dotenv import load_dotenv
from crewai_tools import PDFSearchTool
load_dotenv()

import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"]="gpt-4"

pdf_tool  = PDFSearchTool(pdf='PDF_Files/NLP.pdf')

pdf_researcher = Agent(
    role='PDF Content Researcher',
    goal='Extract relevant information for the topic {query} from the provided PDF document',
    verbose=True,
    memory=True,
    backstory=(
        "Expert in analyzing PDF documents and extracting pertinent information "
        "with deep understanding of technical content and context"
    ),
    tools=[pdf_tool],
    allow_delegation=True
)

content_writer = Agent(
    role='Content Synthesizer',
    goal='Create comprehensive summaries and analyses of PDF content related to {query}',
    verbose=True,
    memory=True,
    backstory=(
        "Skilled at synthesizing complex information into clear, organized content "
        "while maintaining accuracy and technical depth"
    ),
    tools=[pdf_tool],
    allow_delegation=False
)

research_task = Task(
    description=(
        "Search the PDF document for content related to {query}. "
        "Extract key information, important quotes, and relevant data."
    ),
    expected_output='A detailed report containing key findings and relevant excerpts from the PDF related to {query}',
    tools=[pdf_tool],
    agent=pdf_researcher
)

synthesis_task = Task(
    description=(
        "Create a comprehensive analysis based on the research findings about {query}. "
        "Organize the information logically and highlight key insights."
    ),
    expected_output='A well-structured document summarizing the PDF content related to {query} with analysis',
    tools=[pdf_tool],
    agent=content_writer,
    async_execution=False,
    output_file='pdf-analysis.md'
)

crew = Crew(
    agents=[pdf_researcher, content_writer],
    tasks=[research_task, synthesis_task],
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=100,
    share_crew=True
)

#result = crew.kickoff(inputs={'topic': 'What is visual hierarchies?'})
#print(result)