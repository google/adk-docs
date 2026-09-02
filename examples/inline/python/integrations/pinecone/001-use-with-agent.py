from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"

root_agent = Agent(
    model="gemini-flash-latest",
    name="pinecone_agent",
    instruction="Help users manage and search their Pinecone vector indexes",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@pinecone-database/mcp",
                    ],
                    env={
                        "PINECONE_API_KEY": PINECONE_API_KEY,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)