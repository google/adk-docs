from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

CARTESIA_API_KEY = "YOUR_CARTESIA_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="cartesia_agent",
    instruction="Help users generate speech and work with audio content",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["cartesia-mcp"],
                    env={
                        "CARTESIA_API_KEY": CARTESIA_API_KEY,
                        # "OUTPUT_DIRECTORY": "/path/to/output",  # Optional
                    }
                ),
                timeout=30,
            ),
        )
    ],
)