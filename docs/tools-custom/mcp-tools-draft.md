# Model Context Protocol Tools

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

## What is Model Context Protocol (MCP)?

The **Model Context Protocol (MCP)** is an open standard for connecting Large Language Models (LLMs) to external data sources, tools, and systems. Think of it as a universal connection mechanism that simplifies how LLMs obtain context, execute actions, and interact with various systems.

---

## Core architecture and concepts

MCP follows a client-server architecture, defining how data (resources), interactive templates (prompts), and actionable functions (tools) are exposed by an MCP server and consumed by an MCP client (which could be an LLM host application or an AI agent).

```mermaid
sequenceDiagram
    autonumber
    participant Agent as ADK LlmAgent (Client)
    participant Toolset as McpToolset
    participant Server as MCP Server
    
    Agent->>Toolset: Initialize connection
    Toolset->>Server: Protocol Handshake & Tool Discovery (list_tools)
    Server-->>Toolset: Available Tool Schemas
    Toolset-->>Agent: Adapted ADK Tools
    
    Agent->>Toolset: Call Tool (arguments)
    Toolset->>Server: Execute Tool (call_tool via Stdio/HTTP)
    Server-->>Toolset: Execution Result (Text/JSON)
    Toolset-->>Agent: Result returned to LLM
```

## Prerequisites and setup rules

Before you begin, ensure you have the following set up:

### Checklist

- **ADK Installed**: Complete standard ADK setup in your project environment.
- **Runtime Requirements**: Python 3.9+ or Java 17+.
- **Node.js & `npx`** *(Python/TS only)*: Required to run npm-packaged community MCP servers.
- **Verify installations**: Confirm `adk` and `npx` are in your PATH in the activated virtual environment:

=== "MacOS / Linux"

    ```bash
    # Both commands should print the path to the executables.
    which adk
    which npx
    ```
    
=== "Windows PowerShell"

    ```powershell
    # Both commands should print the path to the executables.
    Get-Command adk
    Get-Command npx
    ```
    
!!! warning "Deployment rule"

    Agents deployed to production **must define `McpToolset` synchronously** in `agent.py`. Dynamic asynchronous agent initialization is only supported for local debugging or custom standalone runners.

---

## Key considerations

 When you start building with the Model Context Protocol (MCP) and ADK, these key architectural differences will help you design more stable and efficient agents:

| Concept | MCP (Model Context Protocol) | ADK (Agent Development Kit) |
| :--- | :--- | :--- |
| **Core Identity** | A protocol specification that defines communication rules. | A Python library and framework used to build and run agents. |
| **Tools** | Capabilities exposed by a server according to the protocol's schema. | Native Python objects (like `BaseTool`) built for direct use in the `LlmAgent`. |
| **Asynchronous Design** | Server handlers rely heavily on Python's `asyncio` library. | Tool implementations rely heavily on Python's `asyncio` library. |
| **State & Connections** | Establishes stateful, persistent connections between a client and server. | Manages the connection lifecycle using `McpToolset` and the `exit_stack` pattern. |
| **Session Persistence** | Active connections are not automatically re-established upon restoration. | Preserves agent context across managed environments via object serialization (`getstate` and `setstate`). |

!!! note "State restoration"

        While your agent preserves its session state during lifecycle events, it **does not** automatically re-establish active MCP connections upon restoration. It will re-initialize the connection as needed.

## Universal Setup Rules

  1. **Absolute Paths**: File system MCP servers require absolute path arguments: `os.path.abspath(...)`. Relative paths cause runtime resolution errors in subprocesses.
  2. **Package Discovery**: When running `adk web`, ensure an `__init__.py` file exists inside your agent folder so ADK can import the package.
  3. **Windows Async Bug**: If you encounter `_make_subprocess_transport NotImplementedError` on Windows, start `adk web` with the `--no-reload` flag.

## Understand uses and integrations

There's two main integration patterns:

  1. **Use existing MCP Servers within ADK**: When an ADK agent acts as an MCP client.
  1. **Expose ADK Tools via an MCP Server**: When you build an MCP servers that wraps ADK Tools to make them accessible to any MCP Client.

### Use existing MCP Servers within ADK

The `McpToolset` class can be directly added to your agent's tools list; this class enables seamless connection to an MCP server, discovery of its tools, and making them available for your agent to use. On initialization, `McpToolset` establishes and manages the connection to the MCP server. It also handles graceful connection shutdown when the agent or process terminates.
Use `McpToolset` to import tools from an external MCP server into your ADK `LlmAgent`.

