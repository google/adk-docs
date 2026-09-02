from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

MAILGUN_API_KEY = "YOUR_MAILGUN_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="mailgun_agent",
    instruction="Help users send emails and manage their Mailgun account",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@mailgun/mcp-server",
                    ],
                    env={
                        "MAILGUN_API_KEY": MAILGUN_API_KEY,
                        # "MAILGUN_API_REGION": "eu",  # Optional: defaults to "us"
                    }
                ),
                timeout=30,
            ),
        )
    ],
)