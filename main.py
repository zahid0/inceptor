from crewai import Agent, Crew, Task

import tasks_utils
from agents_utils import create_agent
from models import AgentTaskList, Character
from tools import get_tools


def create_crew(agents, tasks, process=None, manager_llm=None, embedder=None):
    crew_kwargs = {
        "agents": agents,
        "tasks": tasks,
        "verbose": 2,
        "memory": False,
    }
    if embedder is not None:
        crew_kwargs["embedder"] = embedder
    if process is not None:
        crew_kwargs["process"] = process
    if manager_llm is not None:
        crew_kwargs["manager_llm"] = manager_llm
    return Crew(**crew_kwargs)


def plan(goal, llm=None, embedder=None):
    strategy_maker = create_agent(role="Strategy Maker", llm=llm)
    critic = create_agent(role="Strategy Reviewer", llm=llm)
    plan_task = tasks_utils.create_plan_task(strategy_maker)
    review_task = tasks_utils.create_review_task(
        critic, output_file="outputs/tasks.json"
    )
    planning_crew = create_crew(
        agents=[strategy_maker, critic],
        tasks=[plan_task, review_task],
        embedder=embedder,
    )
    tasks_json = planning_crew.kickoff(inputs={"goal": goal})
    tasks_list = AgentTaskList.parse_raw(tasks_json)

    agent_creator = create_agent(role="Leader", llm=llm)

    team_creation_tasks = []
    # Iterate over tasks in tasks_list to create new tasks
    for index, task in enumerate(tasks_list.tasks):
        # Generate output file name
        output_file = f"outputs/role-{index}.json"

        # Create a new task using the updated function signature
        new_task = tasks_utils.create_team_task(
            agent=agent_creator,  # Assuming the same agent for simplicity
            output_file=output_file,
            description=task.description,
            expected_output=task.expected_output,
            goal=goal,
        )
        team_creation_tasks.append(new_task)

    team_setup_crew = create_crew(
        agents=[agent_creator], tasks=team_creation_tasks, embedder=embedder
    )

    team_setup_crew.kickoff()
    return tasks_json


def execute(tasks_json, llm=None, embedder=None):
    tools = get_tools()
    tasks_list = AgentTaskList.parse_raw(tasks_json)
    llm_args = {}
    if llm is not None:
        llm_args["llm"] = llm

    tasks = []
    agents = []

    for i, task in enumerate(tasks_list.tasks):
        with open(f"outputs/role-{i}.json", "r") as f:
            character = Character.parse_raw(f.read())
        agent = Agent(
            role=character.role,
            goal=character.goal,
            backstory=character.backstory,
            tools=tools,
            allow_delegation=False,
            verbose=True,
            **llm_args,
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
        agents=agents,
        tasks=tasks,
        embedder=embedder,
        # , process=Process.hierarchical, manager_llm=llm,
    )

    master_crew.kickoff()
