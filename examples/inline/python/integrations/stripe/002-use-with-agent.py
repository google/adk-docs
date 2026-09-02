from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="stripe_agent",
    instruction="Help users manage their Stripe account",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.stripe.com",
                headers={
                    "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
                },
            ),
        )
    ],
)