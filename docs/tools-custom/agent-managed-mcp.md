# Manage MCP with Sub-Agents

You have already seen how to connect your agent to external resources using 
**Direct MCP Tool Integration** and how to serve your agent to outside clients 
via an **Agent-Exposed MCP Server**. However, as your ADK multi-agent 
capabilities grow, you may need a way to isolate complex, multi-step reasoning 
without overloading a single model's context window.

## Get started

```python
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Step 1: Initialize your MCP connection 
mcp_connection = StdioConnectionParams(
    server_params=StdioServerParameters(
        command='npx',
        args=['-y', '@modelcontextprotocol/server-postgres', 'postgres://user:pass@localhost:5432/db'],
    )
)

# Step 2: Create the child Sub-Agent and attach the McpToolset
database_sub_agent = LlmAgent(
    name="database_sub_agent",
    model="gemini-flash-latest",
    description="Delegates tasks to a database specialist...",
    instruction="You are a SQL expert...",
    tools=[McpToolset(connection_params=mcp_connection, tool_filter=['query_db', 'list_tables'])]
)
database_tool = AgentTool(agent=database_sub_agent)


# Step 4: Provide the AgentTool to your primary root agent
root_agent = LlmAgent(
    name="primary_orchestrator",
    model="gemini-pro-latest",
    instruction="You are the main assistant. You have access to specialized agents. Delegate data retrieval tasks to your database tool.",
    tools=[database_tool]
)
```

## Architectural role and tool adaptation
In the ADK framework, `AgentTool` wraps an `LlmAgent` to expose it as a native 
tool to a parent orchestrator. The child agent consumes tools via `McpToolset`, 
which connects to the underlying MCP server (via `list_tools`), converts the 
external MCP tool definitions into ADK-compatible `BaseTool` instances, and 
proxies all execution calls (`call_tool`) asynchronously.

## Tool scoping and cognitive filtering (`tool_filter`)
When assigning an `McpToolset` to a specialized sub-agent, you can restrict the 
exact tools made available to that agent using the `tool_filter` parameter:
* **Cognitive Focus:** Exposes only the specific actions relevant to the sub-agent's 
  mandate, such as, 'read_file', 'list_directory'.
* **Security and sandboxing:** Prevents unintended access to dangerous tools 
  exposed by the MCP server, isolating the execution surface from unpredictable 
  inputs.

## Connection Transport Modes
The sub-agent's `McpToolset` must be configured with one of two primary 
connection modes depending on deployment architecture:
* **Local Subprocess (`StdioConnectionParams`):** Spawns a local executable or 
  process, for example, via `npx` or `python`, communicating over standard input/output. 
  Best for self-contained single-container environments.
* **Remote Network (`StreamableHTTPConnectionParams` / `SseConnectionParams`):** 
  Connects over HTTP/SSE with headers, such as `X-Goog-Api-Key` or `Authorization`. 
  Best for scalable, multi-tenant, or independently managed MCP backends.

## Definition and lifecycle rules
* **Synchronous Instantiation for Production:** When deploying multi-agent 
  setups, Cloud Run, GKE, Agent Engine, both the sub-agent and its `McpToolset` 
  must be instantiated synchronously in `agent.py` rather than inside an async 
  factory function.
* **Session Persistence and restoration:** `McpToolset` supports serialization 
  via `getstate` and `setstate`. While session state is preserved across 
  lifecycle events, MCP socket/stdio connections are re-initialized dynamically 
  when the agent process restores.
* **Cleanup Management:** When running outside `adk web` in custom runtimes, 
  explicit teardown via `toolset.close()` or an exit stack ensures that 
  background server subprocesses and network connections are terminated cleanly.
