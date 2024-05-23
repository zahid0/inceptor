import os
from langchain_community.agent_toolkits import FileManagementToolkit
from crewai_tools import ScrapeWebsiteTool, SerperDevTool


def get_tools():
    toolkit = FileManagementToolkit()  # If you don't provide a root_dir, operations will default to the current working directory
    file_management_tools = toolkit.get_tools()
    tool_list = file_management_tools + [ScrapeWebsiteTool()] 
    if 'SERPER_API_KEY' in os.environ:
        tool_list.append(SerperDevTool())
    return tool_list
