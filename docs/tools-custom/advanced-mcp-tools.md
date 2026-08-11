# Advanced MCP Configuration & Production Guide

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

This guide covers advanced integration patterns for the Model Context Protocol (MCP) in ADK. It provides production patterns for dynamic per-user authentication, human-in-the-loop approvals, long-running progress tracking, custom runtime execution, and enterprise cloud deployments.

---

## Developer Decision Matrix

Use the matrix below to select the right configuration mechanism for your production workload:

| Developer Requirement | Recommended Mechanism | Primary API / Parameter | Typical Scenario |
| :--- | :--- | :--- | :--- |
| **Inject per-user credentials or dynamic session tokens** | Dynamic Header Provider | `header_provider=...` | Multi-tenant apps, per-user JWTs/OAuth tokens |
| **Require approval before dangerous tool calls** | Tool Confirmation | `require_confirmation=...` | Database mutations, destructive shell/file ops |
| **Stream real-time progress for long operations** | Progress Callback & Factory | `progress_callback=...` | Heavy SQL queries, web scraping, data indexing |
| **Run agents in FastAPI / backend services without `adk web`** | Programmatic Runner Lifecycle | `Runner` + `await toolset.close()` | Custom microservices, CLI tools, worker queues |
| **Deploy containerized MCP agents to Cloud Run or GKE** | Stateless Streamable HTTP / Sidecar | `StreamableHTTPConnectionParams` | Horizontally scalable serverless or cluster pods |
| **Resolve tool naming collisions across servers** | Tool Namespacing & Filtering | `tool_name_prefix`, `tool_filter` | Aggregating multiple MCP servers (DB + GitHub) |
| **Handle server-requested sampling or auth challenges** | Bi-directional Protocol Callbacks | `sampling_callback`, `elicitation_callback` | Server-initiated LLM generation & auth prompts |
| **Inspect raw STDERR diagnostic streams** | Diagnostic Stream Logging | `errlog=sys.stderr` | Troubleshooting MCP subprocess crashes |

---

## 1. Dynamic Authentication & Per-User Headers (`header_provider`)

In multi-tenant or user-facing systems, hardcoding credentials into connection parameters is insecure. `McpToolset` supports `header_provider`, an asynchronous or synchronous callable that receives the active `ReadonlyContext` to dynamically construct authentication headers on every tool invocation.

=== "Python"

```python
from google.adk.agents import LlmAgent, ReadonlyContext
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

async def extract_per_user_headers(context: ReadonlyContext) -> dict[str, str]:
    """Dynamically extracts session state or per-user token on every turn."""
    user_token = context.state.get("user_access_token", "ANONYMOUS_TOKEN")
    return {
        "Authorization": f"Bearer {user_token}",
        "X-User-ID": context.user_id,
        "X-Session-ID": context.session_id,
    }

toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mcp-server.example.com/mcp",
        timeout=5,
        sse_read_timeout=300,
    ),
    header_provider=extract_per_user_headers,
)

root_agent = LlmAgent(
    model="gemini-flash-latest",
    name="enterprise_assistant",
    instruction="Execute authorized MCP tools on behalf of authenticated users.",
    tools=[toolset],
)
```

---

## 2. Human-in-the-Loop & Tool Confirmations (`require_confirmation`)

MCP servers can expose high-impact capabilities (e.g. database schema modifications or record deletions). You can enforce confirmation globally across all tools in the toolset or conditionally via a predicate function that inspects tool arguments.

=== "Python"

```python
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

def should_require_approval(args: dict[str, Any]) -> bool:
    """Require user approval for destructive SQL statements."""
    query = str(args.get("query", "")).lower()
    destructive_keywords = ["drop", "delete", "truncate", "alter", "update"]
    return any(keyword in query for keyword in destructive_keywords)

toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/db"],
        ),
        timeout=5,
    ),
    require_confirmation=should_require_approval,  # Can also be a boolean (True)
)

root_agent = LlmAgent(
    model="gemini-flash-latest",
    name="db_administrator",
    instruction="Execute database queries safely with explicit approval for mutations.",
    tools=[toolset],
)
```

---

## 3. Real-Time Progress Tracking (`progress_callback`)

Long-running MCP operations (such as scraping large websites or training jobs) send intermediate progress notifications over the `notifications/progress` channel.

### Option A: Global Callback Function
Assign a shared callback for simple logging or progress reporting:

```python
async def on_mcp_progress(progress: float, total: float | None, message: str | None) -> None:
    percentage = (progress / total * 100) if total else progress
    print(f"[MCP Progress] {percentage:.1f}% complete: {message or 'Working...'}")

toolset = McpToolset(
    connection_params=...,
    progress_callback=on_mcp_progress,
)
```

### Option B: Per-Tool Callback Factory (Session-Aware)
Use `ProgressCallbackFactory` to inject tool-specific callbacks with write access to `ToolContext.state`:

```python
from google.adk.tools.tool_context import ToolContext

def create_tool_progress_tracker(tool_name: str, callback_context: ToolContext, **kwargs):
    """Generates custom progress handlers and updates active agent session state."""
    async def progress_handler(progress: float, total: float | None, message: str | None):
        callback_context.state[f"{tool_name}_status"] = message
        callback_context.state[f"{tool_name}_progress"] = progress
    return progress_handler

toolset = McpToolset(
    connection_params=...,
    progress_callback=create_tool_progress_tracker,
)
```

---

## 4. Standalone Runner Execution (Outside `adk web`)

