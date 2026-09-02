from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

DEVELOPER_KNOWLEDGE_API_KEY = "YOUR_DEVELOPER_KNOWLEDGE_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="google_knowledge_agent",
    instruction="Search Google developer documentation for implementation guidance.",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://developerknowledge.googleapis.com/mcp",
                headers={"X-Goog-Api-Key": DEVELOPER_KNOWLEDGE_API_KEY},
            ),
        )
    ],
)