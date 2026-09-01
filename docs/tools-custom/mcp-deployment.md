# Deploy Agents with MCP Tools

When deploying ADK agents that use MCP tools to production environments like Cloud Run, GKE, or Agent Runtime, you need to consider how MCP connections will work in containerized and distributed environments.

## Critical Deployment Requirement: Synchronous Agent Definition

**⚠️ Important:** When deploying agents with MCP tools, the agent and its McpToolset must be defined **synchronously** in your `agent.py` file. While `adk web` allows for asynchronous agent creation, deployment environments require synchronous instantiation.

```python
# ✅ CORRECT: Synchronous agent definition for deployment
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

_allowed_path = os.path.dirname(os.path.abspath(__file__))

root_agent = LlmAgent(
    model='gemini-flash-latest',
    name='enterprise_assistant',
    instruction=f'Help user accessing their file systems. Allowed directory: {_allowed_path}',
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=['-y', '@modelcontextprotocol/server-filesystem', _allowed_path],
                ),
                timeout=5,  # Configure appropriate timeouts
            ),
            # Filter tools for security in production
            tool_filter=[
                'read_file', 'read_multiple_files', 'list_directory',
                'directory_tree', 'search_files', 'get_file_info',
                'list_allowed_directories',
            ],
        )
    ],
)
```

```python
# ❌ WRONG: Asynchronous patterns don't work in deployment
async def get_agent():  # This won't work for deployment
    toolset = await create_mcp_toolset_async()
    return LlmAgent(tools=[toolset])
```

## Quick Deployment Commands

### Agent Runtime
```bash
uv run adk deploy agent_engine \
  --project=<your-gcp-project-id> \
  --region=<your-gcp-region> \
  --staging_bucket="gs://<your-gcs-bucket>" \
  --display_name="My MCP Agent" \
  ./path/to/your/agent_directory
```

### Cloud Run
```bash
uv run adk deploy cloud_run \
  --project=<your-gcp-project-id> \
  --region=<your-gcp-region> \
  --service_name=<your-service-name> \
  ./path/to/your/agent_directory
```

## Deployment Patterns

### Pattern 1: Self-Contained Stdio MCP Servers

For MCP servers that can be packaged as npm packages or Python modules (like `@modelcontextprotocol/server-filesystem`), you can include them directly in your agent container:

**Container Requirements:**
```dockerfile
# Example for npm-based MCP servers
FROM python:3.13-slim

# Install Node.js and npm for MCP servers
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Install your Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your agent code
COPY . .

# Your agent can now use StdioConnectionParams with 'npx' commands
CMD ["python", "main.py"]
```

**Agent Configuration:**
```python
# This works in containers because npx and the MCP server run in the same environment
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", "/app/data"],
        ),
    ),
)
```

### Pattern 2: Remote MCP Servers (Streamable HTTP)

For production deployments requiring scalability, deploy MCP servers as separate services and connect via Streamable HTTP:

**MCP Server Deployment (Cloud Run):**
```python
# deploy_mcp_server.py - Separate Cloud Run service using Streamable HTTP
import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Any

import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)

def create_mcp_server():
    """Create and configure the MCP server."""
    app = Server("adk-mcp-streamable-server")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
        """Handle tool calls from MCP clients."""
        # Example tool implementation - replace with your actual ADK tools
        if name == "example_tool":
            result = arguments.get("input", "No input provided")
            return [
                types.TextContent(
                    type="text",
                    text=f"Processed: {result}"
                )
            ]
        else:
            raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available tools."""
        return [
            types.Tool(
                name="example_tool",
                description="Example tool for demonstration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Input text to process"
                        }
                    },
                    "required": ["input"]
                }
            )
        ]

    return app

def main(port: int = 8080, json_response: bool = False):
    """Main server function."""
    logging.basicConfig(level=logging.INFO)

    app = create_mcp_server()

    # Create session manager with stateless mode for scalability
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True,  # Important for Cloud Run scalability
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Manage session manager lifecycle."""
        async with session_manager.run():
            logger.info("MCP Streamable HTTP server started!")
            try:
                yield
            finally:
                logger.info("MCP server shutting down...")

    # Create ASGI application
    starlette_app = Starlette(
        debug=False,  # Set to False for production
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    import uvicorn
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
```

**Agent Configuration for Remote MCP:**

=== "Python"

    ```python
    # Your ADK agent connects to the remote MCP service via Streamable HTTP
    McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://your-mcp-server-url.run.app/mcp",
            headers={"Authorization": "Bearer your-auth-token"}
        ),
    )
    ```

