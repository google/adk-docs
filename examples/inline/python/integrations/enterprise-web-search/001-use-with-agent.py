from google.adk.agents import Agent
from google.adk.tools import enterprise_web_search

root_agent = Agent(
    model="gemini-flash-latest",
    name="enterprise_search_agent",
    instruction="Answer user questions accurately using enterprise-compliant web search results.",
    tools=[enterprise_web_search],
)