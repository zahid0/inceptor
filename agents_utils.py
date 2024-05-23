import yaml
from crewai import Agent

def create_agent(role, llm=None):
    with open('agents_config.yaml', 'r') as file:
        agents_config = yaml.safe_load(file)

    agent_config = agents_config[role]

    extra_args = {}
    if llm is not None:
        extra_args["llm"] = llm
    agent = Agent(
        role=role,
        goal=agent_config['goal'],
        backstory=agent_config['backstory'],
        allow_delegation=agent_config.get('allow_delegation', False),
        verbose=agent_config.get('verbose', True),
        **extra_args
    )
    return agent
