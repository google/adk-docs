from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from temporalio.client import Client
from temporalio.contrib.google_adk_agents import (
    GoogleAdkPlugin,
    TemporalModel,
    TemporalMcpToolSet,
    TemporalMcpToolSetProvider,
)

# Define a shared factory for your MCP toolset.
# Both the worker (TemporalMcpToolSetProvider) and agent (TemporalMcpToolSet) use it.
def toolset_factory(_):
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
            ),
        ),
    )

# The provider tells the worker how to instantiate the toolset.
toolset_provider = TemporalMcpToolSetProvider("my-tools", toolset_factory)

# Configure the client with the toolset provider
async def main():
    client = await Client.connect(
        "localhost:7233",
        plugins=[GoogleAdkPlugin(toolset_providers=[toolset_provider])]
    )
    # ... start a worker or execute a workflow with this client

# Reference the toolset by name when you declare your Agent (inside a @workflow.run).
# not_in_workflow_toolset lets this agent also run locally with `adk web`.
agent = Agent(
    name="tool_agent",
    model=TemporalModel("gemini-flash-latest"),
    tools=[TemporalMcpToolSet("my-tools", not_in_workflow_toolset=toolset_factory)],
)