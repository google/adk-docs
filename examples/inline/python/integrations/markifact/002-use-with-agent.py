from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

MARKIFACT_ACCESS_TOKEN = "YOUR_MARKIFACT_ACCESS_TOKEN"

root_agent = Agent(
    model="gemini-flash-latest",
    name="marketing_agent",
    instruction=(
        "You are a performance marketing agent that helps users manage "
        "ad campaigns, run analytics, sync e-commerce data, and "
        "execute marketing workflows across Google Ads, Meta Ads, GA4, "
        "TikTok Ads, LinkedIn Ads, Shopify, HubSpot, and more. "
        "Always confirm with the user before any write operation."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://api.markifact.com/mcp",
                headers={
                    "Authorization": f"Bearer {MARKIFACT_ACCESS_TOKEN}",
                },
            ),
        )
    ],
)