When embedding ADK agents into custom FastAPI applications, background workers, or standalone CLI scripts, instantiate `Runner` and manage lifecycle teardown explicitly via `await toolset.close()`.

```python
import asyncio
import os
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

async def run_standalone_mcp_agent():
    # 1. Define McpToolset and Agent synchronously
    toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", os.path.abspath("./data")],
            ),
            timeout=5,
        ),
        tool_filter=["list_directory", "read_file"],
    )

    agent = LlmAgent(
        model="gemini-flash-latest",
        name="filesystem_assistant",
        instruction="Assist users with file management.",
        tools=[toolset],
    )

    # 2. Setup Session and Runner
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="standalone_mcp_app",
        user_id="user_001",
    )

    runner = Runner(
        app_name="standalone_mcp_app",
        agent=agent,
        session_service=session_service,
    )

    try:
        # 3. Stream agent execution
        user_message = types.Content(
            role="user",
            parts=[types.Part(text="List the files available in the directory.")],
        )

        async for event in runner.run_async(
            session_id=session.id,
            user_id=session.user_id,
            new_message=user_message,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
    finally:
        # 4. Gracefully terminate subprocesses and network connections
        print("\nTerminating MCP connection...")
        await toolset.close()

if __name__ == "__main__":
    asyncio.run(run_standalone_mcp_agent())
```

---

## 5. Enterprise Cloud Deployment Architectures

### Architecture 1: Cloud Run Remote Service (Streamable HTTP)

Deploy MCP servers as independently scalable Cloud Run services and connect your ADK agent using `StreamableHTTPConnectionParams`.

=== "Python"

```python
# agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

root_agent = LlmAgent(
    model="gemini-flash-latest",
    name="cloud_run_agent",
    instruction="Execute cloud-hosted tools.",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("REMOTE_MCP_URL", "https://mcp-service-xyz.run.app/mcp"),
                headers={"Authorization": f"Bearer {os.getenv('MCP_AUTH_TOKEN')}"},
                timeout=5,
                sse_read_timeout=300,
            )
        )
    ],
)
```

Deploying to Cloud Run:
```bash
uv run adk deploy cloud_run \
  --project=<gcp-project-id> \
  --region=<gcp-region> \
  --service_name="mcp-agent-service" \
  ./path/to/agent_directory
```

---

### Architecture 2: GKE Sidecar Pattern

In Kubernetes/GKE environments, run the MCP server as a companion sidecar container in the same Pod for high-throughput, low-latency `localhost` communication.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent-with-mcp
spec:
  replicas: 3
  template:
    spec:
      containers:
      # Primary ADK Agent Container
      - name: adk-agent
        image: gcr.io/my-project/adk-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: MCP_SERVER_URL
          value: "http://127.0.0.1:8081/mcp"
      # MCP Server Sidecar
      - name: mcp-server
        image: gcr.io/my-project/mcp-server:latest
        ports:
        - containerPort: 8081
```

---

### Architecture 3: Agent Platform Runtime

Deploying to Agent Platform Runtime:

```bash
uv run adk deploy agent_engine \
  --project=<gcp-project-id> \
  --region=<gcp-region> \
  --display_name="Production MCP Agent" \
  ./path/to/agent_directory
```

---

## 6. Name Collisions & Tool Namespacing (`tool_name_prefix`)

When connecting to multiple MCP servers, tool names such as `query` or `search` can conflict. Use `tool_name_prefix` to automatically namespace discovered tools:

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

postgres_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/db"],
        )
    ),
    tool_name_prefix="pg_",  # Generates pg_query, pg_list_tables
)

github_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
        )
    ),
    tool_name_prefix="gh_",  # Generates gh_search_repositories, gh_create_issue
)
```

---

## 7. Bi-directional Protocol Hooks: Sampling & Elicitation

The Model Context Protocol supports bi-directional interaction where servers can request actions from clients:
- **Sampling (`sampling_callback`)**: Allows the MCP server to ask the ADK host to generate an LLM completion.
- **Elicitation (`elicitation_callback`)**: Allows the MCP server to request out-of-band user interactions or authentication flows.

```python
from mcp import SamplingCapability
from google.adk.tools.mcp_tool import McpToolset

async def handle_server_sampling(params):
    """Processes server-initiated LLM generation requests."""
    return {
        "role": "assistant",
        "content": {"type": "text", "text": "Generated response from ADK"},
    }

async def handle_server_elicitation(params):
    """Handles authentication or interactive challenges from the server."""
    print(f"Elicitation requested: {params}")
    return {"action": "approved"}

toolset = McpToolset(
    connection_params=...,
    sampling_callback=handle_server_sampling,
    sampling_capabilities=SamplingCapability(),
    elicitation_callback=handle_server_elicitation,
)
```

---

## 8. Diagnostic Logging & Error Streams (`errlog`)

By default, MCP subprocess errors are logged to standard error. You can redirect STDERR streams to an external file or diagnostic buffer for root-cause debugging:

```python
import sys
from google.adk.tools.mcp_tool import McpToolset

with open("mcp_server_errors.log", "a") as error_file:
    toolset = McpToolset(
        connection_params=...,
        errlog=error_file,  # Redirect subprocess STDERR to a log file
    )
```

---

## Next Steps

* Return to the [Model Context Protocol Overview](./mcp-tools.md) for basic setup, Resources, and Experimental UI Widgets.
* Explore [Custom Function Tools](./function-tools.md) for in-process Python tools.
* Read the [ADK Deployment Guide](../deploy/index.md) for full cloud configuration options.
