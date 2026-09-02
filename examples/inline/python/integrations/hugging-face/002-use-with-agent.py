from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

root_agent = Agent(
    model="gemini-flash-latest",
    name="hugging_face_agent",
    instruction="Help users get information from Hugging Face",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://huggingface.co/mcp",
                headers={
                    "Authorization": f"Bearer {HUGGING_FACE_TOKEN}",
                },
            ),
        )
    ],
)