=== "Java"

    ```java
    import java.util.Map;
    import com.google.adk.tools.mcp.StreamableHttpServerParameters;
    import com.google.adk.tools.mcp.McpToolset;

    // Your ADK agent connects to the remote MCP service via Streamable HTTP
    StreamableHttpServerParameters streamableParams = StreamableHttpServerParameters.builder()
            .url("https://your-mcp-server-url.run.app/mcp")
            .headers(Map.of("Authorization", "Bearer your-auth-token"))
            .build();

    McpToolset toolset = new McpToolset(streamableParams);
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.tools.mcp.McpConnectionParameters
    import com.google.adk.kt.tools.mcp.McpToolset

    // Your ADK agent connects to the remote MCP service via Streamable HTTP
    // headerProvider is suspend, so fetchToken() can await a fresh token per request;
    // it also disables session reuse, so use StreamableHttp(headers = ...) for a fixed one.
    val toolset =
        McpToolset.McpToolsetConfig(
            streamableHttpConnectionParams =
                McpConnectionParameters.StreamableHttp(
                    url = "https://your-mcp-server-url.run.app/mcp",
                ),
        ).toToolset(headerProvider = { mapOf("Authorization" to "Bearer ${fetchToken()}") })
    ```

### Pattern 3: Sidecar MCP Servers (GKE)

In Kubernetes environments, you can deploy MCP servers as sidecar containers:

```yaml
# deployment.yaml - GKE with MCP sidecar
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent-with-mcp
spec:
  template:
    spec:
      containers:
      # Main ADK agent container
      - name: adk-agent
        image: your-adk-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: MCP_SERVER_URL
          value: "http://localhost:8081"

      # MCP server sidecar
      - name: mcp-server
        image: your-mcp-server:latest
        ports:
        - containerPort: 8081
```

## Connection Management Considerations

### Stdio Connections
- **Pros:** Simple setup, process isolation, works well in containers
- **Cons:** Process overhead, not suitable for high-scale deployments
- **Best for:** Development, single-tenant deployments, simple MCP servers

### SSE/HTTP Connections
- **Pros:** Network-based, scalable, can handle multiple clients
- **Cons:** Requires network infrastructure, authentication complexity
- **Best for:** Production deployments, multi-tenant systems, external MCP services

## Production Deployment Checklist

When deploying agents with MCP tools to production:

**✅ Connection Lifecycle**
- Ensure proper cleanup of MCP connections using exit_stack patterns
- Configure appropriate timeouts for connection establishment and requests
- Implement retry logic for transient connection failures

**✅ Resource Management**
- Monitor memory usage for stdio MCP servers (each spawns a process)
- Configure appropriate CPU/memory limits for MCP server processes
- Consider connection pooling for remote MCP servers

**✅ Security**
- Use authentication headers for remote MCP connections
- Restrict network access between ADK agents and MCP servers
- **Filter MCP tools using `tool_filter` to limit exposed functionality**
- Validate MCP tool inputs to prevent injection attacks
- Use restrictive file paths for filesystem MCP servers (e.g., `os.path.dirname(os.path.abspath(__file__))`)
- Consider read-only tool filters for production environments

**✅ Monitoring & Observability**
- Log MCP connection establishment and teardown events
- Monitor MCP tool execution times and success rates
- Set up alerts for MCP connection failures

**✅ Scalability**
- For high-volume deployments, prefer remote MCP servers over stdio
- Configure session affinity if using stateful MCP servers
- Consider MCP server connection limits and implement circuit breakers

## Environment-Specific Configurations

### Cloud Run
```python
# Cloud Run environment variables for MCP configuration
import os

# Detect Cloud Run environment
if os.getenv('K_SERVICE'):
    # Use remote MCP servers in Cloud Run
    mcp_connection = SseConnectionParams(
        url=os.getenv('MCP_SERVER_URL'),
        headers={'Authorization': f"Bearer {os.getenv('MCP_AUTH_TOKEN')}"}
    )
else:
    # Use stdio for local development
    mcp_connection = StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        )
    )

McpToolset(connection_params=mcp_connection)
```

### GKE
```python
# GKE-specific MCP configuration
# Use service discovery for MCP servers within the cluster
McpToolset(
    connection_params=SseConnectionParams(
        url="http://mcp-service.default.svc.cluster.local:8080/sse"
    ),
)
```

### Agent Runtime
```python
# Agent Runtime managed deployment
# Prefer lightweight, self-contained MCP servers or external services
McpToolset(
    connection_params=SseConnectionParams(
        url="https://your-managed-mcp-service.googleapis.com/sse",
        headers={'Authorization': 'Bearer $(gcloud auth print-access-token)'}
    ),
)
```

## Troubleshooting Deployment Issues

**Common MCP Deployment Problems:**

1. **Stdio Process Startup Failures**
   ```python
   # Debug stdio connection issues
   McpToolset(
       connection_params=StdioConnectionParams(
           server_params=StdioServerParameters(
               command='npx',
               args=["-y", "@modelcontextprotocol/server-filesystem", "/app/data"],
               # Add environment debugging
               env={'DEBUG': '1'}
           ),
       ),
   )
   ```

2. **Network Connectivity Issues**
   ```python
   # Test remote MCP connectivity
   import aiohttp

   async def test_mcp_connection():
       async with aiohttp.ClientSession() as session:
           async with session.get('https://your-mcp-server.com/health') as resp:
               print(f"MCP Server Health: {resp.status}")
   ```

3. **Resource Exhaustion**
   - Monitor container memory usage when using stdio MCP servers
   - Set appropriate limits in Kubernetes deployments
   - Use remote MCP servers for resource-intensive operations
