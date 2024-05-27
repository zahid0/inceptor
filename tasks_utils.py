from crewai import Task

from models import AgentTaskList, Character


def create_plan_task(agent):
    create_plan = Task(
        description=(
            "Please generate a high level plan to achieve the following goal:\n\n"
            "{goal}\n\n"
            "The plan should ensure high quality of the work. "
            "The plan should consider efficient execution by dividing "
            "and conquering whenever possible. "
            "There should be no overlap in the scope of tasks. "
            "The plan should not be too granular, and should not have more than 5 tasks."
        ),
        expected_output=(
            "Please output a list of tasks. "
            "Each task should contain the following fields:\n"
            "1. description: A concise description of the task clearly conveying what needs to be done\n"
            "2. expected_output: The expected output when the task is complete. The output can be a file or text needed by other tasks or indicating the success or failure status of the current task"
        ),
        agent=agent,
    )
    return create_plan


def create_review_task(agent, output_file):
    review_plan = Task(
        description=(
            "Please provide a revised high-level plan for the goal described below, "
            "ensuring that the plan is as efficient as possible without any unnecessary steps or overlaps. "
            "Also, confirm that there are no missing elements in the plan that could prevent it from achieving the goal. "
            "Each task should require unique skill or expertise. "
            "If two or more tasks need similar expertise, they should be combined into one. "
            "The goal is:\n\n"
            "{goal}\n\n"
        ),
        expected_output=(
            "Please provide a final list of tasks after reviewing the plan. "
            "Each task should have a description and expected output."
        ),
        output_json=AgentTaskList,
        human_input=True,
        agent=agent,
        output_file=output_file,
    )
    return review_plan


def create_team_task(
    agent, output_file, description, expected_output, goal, tools_list
):
    create_team = Task(
        description=(
            f"Please provide a detailed description of the role to hire for the following task:\n\n"
            f"Task Description: {description}\n"
            f"Expected Output: {expected_output}\n\n"
            f"The task is a part of the following final goal:\n\n"
            f"{goal}\n\n"
            f"A list of tools is available to be used, each with a name and description. Select the tools required by this role.\n\n"
            f"The list of tools is as follows:\n"
            f"{tools_list}"
        ),
        expected_output=(
            "Output the details of the role most suitable for the task in the following format:\n"
            "1. role: name of the role. For example Software Engineer.\n"
            "2. goal: the clearly defined expertise of the role. This should be addressed in second person\n"
            "3. backstory: The backstory highlights capabilities of the role that make it most suitable for the task. This should be addressed in second person to the role\n"
            f"4. tools: selected list of tools from the given tools required by this role."
        ),
        output_json=Character,
        output_file=output_file,
        agent=agent,
    )
    return create_team
