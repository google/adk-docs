from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

PAYPAL_ENVIRONMENT = "SANDBOX"  # Options: "SANDBOX" or "PRODUCTION"
PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"

root_agent = Agent(
    model="gemini-flash-latest",
    name="paypal_agent",
    instruction="Help users manage their PayPal account",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@paypal/mcp",
                        "--tools=all",
                        # (Optional) Specify which tools to enable
                        # "--tools=subscriptionPlans.list,subscriptionPlans.show",
                    ],
                    env={
                        "PAYPAL_ACCESS_TOKEN": PAYPAL_ACCESS_TOKEN,
                        "PAYPAL_ENVIRONMENT": PAYPAL_ENVIRONMENT,
                    }
                ),
                timeout=300,
            ),
        )
    ],
)