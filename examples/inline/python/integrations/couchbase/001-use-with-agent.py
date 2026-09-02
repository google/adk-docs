from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

CB_CONNECTION_STRING = "couchbase://localhost"
CB_USERNAME = "Administrator"
CB_PASSWORD = "password"

root_agent = Agent(
    model="gemini-flash-latest",
    name="couchbase_agent",
    instruction="Help users explore and query Couchbase databases",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["couchbase-mcp-server"],
                    env={
                        "CB_CONNECTION_STRING": CB_CONNECTION_STRING,
                        "CB_USERNAME": CB_USERNAME,
                        "CB_PASSWORD": CB_PASSWORD,
                        "CB_MCP_READ_ONLY_MODE": "true",  # Prevents write operations
                    },
                ),
                timeout=60,
            ),
        )
    ],
)