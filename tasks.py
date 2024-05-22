from crewai import Task

from models import AgentTaskList, Character


def create_plan_task(agent):
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
        agent=agent,
    )
    return create_plan


def create_review_task(agent):
    review_plan = Task(
        description=(
            "Review the high-level plan made by Strategy Maker "
            "for the goal described below:\n"
            "{goal}\n\n"
            "Ensure that the plan is as efficient as possible without any "
            "unnecessary steps or overlaps. Also, confirm that there are no "
            "missing elements in the plan that could prevent it from achieving the goal."
        ),
        expected_output=(
            "Final list of tasks after revision based on critical review. "
            "Each task will have description "
            "and expected_output fields."
        ),
        output_json=AgentTaskList,
        agent=agent,
    )
    return review_plan


def create_team_task(agent):
    create_team = Task(
        description=(
            "Clearly define the role to hire for the following task:\n"
            "# Task Description: {description}\n"
            "# Expected Output: {expected_output}\n\n"
            "The task is the part of the following final goal:\n"
            "{goal}"
        ),
        expected_output=(
            "Output the details of the role most suitable for the task.\n"
            "The roles must contain the following:\n"
            "1. role: name of the role. For example Software Engineer.\n"
            "2. goal: the clearly defined expertise of the role. "
            "This should be addressed in second person\n"
            "3. backstory: The backstory highlights capabilities of the role "
            "that makes in most suitable for the task. "
            "This should be addressed in second person to the role"
        ),
        output_json=Character,
        agent=agent,
    )
    return create_team
