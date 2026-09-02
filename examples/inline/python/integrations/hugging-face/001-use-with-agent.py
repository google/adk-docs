from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

root_agent = Agent(
    model="gemini-flash-latest",
    name="hugging_face_agent",
    instruction="Help users get information from Hugging Face",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@llmindset/hf-mcp-server",
                    ],
                    env={
                        "HF_TOKEN": HUGGING_FACE_TOKEN,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)