from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="stripe_agent",
    instruction="Help users manage their Stripe account",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@stripe/mcp",
                        "--tools=all",
                        # (Optional) Specify which tools to enable
                        # "--tools=customers.read,invoices.read,products.read",
                    ],
                    env={
                        "STRIPE_SECRET_KEY": STRIPE_SECRET_KEY,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)