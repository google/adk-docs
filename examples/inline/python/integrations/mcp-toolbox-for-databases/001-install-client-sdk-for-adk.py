from google.adk import Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

toolset = ToolboxToolset(
    server_url="http://127.0.0.1:5000"
)

root_agent = Agent(
    ...,
    tools=[toolset] # Provide the toolset to the Agent
)