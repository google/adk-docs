from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

perseus_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="perseus",
            args=["mcp", "serve", "--workspace", "."],
        )
    )
)

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Use Perseus tools to read workspace context.",
    tools=[perseus_tools],
)