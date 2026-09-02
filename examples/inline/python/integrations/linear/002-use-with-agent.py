from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

LINEAR_API_KEY = "YOUR_LINEAR_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="linear_agent",
    instruction="Help users manage issues, projects, and cycles in Linear",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.linear.app/mcp",
                headers={
                    "Authorization": f"Bearer {LINEAR_API_KEY}",
                },
            ),
        )
    ],
)