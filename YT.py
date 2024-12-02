import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import YoutubeChannelSearchTool
from dotenv import load_dotenv
import os

load_dotenv()

import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"]="gpt-4"


def init_crew():
    yt_tool = YoutubeChannelSearchTool(youtube_channel_handle='@codebasics')
    
    blog_researcher=Agent(
        role='Blog Researcher from Youtube Videos',
        goal='get the relevant video transcription for the topic {topic} from the provided Yt channel',
        verbose=True,
        memory=True,
        backstory=(
        "Expert in understanding videos in AI Data Science, MAchine Learning And GEN AI and providing suggestion" 
        ),
        tools=[yt_tool],
        allow_delegation=True
    )
        
    blog_writer=Agent(
        role='Blog Writer',
        goal='Narrate compelling tech stories about the video {topic} from YT video',
        verbose=True,
        memory=True,
        backstory=(
            "With a flair for simplifying complex topics, you craft"
            "engaging narratives that captivate and educate, bringing new"
            "discoveries to light in an accessible manner."
        ),
        tools=[yt_tool],
        allow_delegation=False
    )
    
    research_task = Task(
    description=(
        "Identify the video {topic}."
        "Get detailed information about the video from the channel video."
    ),
    expected_output='A comprehensive 3 paragraphs long report based on the {topic} of video content.',
    tools=[yt_tool],
    agent=blog_researcher,
    )
    
    write_task = Task(
    description=(
        "get the info from the youtube channel on the topic {topic}."
    ),
    expected_output='Summarize the info from the youtube channel video on the topic{topic} and create the content for the blog',
    tools=[yt_tool],
    agent=blog_writer,
    async_execution=False,
    output_file='new-blog-post.md'  # Example of output customization
    )
    
    crew = Crew(
    agents=[blog_researcher, blog_writer],
    tasks=[research_task, write_task],
    process=Process.sequential,  # Optional: Sequential task execution is default
    #memory=True,
    cache=True,
    max_rpm=100,
    share_crew=True
    )
    
    return crew

def display_results(result):
   # Convert CrewOutput to string and clean it
   content = str(result).strip()
   if "raw" in content:
       # Extract content between first raw:" and next "
       start = content.find('raw":"') + 6
       end = content.find('","', start)
       if start >= 0 and end >= 0:
           clean_content = content[start:end]
           # Format the content
           st.write(clean_content.replace('\\n', '\n'))
   else:
       st.write(content)

def main():
    st.title("YouTube Content Analysis")
    topic = st.text_input("Enter Topic:", placeholder="e.g., What is BERT?")
    
    if st.button("Start Analysis"):
        if topic:
            with st.spinner("Analyzing content..."):
                try:
                    crew = init_crew()
                    result = crew.kickoff(inputs={'topic': topic})
                    display_results(result)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a topic")

if __name__ == "__main__":
    main()
