from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

GRAFANA_URL = "https://<your-stack>.grafana.net"

root_agent = Agent(
    model="gemini-flash-latest",
    name="observability_agent",
    instruction="Help users investigate issues using Grafana Cloud observability data",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.grafana.com/mcp",
                headers={
                    "X-Grafana-URL": GRAFANA_URL,
                },
            ),
        )
    ],
)