from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="postman_agent",
    instruction="Help users manage their Postman workspaces and collections",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.postman.com/mcp",
                # (Optional) Use "/minimal" for essential tools only
                # (Optional) Use "/code" for code generation tools
                # (Optional) Use "https://mcp.eu.postman.com" for EU region
                headers={
                    "Authorization": f"Bearer {POSTMAN_API_KEY}",
                },
            ),
        )
    ],
)