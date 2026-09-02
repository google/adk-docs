from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

N8N_INSTANCE_URL = "https://localhost:5678"
N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN"

root_agent = Agent(
    model="gemini-flash-latest",
    name="n8n_agent",
    instruction="Help users manage and execute workflows in n8n",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "supergateway",
                        "--streamableHttp",
                        f"{N8N_INSTANCE_URL}/mcp-server/http",
                        "--header",
                        f"authorization:Bearer {N8N_MCP_TOKEN}"
                    ]
                ),
                timeout=300,
            ),
        )
    ],
)