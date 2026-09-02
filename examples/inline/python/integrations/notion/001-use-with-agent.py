from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

NOTION_TOKEN = "YOUR_NOTION_TOKEN"

root_agent = Agent(
    model="gemini-flash-latest",
    name="notion_agent",
    instruction="Help users get information from Notion",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@notionhq/notion-mcp-server",
                    ],
                    env={
                        "NOTION_TOKEN": NOTION_TOKEN,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)