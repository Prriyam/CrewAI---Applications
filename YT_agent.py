from crewai import Agent
from crewai import Task
from crewai import Crew,Process
from dotenv import load_dotenv
from crewai_tools import YoutubeChannelSearchTool
load_dotenv()

import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"]="gpt-4"

yt_tool = YoutubeChannelSearchTool(youtube_channel_handle='@codebasics')

blog_researcher=Agent(
    role='Blog Researcher from Youtube Videos',
    goal='get the relevant video transcription for the topic {query} from the provided YouTube channel',
    verboe=True,
    memory=True,
    backstory=(
       "Expert in understanding videos in AI Data Science, Machine Learning, Natural Language Processing, Deep Learning and Generative AI and providing suggestion" 
    ),
    tools=[yt_tool],
    allow_delegation=True
)

blog_writer=Agent(
    role='Blog Writer',
    goal='Narrate compelling tech stories about the video {query} from YouTuve video',
    verbose=True,
    memory=True,
    backstory=(
        """Simplify complex topics, craft engaging narratives that captivate and bringing new discoveries to light in an accessible manner."""
    ),
    tools=[yt_tool],
    allow_delegation=False
)

research_task = Task(
  description=(
    "Identify the video {query}."
    "Get detailed information about the video from the YouTube channel"
  ),
  expected_output='A comprehensive 2 paragraphs long report based on the {query} of video content.',
  tools=[yt_tool],
  agent=blog_researcher,
  async_execution=True
)

write_task = Task(
  description=(
    "Get the information from the YouTube channel on the topic {query}."
  ),
  expected_output='Summarize the information from the YouTube channel video on the topic{query} and create the content for the blog',
  tools=[yt_tool],
  agent=blog_writer,
  async_execution=False,
  context=[research_task]
  #output_file='new-blog-post.md'
)

crew = Crew(
  agents=[blog_researcher, blog_writer],
  tasks=[research_task, write_task],
  process=Process.sequential,
  #memory=True,
  cache=True,
  max_rpm=100,
  share_crew=True
)

#result=crew.kickoff(inputs={'topic':'What is BERT?'})
#print(result)