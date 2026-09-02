from google.adk.agents.llm_agent import LlmAgent
from .tools import sample_toolset

root_agent = LlmAgent(
    model='gemini-flash-latest',
    name='enterprise_assistant',
    instruction='Help user, leverage the tools you have access to',
    tools=[sample_toolset],
)