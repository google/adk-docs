# Model Context Protocol Tools

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.3.10</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

The **Model Context Protocol (MCP)** is an open standard for connecting generative AI models to external data sources, tools, and systems. Think of it as a universal connection mechanism that simplifies how LLMs obtain context, execute actions, and interact with various systems.

---

## Core architecture and concepts

MCP follows a client-server architecture, defining how data or resources, interactive templates or prompts, and actionable functions or tools are exposed by an MCP server and consumed by an MCP client, which could be an LLM host application or an AI agent. In ADK, you use the McpToolset class as an interface between MCP Servers and ADK agents. It is also possible to configure an ADK server as an MCP server for use by other client systems.

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

- **ADK Installed**: Complete standard ADK setup in your project environment.
- **Runtime Requirements**: Python 3.10+ or Java 17+.
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

## MCP Implementation options

 When you start building with the Model Context Protocol (MCP) and ADK, these key architectural differences will help you design more stable and efficient agents. The following table works as a comparative guide to help you construct those agents.

| Dimension | **Direct MCP Tool Integration** (`McpToolset`) | **Specialized Sub-Agent Delegation** (`AgentTool`) | **Agent-Exposed MCP Server** (`to_mcp_server`) |
| :--- | :--- | :--- | :--- |
| **Architecture** | External server process or remote service providing deterministic endpoints adapted into the primary `LlmAgent` tool list. | In-process, hierarchical agent encapsulation where a parent agent invokes a child `LlmAgent` as a callable tool. | An autonomous ADK agent compiled into an MCP server, callable by external clients (Claude Code, IDEs, external hosts). |
| **Context Window Impact** | **High Context Bloat**: Every tool definition and raw output, for example: database rows or file blobs, enters the primary agent's history. | **Zero Context Bloat**: Intermediate exploratory reasoning, failed tool calls, and large raw outputs remain isolated in the sub-agent loop. | **Isolated**: The external caller only receives the final aggregated response text/blocks. |
| **AI Model Load and Tiering** | Single model must understand all tool schemas, validation constraints, and workflow state simultaneously. | Enables **model tiering**, for example: `gemini-2.5-pro` for orchestrator, and `gemini-2.5-flash` for sub-agent tool execution with dedicated system instructions. | Independent model reasoning dedicated solely to the wrapped task. |
| **Latency & Token Cost** | **Lower Cost & Predictable Latency**: 1 LLM turn + 1 deterministic tool invocation + 1 response generation turn. | **Higher Cost & Variable Latency**: Multiple LLM calls, sub-agent reasoning turns before returning to parent. | Client-driven; latency depends on internal agent execution depth. |
| **Ideal Use Cases** | <ul><li>Deterministic API integrations: Postgres, BigQuery, GitHub, Google Maps.</li><li>File system operations & static resource reading.</li><li>Reusing standard pre-built community MCP servers.</li></ul> | <ul><li>Multi-step autonomous workflows requiring trial-and-error. For example: code debugging or research synthesis.</li><li>Tasks needing isolated personas or specialized instructions.</li><li>Scenarios with >20 tools where schema overload harms accuracy.</li></ul> | <ul><li>Exposing complex ADK multi-agent capabilities to external MCP-compliant ecosystems.</li><li>Integrating ADK agents into IDEs, editors, or A2A pipelines.</li></ul> |

!!! note "State restoration"

    While ADK agents preserve session state during lifecycle events, they do not automatically re-establish active MCP connections upon restoration. Agents re-initialize connections as needed.

## Universal Setup Rules

  1. **Absolute Paths**: File system MCP servers require absolute path arguments: `os.path.abspath(...)`. Relative paths cause runtime resolution errors in subprocesses.
  2. **Package Discovery**: When running `adk web`, ensure an `__init__.py` file exists inside your agent folder so ADK can import the package.

### Understand uses and integrations

