from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


root_agent = Agent(
    model="gemini-flash-latest",
    name="atlan_agent",
    instruction="Help users search, discover, and manage enterprise data assets using Atlan",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        "https://mcp.atlan.com/mcp",
                    ]
                ),
                timeout=30,
            ),
        )
    ],
)