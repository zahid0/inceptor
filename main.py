import os

from crewai import Agent, Crew, Task
from crewai.process import Process
from langchain_groq import ChatGroq

from agents import create_critic, create_role_creator, create_strategy_maker
from models import AgentTaskList, Character
from tasks import create_plan_task, create_review_task, create_team_task


def create_crew(agents, tasks, process=Process.sequential, manager_llm=None):
    return Crew(
        agents=agents,
        tasks=tasks,
        process=process,
        manager_llm=manager_llm,
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


def main(goal):
    llm = ChatGroq(model="llama3-8b-8192", max_tokens=2048)
    strategy_maker = create_strategy_maker(llm)
    critic = create_critic(llm)
    plan_task = create_plan_task(strategy_maker)
    review_task = create_review_task(critic)
    planning_crew = create_crew(
        agents=[strategy_maker, critic], tasks=[plan_task, review_task]
    )
    tasks_json = planning_crew.kickoff(inputs={"goal": goal})
    tasks_list = AgentTaskList.parse_raw(tasks_json)

    agent_creator = create_role_creator(llm)
    team_creation_task = create_team_task(agent_creator)
    team_setup_crew = create_crew(agents=[agent_creator], tasks=[team_creation_task])

    tasks = []
    agents = []

    for task in tasks_list.tasks:
        agent_json = team_setup_crew.kickoff(
            inputs={
                "description": task.description,
                "expected_output": task.expected_output,
                "goal": goal,
            }
        )
        character = Character.parse_raw(agent_json)
        agent = Agent(
            role=character.role,
            goal=character.goal,
            backstory=character.backstory,
            allow_delegation=False,
            llm=llm,
            verbose=True,
        )
        agents.append(agent)
        tasks.append(
            Task(
                description=task.description,
                expected_output=task.expected_output,
                agent=agent,
            )
        )

    master_crew = create_crew(
        agents=agents, tasks=tasks, process=Process.hierarchical, manager_llm=llm
    )

    master_crew.kickoff()


main(
    "Develop an MVP for AI application for interview preparation. The application is for personal. It generate interview questions for given job reqiurements. transcribe user answer audio using whisper.cpp and review the answer with a lanrge language model providing feedback. It is a cli app intented to run from terminal on mac."
)
