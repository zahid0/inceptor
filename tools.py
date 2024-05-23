from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.agent_toolkits import FileManagementToolkit
from crewai_tools import ScrapeWebsiteTool, WebsiteSearchTool, CodeDocsSearchTool


def get_tools():
    toolkit = FileManagementToolkit()  # If you don't provide a root_dir, operations will default to the current working directory
    file_management_tools = toolkit.get_tools()
    return file_management_tools + [DuckDuckGoSearchResults(), ScrapeWebsiteTool(),
                                    WebsiteSearchTool(), CodeDocsSearchTool()]
