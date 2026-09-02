from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

ADSPIRER_ACCESS_TOKEN = "YOUR_ADSPIRER_ACCESS_TOKEN"

root_agent = Agent(
    model="gemini-flash-latest",
    name="advertising_agent",
    instruction=(
        "You are an advertising agent that helps users create, manage, "
        "and optimize ad campaigns across Google Ads, Meta Ads, "
        "LinkedIn Ads, and TikTok Ads."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.adspirer.com/mcp",
                headers={
                    "Authorization": f"Bearer {ADSPIRER_ACCESS_TOKEN}",
                },
            ),
        )
    ],
)