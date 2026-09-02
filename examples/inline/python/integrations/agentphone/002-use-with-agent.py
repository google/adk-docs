from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="agentphone_agent",
    instruction="Help users make phone calls, send SMS, and manage phone numbers",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.agentphone.to/mcp",
                headers={
                    "Authorization": f"Bearer {AGENTPHONE_API_KEY}",
                },
            ),
        )
    ],
)