### Example: Local Stdio Transport (FileSystem MCP)

This example sets up an ADK agent that connects to a local MCP file system server. It instantiates the McpToolset directly within the agent's tools list to enable file management capabilities.

**Step 1**. Define your agent with `McpToolset`:

=== "Python"

    ```python
    import os
    from google.adk.agents import LlmAgent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    TARGET_FOLDER = os.path.abspath("./accessible_files")

    root_agent = LlmAgent(
        model="gemini-flash-latest",
        name="filesystem_assistant",
        instruction="Help users manage local files.",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="npx",
                        args=["-y", "@modelcontextprotocol/server-filesystem", TARGET_FOLDER],
                    ),
                ),
                # Optional: Select specific tools exposed to the agent
                tool_filter=["list_directory", "read_file"],
            )
        ],
    )
    ```
    
    **Step 2**: Package and Run your Agent to make your agent discoverable to ADK and start interacting with it, follow this workflow:
    
      - Initiate your package: Create an `__init__.py` file in the same directory as your agent.py. This step is required for ADK to recognize your agent.
      - Launch the Web Interface:

     ```bash
      cd ./adk_agent_samples 
      adk web
    ```
    
    - Interact with the Agent: select `filesystem_assistant_agent` from the drop-down menu and prompt the Agent with commands: *List files in the current directory* or *What is the content of another_file.md?*

    ![Python Architecture](./assets/adk-tool-mcp-filesystem-adk-web-demo.png)

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";
    import path from "path";

    const TARGET_FOLDER = path.resolve("./accessible_files");

    export const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "filesystem_assistant",
        instruction: "Help users manage local files.",
        tools: [
            new MCPToolset({
                type: "StdioConnectionParams",
                serverParams: {
                    command: "npx",
                    args: ["-y", "@modelcontextprotocol/server-filesystem", TARGET_FOLDER],
                },
            }, ["list_directory", "read_file"]) // Optional tool filter array
        ],
    });
    ```

=== "Java"

    ```java
    package agents;

    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.mcp.McpToolset;
    import com.google.adk.tools.mcp.StdioServerParameters;
    import java.util.List;

    public class FileSystemAgentCreator {
        public static void main(String[] args) throws Exception {
            StdioServerParameters serverParams = StdioServerParameters.builder()
                    .command("npx")
                    .args(List.of("-y", "@modelcontextprotocol/server-filesystem", "/absolute/path/to/folder"))
                    .build();

            try (McpToolset toolset = new McpToolset(serverParams.toServerParameters())) {
                LlmAgent agent = LlmAgent.builder()
                        .model("gemini-flash-latest")
                        .name("filesystem_assistant")
                        .instruction("Help users access their file systems.")
                        .tools(toolset)
                        .build();
                
                System.out.println("Agent initialized: " + agent.name());
            }
        }
    }
    ```

---

### Example: Remote HTTP / SSE Transport (Google Maps Grounding Lite)

=== "Python"

```python
import os
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

root_agent = Agent(
    model="gemini-flash-latest",
    name="travel_planner",
    instruction="Plan travel routes and search locations using Google Maps.",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="[https://mapstools.googleapis.com/mcp](https://mapstools.googleapis.com/mcp)",
                headers={
                    "X-Goog-Api-Key": API_KEY,
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                },
                timeout=5,
                sse_read_timeout=300
            )
        )
    ],
)
```

=== "TypeScript"

```typescript

import { LlmAgent, MCPToolset } from "@google/adk";

