from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

QDRANT_URL = "http://localhost:6333"  # Or your Qdrant Cloud URL
COLLECTION_NAME = "my_collection"
# QDRANT_API_KEY = "YOUR_QDRANT_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="qdrant_agent",
    instruction="Help users store and retrieve information using semantic search",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["mcp-server-qdrant"],
                    env={
                        "QDRANT_URL": QDRANT_URL,
                        "COLLECTION_NAME": COLLECTION_NAME,
                        # "QDRANT_API_KEY": QDRANT_API_KEY,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)