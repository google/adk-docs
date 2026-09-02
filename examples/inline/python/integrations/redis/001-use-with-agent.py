from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

root_agent = Agent(
    model="gemini-flash-latest",
    name="redis_mcp_agent",
    instruction="Use the search-records tool to answer questions.",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="rvl",
                    args=[
                        "mcp",
                        "--config",
                        "/path/to/mcp_config.yaml",
                        "--read-only",
                    ],
                ),
                timeout=30,
            ),
            tool_filter=["search-records"],
        ),
    ],
)