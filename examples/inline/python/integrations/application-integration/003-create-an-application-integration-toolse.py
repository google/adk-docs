from google.adk.agents.llm_agent import LlmAgent
from .tools import connector_tool

root_agent = LlmAgent(
    model='gemini-flash-latest',
    name='connector_agent',
    instruction="Help user, leverage the tools you have access to",
    tools=[connector_tool],
)