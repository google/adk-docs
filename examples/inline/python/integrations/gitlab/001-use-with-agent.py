from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Replace with your instance URL if self-hosted (e.g., "gitlab.example.com")
GITLAB_INSTANCE_URL = "gitlab.com"

root_agent = Agent(
    model="gemini-flash-latest",
    name="gitlab_agent",
    instruction="Help users get information from GitLab",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        f"https://{GITLAB_INSTANCE_URL}/api/v4/mcp",
                        "--static-oauth-client-metadata",
                        "{\"scope\": \"mcp\"}",
                    ],
                ),
                timeout=30,
            ),
        )
    ],
)