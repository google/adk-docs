from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)

E2A_API_KEY = "YOUR_E2A_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="e2a_agent",
    instruction=(
        "You manage email through the e2a tools. Call whoami once to "
        "learn your identity and inbox address. Use list_messages and "
        "get_message to read; use reply_to_message when replying to an "
        "existing thread (it preserves In-Reply-To and References), and "
        "send_message only to start a new thread. Both 'accepted' and "
        "'pending_review' are successful outcomes — never re-send after "
        "either one."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://api.e2a.dev/mcp",
                headers={"Authorization": f"Bearer {E2A_API_KEY}"},
                timeout=30,
            ),
        )
    ],
)