There are two main integration patterns:

  1. **Use existing MCP Servers within ADK**: When an ADK agent acts as an MCP client.
  1. **Expose ADK Tools via an MCP Server**: When you build an MCP server that wraps ADK Tools to make them accessible to any MCP Client.

## Use existing MCP Servers within ADK

The `McpToolset` class can be directly added to your agent's tools list; this class enables seamless connection to an MCP server, discovery of its tools, and making them available for your agent to use. On initialization, `McpToolset` establishes and manages the connection to the MCP server. It also handles graceful connection shutdown when the agent or process terminates.
Use `McpToolset` to import tools from an external MCP server into your ADK `LlmAgent`.

### Example: Local Stdio Transport (FileSystem MCP)

This example sets up an ADK agent that connects to a local MCP file system server; it instantiates the McpToolset directly within the agent's tools list to enable file management capabilities.

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
    
    - Interact with the Agent: select `filesystem_assistant` from the drop-down menu and prompt the Agent with commands: *List files in the current directory* or *What is the content of another_file.md?*

    ![MCP with ADK Web - FileSystem Example](../assets/adk-tool-mcp-filesystem-adk-web-demo.png)

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

Before starting, follow the instructions for [Google Maps Grounding Lite](https://developers.google.com/maps/ai/grounding-lite) to enable the service on your Google Cloud project and generate your Maps Platform API Key.
Unlike the previous local process example, this pattern connects your agent to a remote, cloud-hosted MCP server using Server-Sent Events (SSE). It uses the Google Maps Grounding Lite service to demonstrate how to pass authentication headers, such as an API key, to a scalable endpoint.

**Step 1**: Define your agent with `McpToolset`.

=== "Python"

    ```python
    import os
    from google.adk.agents import LlmAgent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
    
    API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    
    root_agent = LlmAgent(
        model="gemini-flash-latest",
        name="travel_planner",
        instruction="Plan travel routes and search locations using Google Maps.",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://mapstools.googleapis.com/mcp",
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
    **Step 2**: Set environment variable before running `adk web`, set you Google API key in your terminal
      
      ```bash
      export GOOGLE_MAPS_API_KEY="YOUR_ACTUAL_GOOGLE_MAPS_API_KEY"
      ```
      
     **Step 3**: Run `adk web`: Navigate to the parent directory of `mcp_agent` and launch the web Interface.
     **Step 4**: Interact with the UI:
       - Select `travel_planner` from the drop-down.
       - Try prompts such as: *I will be in San Francisco tomorrow. What's the weather like* or *Find coffee shops near Golden Gate Park*
       
     ![MCP with ADK Web - Google Maps Example](../assets/adk-tool-maps-lite-mcp-adk-web-demo.png)

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
                url: "https://mapstools.googleapis.com/mcp",
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
    
---

## Expose ADK Tools with MCP Server

You can make ADK capabilities accessible to external MCP clients, such as Claude Desktop, IDEs, or custom hosts, in two ways:

1. **Expose an entire Agent (`to_mcp_server`)**: One-line conversion that exposes full multi-turn agent reasoning and internal tool execution to external MCP clients.
2. **Expose individual Tools (`FunctionTool`)**: Manually build a lightweight MCP server that wraps specific standalone ADK tools.

---

### Expose an entire ADK Agent (`to_mcp_server`)
Use ADK's native `to_mcp_server()` utility to wrap an existing `LlmAgent` into a standard FastMCP server:

```python
from google.adk.agents import LlmAgent
from google.adk.tools.load_web_page import load_web_page
from google.adk.tools.mcp_tool import to_mcp_server
# Define your ADK agent
agent = LlmAgent(
    model="gemini-flash-latest",
    name="web_reader_agent",
    instruction="Fetch and summarize web content for the user.",
    tools=[load_web_page],
)
# Convert the agent into an MCP server
app = to_mcp_server(agent)
if __name__ == "__main__":
    # Runs the agent as a standard stdio MCP server
    app.run()
```

---

### Expose individual Tools

If you only want to expose individual ADK tools without the full agent reasoning loop, wrap FunctionTool inside an MCP Server:

#### Prerequisites

Install the MCP Server library in the same environment as your ADK installation:

     ```bash
     pip install mcp
     ```
     
### Build the MCP server with ADK tools

1. Create a new Python file for your MCP server, for example: `my_adk_mcp_server.py`.
2. Implement server logic with the following code to your new file. This following script sets up an MCP server that exposes the ADK `load_web_page` tool.

```python
import asyncio
import json
import os
from dotenv import load_dotenv

from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio 

from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.load_web_page import load_web_page 
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

# Load environment variables (e.g., API keys required by ADK tools)
load_dotenv() 

adk_tool_to_expose = FunctionTool(load_web_page)
app = Server("adk-tool-exposing-mcp-server")

@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """List tools exposed by this server."""
    mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_to_expose)
    return [mcp_tool_schema]

