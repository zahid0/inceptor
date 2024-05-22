import json
import os
from typing import List

from crewai import Agent, Crew, Task
from langchain_groq import ChatGroq
from pydantic import BaseModel
from crewai.process import Process


llm = ChatGroq(model = "llama3-8b-8192", max_tokens=2048)

strategy_maker = Agent(
    role="Strategy Maker",
    goal=(
        "You break down the goal in high level tasks "
        "that can be easily completed by divide and conquer"
    ),
    backstory=(
        "You are a great visionary strategy maker. "
        "You effectively break down the goal in clearly defined tasks. "
        "You carefully consider the efficiency and quality of work "
        "while making the strategy. "
    ),
    llm=llm,
    allow_delegation=False,
    verbose=True,
)


class AgentTask(BaseModel):
    description: str
    expected_output: str


class AgentTaskList(BaseModel):
    tasks: List[AgentTask]


create_plan = Task(
    description=(
        "Make a high level plan to acheive the following goal:\n"
        "{goal}\n\n"
        "The the plan must ensure the high quality of the work. "
        "The plan must consider the efficient execution by divide "
        "and conquer when ever possible. "
        "There should not be any overlap in the scope of steps."
    ),
    expected_output=(
        "Output the list of tasks. "
        "The tasks contains the following fields:\n"
        "1. description: Concise description of the task clearly conveying what needs to be done\n"
        "2. expected_output: What is the expected output when the task is complete. The output can be file or text needed by other tasks or indicating the success or failure status of current task"
    ),
    agent=strategy_maker,
)

critic = Agent(
	role="Strategy Reviewer",
	goal="Ensure the execution plan is the best possible.",
	backstory=(
		"You are experience strategy reviewer. You critically "
        "review the plan to find shortcomings and revise "
        "the plan to make it best possible."
        ),
    llm=llm,
    allow_delegation=False,
    verbose=True,
)

review_plan = Task(
    description=(
        "Review the high-level plan made by Strategy Maker "
        "for the goal described below:\n"
        "{goal}\n\n"
        "Ensure that the plan is as efficient as possible without any "
        "unnecessary steps or overlaps. Also, confirm that there are no "
        "missing elements in the plan that could prevent it from achieving the goal."
        ),
    expected_output = (
        "Final list of tasks after revision based on critical review. "
        "Each task will have description "
        "and expected_output fields."
        ),
    output_json=AgentTaskList,
    output_file="tasks.json",
    agent=critic
)

crew = Crew(
    agents=[strategy_maker, critic],
    tasks=[create_plan, review_plan],
    embedder={
        "provider": "openai",
        "config": {
            "model": "jina-embeddings-v2-base-en",
            "api_key": os.getenv("JINA_API_KEY"),
            "api_base": "https://api.jina.ai/v1",
        },
    },
    verbose=2,
    memory=True,
)

inputs = {"goal": "Develop an MVP for AI application for interview preparation. The application is for personal. It generate interview questions for given job reqiurements. transcribe user answer audio using whisper.cpp and review the answer with a lanrge language model providing feedback. It is a cli app intented to run from terminal on mac."}

tasks_json = crew.kickoff(inputs=inputs)
# Deserialize the json string to a list of AgentTask objects
tasks_list = AgentTaskList.parse_raw(tasks_json)

agent_creator = Agent(
    role="Leader",
    goal="Define role to hire for the given task",
    backstory=(
        "You are a great visionary leader. "
        "You are putting together "
        "an efficient team for the given task. "
        "You make sure that the efficiency and "
        "quality of the work are considered "
        "while putting the team together"
    ),
    llm=llm,
    allow_delegation=False,
    verbose=True,
)


class Character(BaseModel):
    role: str
    goal: str
    backstory: str


create_team = Task(
    description=(
        "Clearly define the role to hire for the following task:\n"
        "# Task Description: {description}\n"
        "# Expected Output: {expected_output}\n"
    ),
    expected_output=(
        "Output the details of the role most suitable for the task.\n"
        "The roles must contain the following:\n"
        "1. role: name of the role. For example Software Engineer.\n"
        "2. goal: the clearly defined expertise of the role.\n"
        "3. backstory: The backstory of the role highlighting what makes it most suitable for the task. "
        "The backstory focuses on capabilities rather than credentials"
    ),
    output_json=Character,
    agent=agent_creator,
)

agent_creator_crew = Crew(
    agents=[agent_creator],
    tasks=[create_team],
    embedder={
        "provider": "openai",
        "config": {
            "model": "jina-embeddings-v2-base-en",
            "api_key": os.getenv("JINA_API_KEY"),
            "api_base": "https://api.jina.ai/v1",
        },
    },
    verbose=2,
    memory=True,
)


tasks = []
agents = []

for task in tasks_list.tasks:
    agent_json = agent_creator_crew.kickoff(inputs={
        "description" : task.description,
        "expected_output": task.expected_output
        })
    print(agent_json)
    character = Character.parse_raw(agent_json)
    agent = Agent(
            role = character.role,
            goal = character.goal,
            backstory = character.backstory,
            allow_delegation = False,
            llm = llm,
            verbose = True
            )
    agents.append(agent)
    tasks.append(Task(description=task.description, expected_output=task.expected_output, agent=agent))

master_crew = Crew(
    agents=agents,
    tasks=tasks,
    process=Process.hierarchical,
    manager_llm = ChatGroq(model="llama3-70b-8192", max_tokens=1024)
    embedder={
        "provider": "openai",
        "config": {
            "model": "jina-embeddings-v2-base-en",
            "api_key": os.getenv("JINA_API_KEY"),
            "api_base": "https://api.jina.ai/v1",
        },
    },
    verbose=2,
    memory=True,
)

master_crew.kickoff()
