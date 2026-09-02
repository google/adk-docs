from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

PAYPAL_MCP_ENDPOINT = "https://mcp.sandbox.paypal.com/sse"  # Production: https://mcp.paypal.com/sse
PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"

root_agent = Agent(
    model="gemini-flash-latest",
    name="paypal_agent",
    instruction="Help users manage their PayPal account",
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=PAYPAL_MCP_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {PAYPAL_ACCESS_TOKEN}",
                },
            ),
        )
    ],
)