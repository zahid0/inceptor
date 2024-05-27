import os

from crewai_tools import ScrapeWebsiteTool, SerperDevTool


def get_tools():
    tool_list = [ScrapeWebsiteTool()]
    if "SERPER_API_KEY" in os.environ:
        tool_list.append(SerperDevTool())
    else:
        from langchain_community.tools import DuckDuckGoSearchResults

        tool_list.append(DuckDuckGoSearchResults())
    return tool_list
