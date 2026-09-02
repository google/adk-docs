from google.adk.agents import LlmAgent
from google.adk.tools.spanner import SpannerAdminToolset

# Initialize the Spanner admin toolset
spanner_admin_tools = SpannerAdminToolset()

# Register the toolset with your agent, ensuring model and instructions are provided
agent = LlmAgent(
    name="SpannerAdminAgent",
    model="gemini-flash-latest",
    instruction=(
        "You are a helpful database administrator. Use the SpannerAdminToolset "
        "to manage and query Spanner instances and databases in the project."
    ),
    tools=[spanner_admin_tools]
)