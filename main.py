import os

from crewai import Agent, Crew, Task
from crewai.process import Process

from agents_utils import create_agent
import tasks_utils

from models import AgentTaskList, Character
from tools import get_tools


def create_crew(agents, tasks, process=None, manager_llm=None, embedder=None):
    crew_kwargs = {
        'agents': agents,
        'tasks': tasks,
        'verbose': 2,
        'memory': True,
    }
    if embedder is not None:
        crew_kwargs['embedder'] = embedder
    if process is not None:
        crew_kwargs['process'] = process
    if manager_llm is not None:
        crew_kwargs['manager_llm'] = manager_llm
    return Crew(**crew_kwargs)


def main(goal, llm=None, embedder=None):
    tools = get_tools()
    strategy_maker = create_agent(role='Strategy Maker', llm=llm)
    critic = create_agent(role='Strategy Reviewer', llm=llm)
    plan_task = tasks_utils.create_plan_task(strategy_maker)
    review_task = tasks_utils.create_review_task(critic)
    planning_crew = create_crew(
        agents=[strategy_maker, critic], tasks=[plan_task, review_task],
        embedder=embedder
    )
    tasks_json = planning_crew.kickoff(inputs={"goal": goal})
    tasks_list = AgentTaskList.parse_raw(tasks_json)

    agent_creator = create_agent(role='Leader', llm=llm)
    team_creation_task = tasks_utils.create_team_task(agent_creator)
    team_setup_crew = create_crew(agents=[agent_creator], tasks=[team_creation_task],
        embedder=embedder)

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
            tools = tools,
            allow_delegation=False,
            llm=llm,
            verbose=True,
        )
        agents.append(agent)
        tasks.append(
            Task(
                description=task.description,
                expected_output=task.expected_output,
                human_input=True,
                agent=agent,
            )
        )

    master_crew = create_crew(
        agents=agents, tasks=tasks, embedder=embedder,
        #, process=Process.hierarchical, manager_llm=llm,
    )

    master_crew.kickoff()