export const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "travel_planner",
    instruction: "Plan travel routes and search locations using Google Maps.",
    tools: [
        new MCPToolset({
            type: "SseConnectionParams",
            url: "[https://mapstools.googleapis.com/mcp](https://mapstools.googleapis.com/mcp)",
            headers: {
                "X-Goog-Api-Key": process.env.GOOGLE_MAPS_API_KEY!,
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            timeout: 5,
            sseReadTimeout: 300
        }),
    ],
});
```





### Production timeout configuration

To prevent hanging connections, socket leaks, or process starvation, configure explicit timeouts in production:

| Parameter | Applies To | Description |
| :--- | :--- | :--- |
| `timeout` | All Transports | Maximum seconds to wait for connection setup or RPC request calls. |
| `sse_read_timeout` | `SseConnectionParams`, `StreamableHTTPConnectionParams` | Maximum seconds to wait for streaming event data from the server. |

---



---

## Pattern 2: Exposing ADK Tools via a Custom MCP Server

Wrap existing ADK tools (`FunctionTool`) inside an MCP server to make them accessible to external clients, such as Claude Desktop or custom hosts.

    ```python
    import asyncio
    import json
    from mcp import types as mcp_types
    from mcp.server.lowlevel import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio

    from google.adk.tools.function_tool import FunctionTool
    from google.adk.tools.load_web_page import load_web_page
    from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

    # 1. Instantiate the ADK Tool
    adk_tool = FunctionTool(load_web_page)

    # 2. Create the MCP Server
    app = Server("adk-web-loader-server")

    @app.list_tools()
    async def list_mcp_tools() -> list[mcp_types.Tool]:
        """Expose converted ADK tool schema to MCP clients."""
        return [adk_to_mcp_tool_type(adk_tool)]

    @app.call_tool()
    async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
        """Execute the ADK tool when called by an MCP client."""
        if name == adk_tool.name:
            try:
                result = await adk_tool.run_async(args=arguments, tool_context=None)
                return [mcp_types.TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as err:
                return [mcp_types.TextContent(type="text", text=json.dumps({"error": str(err)}))]
        raise ValueError(f"Unknown tool: {name}")

    # 3. Run Server over Stdio
    async def main():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=app.name,
                    server_version="0.1.0",
                    capabilities=app.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    if __name__ == "__main__":
        asyncio.run(main())
    ```
---

## Deployment Comparison Matrix

| Strategy | Architecture | Ideal Use Case | Pros / Cons |
| :--- | :--- | :--- | :--- |
| **Self-Contained Stdio** | Single container runs ADK agent + Node.js/Python MCP subprocess | Lightweight apps, single-tenant tasks | **Pros:** Zero network latency, simple deployment.<br>**Cons:** Higher container memory consumption. |
| **Streamable HTTP Service** | ADK agent connects to separate Cloud Run HTTP service | High-scale, multi-tenant production systems | **Pros:** Independent auto-scaling, stateless.<br>**Cons:** Requires network authentication setup. |
| **GKE Sidecar** | MCP server runs as a sidecar container in the same Kubernetes Pod | Microservice clusters, local cluster IPC | **Pros:** Fast `localhost` IPC, isolated dependencies.<br>**Cons:** Pod-level resource allocation. |

---

### Deployment CLI Commands

```bash
# Deploy to Agent Runtime
uv run adk deploy agent_engine \
  --project=<gcp-project-id> \
  --region=<gcp-region> \
  --staging_bucket="gs://<gcs-bucket>" \
  --display_name="MCP Agent" \
  ./path/to/agent_directory

# Deploy to Cloud Run
uv run adk deploy cloud_run \
  --project=<gcp-project-id> \
  --region=<gcp-region> \
  --service_name=<service-name> \
  ./path/to/agent_directory
```

---

## Remote MCP Authentication and resource access

This section shows you how to connect to remote MCP servers using authentication and how to read data **Resources** exposed by an MCP server. When an MCP server requires authentication, such as over Server-Sent Events `SseConnectionParams` or Streamable HTTP, `McpToolset` handles credential injection and token management automatically.

### Key authentication parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `auth_scheme` | `AuthScheme` | The authentication strategy (e.g., `Bearer`, `Basic`, `APIKey`, `OAuth2`). |
| `auth_credential` | `AuthCredential` | The secret credential payload, for example, API token, OAuth access token, username/password. |

ADK automatically constructs the required `Authorization` HTTP headers and manages OAuth 2.0 token refreshes during client requests.

### Configurate authentication

When an MCP server requires authentication, `McpToolset` handles credential injection and token management automatically. Use the native `auth_scheme` and `auth_credential` parameters rather than manually injecting HTTP headers.

*For general ADK authentication patterns, see our [Custom Tools Authentication Guide](./authentication.md)*

=== "Python"

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.auth import AuthScheme, AuthCredential

# Configure Bearer Token / OAuth Authentication
toolset = McpToolset(
    connection_params=SseConnectionParams(
        url="[https://mcp-server.example.com/sse](https://mcp-server.example.com/sse)",
        timeout=5
    ),
    auth_scheme=AuthScheme.BEARER,
    auth_credential=AuthCredential(token="YOUR_ACCESS_TOKEN"),
)
```

=== "TypeScript"

```typescript
    import { MCPToolset } from "@google/adk";

    // Configure Bearer Token Authentication
    const toolset = new MCPToolset({
        type: "SseConnectionParams",
        url: "https://mcp-server.example.com/sse",
        headers: {
            "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        },
    });
```

---

## Accessing MCP Resources

In addition to executable **Tools**, MCP servers can expose **Resources**\E2\80\94read-only data files, database records, or API context blobs.

`McpToolset` provides two core methods to discover and read these data resources:

### Core Methods

* **`list_resources()`**: Returns a list of all available data resources exposed by the MCP server.
* **`read_resource(name)`**: Retrieves the raw content blocks, text or binary data, for a specific resource by its name or URI.

### Try it out

=== "Python"

  ```python
    import asyncio

    async def fetch_mcp_data(toolset):
        # 1. Discover available resources on the server
        resources = await toolset.list_resources()
        print("Available Resources:", resources)

        # 2. Read content from a specific resource
        if resources:
            resource_name = resources[0].name
            content_blocks = await toolset.read_resource(name=resource_name)
            print(f"Content of {resource_name}:", content_blocks)
  ```

=== "TypeScript"

  ```typescript
    async function fetchMcpData(toolset: any) {
        // 1. Discover available resources
        const resources = await toolset.listResources();
        console.log("Available Resources:", resources);

        // 2. Read a specific resource
        if (resources.length > 0) {
            const content = await toolset.readResource(resources[0].name);
            console.log(`Content of ${resources[0].name}:`, content);
        }
    }
  ```

---

## Troubleshooting & Best Practices Checklist

* **Security & Scoping**: Always supply `tool_filter=[...]` in `McpToolset` to expose only necessary actions to your LLM.
* **Timeouts**: Configure explicit timeouts on `StdioConnectionParams(timeout=5)` to prevent hanging subprocesses.
* **Lifecycle Cleanup**: In non-`adk web` runners, invoke `await toolset.close()` or use async context managers to gracefully shutdown subprocesses.
* **Environment Detection**: Dynamically pick connection types based on environment variables (for example, `K_SERVICE` for Cloud Run vs Stdio for local dev.

### Configure the environment-aware connection

```python
import os
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams, StdioConnectionParams
from google.adk.auth import AuthScheme, AuthCredential
from mcp import StdioServerParameters

if os.getenv("K_SERVICE"):
    # Running in Production (Cloud Run)
    # Uses Streamable HTTP for stateless scalability and native ADK Auth
    mcp_toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=os.getenv("REMOTE_MCP_URL"),
            timeout=5,
            sse_read_timeout=300
        ),
        auth_scheme=AuthScheme.BEARER,
        auth_credential=AuthCredential(token=os.getenv("MCP_AUTH_TOKEN"))
    )
else:
    # Running in Local Development
    # Uses Stdio Subprocess IPC for zero-network latency testing
    mcp_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
            ),
            timeout=5
        )
    )
```

## Experimental UI Rendering (`meta.ui.resourceUri`)

Standard MCP tools return plain text or JSON output. **Experimental UI Rendering** enables MCP tools to return rich, interactive visual widgets, such as maps, charts, or forms, directly inside the chat interface.

```mermaid
sequenceDiagram
    autonumber
    participant Tool as MCP Server Tool
    participant ADK as ADK Framework
    participant UI as Client UI (adk web / Frontend)

    Tool-->>ADK: Returns result + metadata (meta.ui.resourceUri = "ui://widgets/map")
    ADK->>ADK: Detects meta.ui.resourceUri annotation
    ADK-->>UI: Emits Event with UI rendering signal & Resource URI
    UI->>Tool: Fetches UI bundle from Resource URI
    UI-->>UI: Renders interactive widget in chat interface
```

### How It Works
1. **Metadata Link**: An MCP tool attaches a UI resource link in its output metadata: `meta.ui.resourceUri = "ui://widgets/card"`.
2. **ADK Detection**: ADK detects `meta.ui.resourceUri` when processing tool execution results.
3. **Client Display**: ADK signals the web UI, `adk web` or custom frontend, to fetch the UI resource and render an interactive widget instead of plain text.

```python
    # MCP Server tool returning a UI metadata link
    @app.call_tool()
    async def get_weather(city: str):
        return {
            "content": [{"type": "text", "text": f"Weather in {city}: 72°F Sunny"}],
            "_meta": {
                "ui": {
                    "resourceUri": "ui://widgets/weather-card"
                }
            }
        }
    ```
