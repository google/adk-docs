from daytona_adk import DaytonaPlugin
from google.adk.agents import Agent

plugin = DaytonaPlugin(
  api_key="your-daytona-api-key" # Or set DAYTONA_API_KEY environment variable
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="sandbox_agent",
    instruction="Help users execute code and commands in a secure sandbox",
    tools=plugin.get_tools(),
)