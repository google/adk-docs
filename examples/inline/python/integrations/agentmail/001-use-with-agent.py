from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

AGENTMAIL_API_KEY = "YOUR_AGENTMAIL_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="agentmail_agent",
    instruction="Help users manage email inboxes and send messages",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "agentmail-mcp",
                    ],
                    env={
                        "AGENTMAIL_API_KEY": AGENTMAIL_API_KEY,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)