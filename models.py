from typing import List

from pydantic import BaseModel


class AgentTask(BaseModel):
    description: str
    expected_output: str


class AgentTaskList(BaseModel):
    tasks: List[AgentTask]


class Character(BaseModel):
    role: str
    goal: str
    backstory: str
    tools: List[str]
