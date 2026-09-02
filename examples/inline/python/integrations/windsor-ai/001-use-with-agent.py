from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

WINDSOR_API_KEY = "YOUR_WINDSOR_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="windsor_agent",
    instruction="Help users analyze their marketing and business data.",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.windsor.ai",
                headers={
                    "Authorization": f"Bearer {WINDSOR_API_KEY}",
                },
            ),
        )
    ],
)