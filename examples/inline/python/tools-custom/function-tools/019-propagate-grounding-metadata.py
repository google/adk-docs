from google.adk.agents import Agent
from google.adk.tools import AgentTool

search_specialist_agent = Agent(
    # Specify your generative model
    model="gemini-flash-latest",
    name="search_specialist_agent",
    instruction=(
        "You are a search expert. Find and "
        "compile citations on requested topics."
    ),
    # Add any search tools here
)

search_agent_tool = AgentTool(
    agent=search_specialist_agent,
    # Keeps citations intact back to the root
    propagate_grounding_metadata=True
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="root_agent",
    description=(
        "A central coordinator that delegates "
        "to specialist agents."
    ),
    tools=[search_agent_tool]
)