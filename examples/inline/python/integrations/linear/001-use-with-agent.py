from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

root_agent = Agent(
    model="gemini-flash-latest",
    name="linear_agent",
    instruction="Help users manage issues, projects, and cycles in Linear",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        "https://mcp.linear.app/mcp",
                    ]
                ),
                timeout=30,
            ),
        )
    ],
)