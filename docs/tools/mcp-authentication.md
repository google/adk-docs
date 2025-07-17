# Authenticating with Remote MCP Servers

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python."}

This guide explains how to connect your ADK agent to a remote Model Context Protocol (MCP) server that requires authentication. This is a common requirement for production environments where MCP servers expose sensitive tools or data and must be secured.

You will learn how to use ADK's built-in authentication framework with `MCPToolset` to securely pass credentials, such as Bearer tokens, to a remote MCP server.

## Core Concepts

ADK integrates its standard authentication system with `MCPToolset`, allowing you to secure connections to remote MCP servers in the same way you would for a REST API or OpenAPI tool.

The key components are:

1.  **`MCPToolset`**: The ADK toolset for integrating with MCP servers.
2.  **`StreamableHTTPConnectionParams`**: The recommended connection parameter class for connecting to remote MCP servers over HTTP. It allows you to specify the server's URL.
3.  **`auth_scheme`**: An object defining *how* the server expects credentials. For many modern services, this will be `HTTPBearer()` for sending an `Authorization: Bearer <token>` header.
4.  **`auth_credential`**: An object holding the *actual* credential information, such as the Bearer token itself.

When you provide an `auth_scheme` and `auth_credential` to `MCPToolset`, ADK automatically constructs the correct `Authorization` header and includes it in all requests to the MCP server.

## Example: Connecting to a Secured Server with a Bearer Token

This example demonstrates how to build an agent that connects to a remote MCP server protected by Bearer token authentication. We will provide a complete, runnable example that includes a mock server, so you can test the entire flow locally.

### Step 1: Create a Mock Authenticated MCP Server

First, let's create a simple MCP server using FastAPI that requires an `Authorization` header. This simulates a real-world secured service.

Save this code as `mock_mcp_server.py`:

```python title="mock_mcp_server.py"
--8<-- "examples/python/snippets/tools/mcp_auth/mock_mcp_server.py:init"
```

This server does the following:
*   It listens for POST requests on the `/mcp` endpoint.
*   It checks for an `Authorization` header.
*   If the header is missing or the token is incorrect, it returns a `401 Unauthorized` error.
*   If the token is valid (`secret-token-123`), it responds with a mock list of tools, simulating a real MCP server.

### Step 2: Create the ADK Agent with Authentication

Next, create the ADK agent. This agent will be configured to send the required Bearer token to the mock server.

Save this code as `agent_with_auth.py`:

```python title="agent_with_auth.py"
--8<-- "examples/python/snippets/tools/mcp_auth/agent_with_auth.py:init"
```

Key parts of this agent configuration:

*   **`StreamableHTTPConnectionParams`**: We use this to point to our mock server's URL (`http://127.0.0.1:8001/mcp`).
*   **`auth_scheme = HTTPBearer()`**: This tells ADK that the authentication method is a Bearer token sent via an HTTP header.
*   **`auth_credential`**: This holds the actual token. We use `AuthCredential` with `auth_type=AuthCredentialTypes.HTTP` and provide the token value.

!!! tip "Best Practice: Use Environment Variables for Tokens"
    In the example, the token is hardcoded for simplicity. In a real application, you should **never** hardcode secrets. Load them from environment variables or a secure secret manager.
    ```python
    import os
    my_token = os.environ.get("MY_MCP_API_TOKEN")
    ```

### Step 3: Run and Test the Example

1.  **Install dependencies:**
    ```shell
    pip install fastapi uvicorn
    ```

2.  **Start the mock server:**
    Open a terminal and run:
    ```shell
    uvicorn mock_mcp_server:app --host 127.0.0.1 --port 8001
    ```
    The server is now running and waiting for connections.

3.  **Run the ADK agent:**
    Open a *second* terminal, ensure your ADK environment is active, and run:
    ```shell
    python agent_with_auth.py
    ```

**Expected Output:**

In the terminal running `agent_with_auth.py`, you should see the agent successfully get the tool list and then call the `get_user_profile` tool:

```console
User Query: 'What is the profile for user 42?'
Running agent...
Event received: ... 'function_call': {'name': 'get_user_profile', 'args': {'user_id': '42'}} ...
Event received: ... 'function_response': {'name': 'get_user_profile', 'response': {'id': '42', 'name': 'Jane Doe', 'email': 'jane.doe@example.com'}} ...
Event received: ... 'text': 'The user profile for user ID 42 belongs to Jane Doe, with the email address jane.doe@example.com.' ...
```

In the terminal running the `mock_mcp_server.py`, you will see logs confirming it received the requests with the correct authorization:

```console
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Application startup complete.
INFO:     127.0.0.1:xxxx - "POST /mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:xxxx - "POST /mcp HTTP/1.1" 200 OK
```

This confirms that the ADK agent successfully authenticated with the remote MCP server.

## Deployment Considerations

When deploying agents that use authenticated MCP tools to production environments like Cloud Run or Agent Engine, special considerations are necessary.

*   **Avoid `StdioConnectionParams`**: Do not use `stdio`-based connections in a serverless or containerized environment. The MCP server should always be a separate, network-accessible service.
*   **Secure Credential Management**: Use a service like Google Secret Manager to store and retrieve API tokens and other credentials at runtime. Do not store them in source code or as plain text environment variables.
*   **Service-to-Service Authentication**: In cloud environments, leverage built-in service-to-service authentication mechanisms. For example, a Cloud Run service can be configured to only accept requests from other specific services, using automatically managed identity tokens.

For detailed guidance, see the new sections on deploying agents with MCP tools in the deployment guides:
*   [**Deploy to Cloud Run**](../deploy/cloud-run.md#deploying-agents-with-mcp-tools)
*   [**Deploy to Agent Engine**](../deploy/agent-engine.md#deploying-agents-with-mcp-tools)