@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    """Execute a tool call requested by an MCP client."""
    if name == adk_tool_to_expose.name:
        try:
            # Note: tool_context is None because the ADK tool runs outside a full ADK Runner.
            # Tools requiring ToolContext features (like state or auth) need custom handling here.
            adk_tool_response = await adk_tool_to_expose.run_async(
                args=arguments,
                tool_context=None,
            )

            # Serialize the ADK tool's response into MCP's expected Content format
            response_text = json.dumps(adk_tool_response, indent=2)
            return [mcp_types.TextContent(type="text", text=response_text)]

        except Exception as e:
            error_text = json.dumps({"error": f"Failed to execute tool '{name}': {str(e)}"})
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        error_text = json.dumps({"error": f"Tool '{name}' not implemented by this server."})
        return [mcp_types.TextContent(type="text", text=error_text)]

async def run_mcp_stdio_server():
    """Run the MCP server over standard input/output."""
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
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        print("\nMCP Server (stdio) stopped by user.")
```

#### Test your custom MCP server with an ADK Agent

To test your custom server, you need to build an ADK agent that acts as a client. This agent uses the `McpToolset` to establish a connection to the server script you just created.

1. Set up your agent in a new directory such as `./adk_agent_samples/mcp_client_agent/`. Create an `agent.py` file and include an `__init__.py` alongside it to make it discoverable.

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# IMPORTANT: Provide the absolute path to the server script you built previously
MCP_SERVER_SCRIPT = "/path/to/your/my_adk_mcp_server.py"

root_agent = LlmAgent(
    model='gemini-flash-latest',
    name='web_reader_mcp_client_agent',
    instruction="Use the 'load_web_page' tool to fetch content from a URL provided by the user.",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='python3', 
                    args=[MCP_SERVER_SCRIPT], 
                )
            )
        )
    ],
)
```

2. Navigate to your agent's parent directory in the terminal:

```bash
cd ./adk_agent_samples
adk web
```

3. Open the ADK Web UI and select the web_reader_mcp_client_agent.
4. Test the connection with a prompt such as: *Load the content from "https://example.com"*.

---

## Remote MCP Authentication and resource access

This section shows you how to connect to remote MCP servers using authentication and how to read data **Resources** exposed by an MCP server. When an MCP server requires authentication, such as over Server-Sent Events `SseConnectionParams` or Streamable HTTP, `McpToolset` handles credential injection and token management automatically.

### Key authentication parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `auth_scheme` | `AuthScheme` | The authentication strategy (e.g., `Bearer`, `Basic`, `APIKey`, `OAuth2`). |
| `auth_credential` | `AuthCredential` | The secret credential payload, for example, API token, OAuth access token, username/password. |

ADK automatically constructs the required `Authorization` HTTP headers and manages OAuth 2.0 token refreshes during client requests.

### Configure authentication

When an MCP server requires authentication, `McpToolset` handles credential injection and token management automatically. Use the native `auth_scheme` and `auth_credential` parameters rather than manually injecting HTTP headers.

*For general ADK authentication patterns, see our [Custom Tools Authentication Guide](./authentication.md)*

=== "Python"

