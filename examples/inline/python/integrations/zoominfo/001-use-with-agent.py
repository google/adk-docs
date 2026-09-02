from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


root_agent = Agent(
    model="gemini-flash-latest",
    name="zoominfo_agent",
    instruction="Help users find companies, enrich contacts, and surface go-to-market insights using ZoomInfo",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        "https://mcp.zoominfo.com/mcp",
                    ]
                ),
                timeout=30,
            ),
        )
    ],
)