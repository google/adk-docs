from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# For local storage, use:
DATA_DIR = "/path/to/your/data/directory"

# For Chroma Cloud, use:
# CHROMA_TENANT = "your-tenant-id"
# CHROMA_DATABASE = "your-database-name"
# CHROMA_API_KEY = "your-api-key"

root_agent = Agent(
    model="gemini-flash-latest",
    name="chroma_agent",
    instruction="Help users store and retrieve information using semantic search",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=[
                        "chroma-mcp",
                        # For local storage, use:
                        "--client-type",
                        "persistent",
                        "--data-dir",
                        DATA_DIR,
                        # For Chroma Cloud, use:
                        # "--client-type",
                        # "cloud",
                        # "--tenant",
                        # CHROMA_TENANT,
                        # "--database",
                        # CHROMA_DATABASE,
                        # "--api-key",
                        # CHROMA_API_KEY,
                    ],
                ),
                timeout=30,
            ),
        )
    ],
)