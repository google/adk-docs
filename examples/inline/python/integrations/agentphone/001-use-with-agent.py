from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="agentphone_agent",
    instruction="Help users make phone calls, send SMS, and manage phone numbers",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "agentphone-mcp",
                    ],
                    env={
                        "AGENTPHONE_API_KEY": AGENTPHONE_API_KEY,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)