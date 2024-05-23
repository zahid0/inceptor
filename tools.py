import os

from crewai_tools import ScrapeWebsiteTool, SerperDevTool


def get_tools():
    tool_list = [ScrapeWebsiteTool()]
    if "SERPER_API_KEY" in os.environ:
        tool_list.append(SerperDevTool())
    return tool_list
