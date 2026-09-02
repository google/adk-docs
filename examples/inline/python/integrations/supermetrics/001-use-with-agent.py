from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

SUPERMETRICS_API_KEY = "YOUR_SUPERMETRICS_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="supermetrics_agent",
    instruction="Help users query and analyze their marketing data from Supermetrics",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.supermetrics.com/mcp",
                headers={
                    "Authorization": f"Bearer {SUPERMETRICS_API_KEY}",
                },
            ),
        )
    ],
)