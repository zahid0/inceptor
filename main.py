from crewai import Agent, Crew, Task

import tasks_utils
from agents_utils import create_agent
from models import AgentTaskList, Character
from tools import get_tools


def create_crew(agents, tasks, process=None, manager_llm=None, embedder=None):
    crew_kwargs = {
        "agents": agents,
        "tasks": tasks,
        "verbose": True,
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
    tasks_output = planning_crew.kickoff(inputs={"goal": goal})
    tasks_json = tasks_output.json
    tasks_list = AgentTaskList.parse_raw(tasks_json)

    agent_creator = create_agent(role="Leader", llm=llm)

    team_creation_tasks = []
    # Iterate over tasks in tasks_list to create new tasks
    tools = get_tools()
    tools_list = "\n".join(
        f"{i+1}. Name: {tool.name}\n   Description: {tool.description}"
        for i, tool in enumerate(tools)
    )
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
            tools_list=tools_list,
        )
        team_creation_tasks.append(new_task)

        team_setup_crew = create_crew(
            agents=[agent_creator], tasks=[new_task], embedder=embedder
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

    context = None
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
        task_args = {
            "description": task.description,
            "expected_output": task.expected_output,
            "agent": agent,
            "context": context,
        }
        if context is not None:
            task_args["context"] = [context]
        task = Task(**task_args)

        tasks.append(task)
        context = task  # Update the context for the next iteration

    master_crew = create_crew(
        agents=agents,
        tasks=tasks,
        embedder=embedder,
        # , process=Process.hierarchical, manager_llm=llm,
    )

    master_crew.kickoff()
