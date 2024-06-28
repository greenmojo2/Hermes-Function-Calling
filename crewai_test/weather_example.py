import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# with ollama localhost
os.environ["OPENAI_API_BASE"] = 'http://192.168.8.17:8080/v1'
os.environ["OPENAI_MODEL_NAME"] ='interstellarninja/hermes-2-theta-llama-3-8b:latest'  # Adjust based on available model
#os.environ["OPENAI_MODEL_NAME"] ='adrienbrault/nous-hermes2pro:Q4_0'  # Adjust based on available model
os.environ["OPENAI_API_KEY"] ='sk-111111111111111111111111111111111111111111111111'

# with lm studio localhost
#os.environ["OPENAI_API_BASE"] = 'http://localhost:1234/v1'
#os.environ["OPENAI_MODEL_NAME"] = 'NousResearch/Hermes-2-Pro-Llama-3-8B-GGUF/Hermes-2-Pro-Llama-3-8B-Q4_K_M.gguf'
#os.environ["OPENAI_API_KEY"] ='lm-studio'

# search_tool = SerperDevTool()

# Define your agents with roles and goals
tester = Agent(
  role='Tool Decider',
  goal='Given a prompt, execute tool calls as required.',
  backstory="""You are a test engineer who tests the tools provided by the LLM Toolkit.
  You have a knack for dissecting complex data and presenting actionable insights.""",
  verbose=True,
  allow_delegation=False,
  tools=[search_tool]
)
writer = Agent(
  role='Tech Content Strategist',
  goal='Craft compelling content on tech advancements',
  backstory="""You are a renowned Content Strategist, known for your insightful and engaging articles.
  You transform complex concepts into compelling narratives.""",
  verbose=True,
  allow_delegation=True
)

# Create tasks for your agents
task1 = Task(
  description="""Conduct a comprehensive analysis of the latest advancements in AI in 2024.
  Identify key trends, breakthrough technologies, and potential industry impacts.""",
  expected_output="Full analysis report in bullet points",
  agent=researcher
)

task2 = Task(
  description="""Using the insights provided, develop an engaging blog
  post that highlights the most significant AI advancements.
  Your post should be informative yet accessible, catering to a tech-savvy audience.
  Make it sound cool, avoid complex words so it doesn't sound like AI.""",
  expected_output="Full blog post of at least 4 paragraphs",
  agent=writer
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher, writer],
  tasks=[task1, task2],
  verbose=2, # You can set it to 1 or 2 to different logging levels
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)
