from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

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
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        "https://api.markifact.com/mcp",
                    ],
                ),
                timeout=30,
            ),
        )
    ],
)