```python
import os
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# Configure Bearer Token Authentication via headers
toolset = McpToolset(
    connection_params=SseConnectionParams(
        url="https://mcp-server.example.com/sse",
        headers={"Authorization": f"Bearer {os.getenv('MCP_AUTH_TOKEN')}"},
        timeout=5,
    )
)
```

=== "TypeScript"

```typescript
import { MCPToolset } from "@google/adk";

// Configure Bearer Token Authentication via headers
const toolset = new MCPToolset({
    type: "SseConnectionParams",
    url: "https://mcp-server.example.com/sse",
    headers: {
        "Authorization": `Bearer ${process.env.MCP_AUTH_TOKEN}`,
    },
    timeout: 5,
});
```

---

## Accessing MCP Resources

In addition to executable **Tools**, MCP servers can expose **Resources** data files, database records, or API context blobs.

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
            resource_name = resources[0]
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
            const content = await toolset.readResource(resources[0]);
            console.log(`Content of ${resources[0]}:`, content);
        }
    }
  ```

---

## Troubleshooting & Best Practices Checklist

* **Security & Scoping**: Always supply `tool_filter=[...]` in `McpToolset` to expose only necessary actions to your LLM.
* **Timeouts**: Configure explicit timeouts on `StdioConnectionParams(timeout=5)` to prevent hanging subprocesses.
* **Lifecycle Cleanup**: In non-`adk web` runners, invoke `await toolset.close()` or use async context managers to gracefully shutdown subprocesses.
* **Environment Detection**: Dynamically pick connection types based on environment variables, for example: `K_SERVICE` for Cloud Run vs Stdio for local dev.

### Configure the environment-aware connection

```python
import os
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters

if os.getenv("K_SERVICE"):
  # Running in Production (Cloud Run)
  # Uses Streamable HTTP for stateless scalability and bearer auth headers
  mcp_toolset = McpToolset(
      connection_params=StreamableHTTPConnectionParams(
          url=os.getenv("REMOTE_MCP_URL"),
          headers={"Authorization": f"Bearer {os.getenv('MCP_AUTH_TOKEN')}"},
          timeout=5,
          sse_read_timeout=300,
      )
  )
else:
  # Running in Local Development
  # Uses Stdio Subprocess IPC for zero-network latency testing
  mcp_toolset = McpToolset(
      connection_params=StdioConnectionParams(
          server_params=StdioServerParameters(
              command="npx",
              args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
          ),
          timeout=5,
      )
  )

```

## UI Rendering 

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

1. **Tool Registration**: The MCP tool declares a UI resource link in its schema definition metadata during `tools/list`: `_meta.ui.resourceUri = "ui://widgets/weather-card"`.
2. **ADK Detection**: ADK reads the schema definition to detect `_meta.ui.resourceUri` and knows this tool supports an interactive UI.
3. **Client Display**: Upon tool execution, ADK signals the web UI (`adk web` or custom frontend) to fetch the UI resource and render an interactive widget instead of plain text.

```python
from mcp import types as mcp_types
from mcp.server.lowlevel import Server

app = Server("weather-mcp-server")


@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
  """Declares the tool and attaches UI rendering metadata."""
  return [
      mcp_types.Tool(
          name="get_weather",
          description="Get weather forecast for a city.",
          inputSchema={
              "type": "object",
              "properties": {"city": {"type": "string"}},
              "required": ["city"],
          },
          meta={"ui": {"resourceUri": "ui://widgets/weather-card"}},
      )
  ]


@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
  """Executes the tool and returns standard text/data content."""
  if name == "get_weather":
    city = arguments.get("city", "Unknown")
    return [
        mcp_types.TextContent(
            type="text", text=f"Weather in {city}: 72°F Sunny"
        )
    ]
  return [
      mcp_types.TextContent(type="text", text=f"Unknown tool: '{name}'")
  ]

```

## Further resources

Once you understand the basics, explore [Advanced use cases](/advanced-mcp-tools) for complex implementations and custom integrations.
