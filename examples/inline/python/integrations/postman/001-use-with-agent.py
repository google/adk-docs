from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="postman_agent",
    instruction="Help users manage their Postman workspaces and collections",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@postman/postman-mcp-server",
                        # "--full",  # Use all 100+ tools
                        # "--code",  # Use code generation tools
                        # "--region", "eu",  # Use EU region
                    ],
                    env={
                        "POSTMAN_API_KEY": POSTMAN_API_KEY,
                    },
                ),
                timeout=30,
            ),
        )
    ],
)