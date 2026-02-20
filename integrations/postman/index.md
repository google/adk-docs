# Postman MCP tool for ADK

Supported in ADKPythonTypeScript

The [Postman MCP Server](https://github.com/postmanlabs/postman-mcp-server) connects your ADK agent to the [Postman](https://www.postman.com/) ecosystem. This integration gives your agent the ability to access workspaces, manage collections and environments, evaluate APIs, and automate workflows through natural language interactions.

## Use cases

- **API testing**: Continuously test your APIs using your Postman collections.
- **Collection management**: Create and tag collections, update documentation, add comments, or perform actions across multiple collections without leaving your editor.
- **Workspace and environment management**: Create workspaces and environments, and manage your environment variables.
- **Client code generation**: Generate production-ready client code that consumes APIs following best practices and project conventions.

## Prerequisites

- Create a [Postman account](https://identity.getpostman.com/signup)
- Generate a [Postman API key](https://postman.postman.co/settings/me/api-keys)

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="postman_agent",
    instruction="Help users manage their Postman workspaces and collections",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@postman/postman-mcp-server",
                        # "--full",  # Use all 100+ tools
                        # "--code",  # Use code generation tools
                        # "--region", "eu",  # Use EU region
                    ],
                    env={
                        "POSTMAN_API_KEY": POSTMAN_API_KEY,
                    },
                ),
                timeout=30,
            ),
        )
    ],
)
```

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="postman_agent",
    instruction="Help users manage their Postman workspaces and collections",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPServerParams(
                url="https://mcp.postman.com/mcp",
                # (Optional) Use "/minimal" for essential tools only
                # (Optional) Use "/code" for code generation tools
                # (Optional) Use "https://mcp.eu.postman.com" for EU region
                headers={
                    "Authorization": f"Bearer {POSTMAN_API_KEY}",
                },
            ),
        )
    ],
)
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "postman_agent",
    instruction: "Help users manage their Postman workspaces and collections",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "@postman/postman-mcp-server",
                    // "--full",  // Use all 100+ tools
                    // "--code",  // Use code generation tools
                    // "--region", "eu",  // Use EU region
                ],
                env: {
                    POSTMAN_API_KEY: POSTMAN_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "postman_agent",
    instruction: "Help users manage their Postman workspaces and collections",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.postman.com/mcp",
            // (Optional) Use "/minimal" for essential tools only
            // (Optional) Use "/code" for code generation tools
            // (Optional) Use "https://mcp.eu.postman.com" for EU region
            header: {
                Authorization: `Bearer ${POSTMAN_API_KEY}`,
            },
        }),
    ],
});

export { rootAgent };
```

## Configuration

Postman offers three tool configurations:

- **Minimal** (default): Essential tools for basic Postman operations. Best for simple modifications to collections, workspaces, or environments.
- **Full**: All available Postman API tools (100+ tools). Ideal for advanced collaboration and enterprise features.
- **Code**: Tools for searching API definitions and generating client code. Perfect for developers who need to consume APIs.

To select a configuration:

- **Local server**: Add `--full` or `--code` to the `args` list.
- **Remote server**: Change the URL path to `/minimal`, `/mcp` (full), or `/code`.

For EU region, use `--region eu` (local) or `https://mcp.eu.postman.com` (remote).

## Additional resources

- [Postman MCP Server on GitHub](https://github.com/postmanlabs/postman-mcp-server)
- [Postman API key settings](https://postman.postman.co/settings/me/api-keys)
- [Postman Learning Center](https://learning.postman.com/)
