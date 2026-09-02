from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

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
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        "https://mcp.adspirer.com/mcp",
                    ],
                ),
                timeout=30,
            ),
        )
    ],
)