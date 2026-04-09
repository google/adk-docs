---
sidebar_label: Agent Registry
---

# Google Cloud Agent Registry Integration

The `AgentRegistry` client in the ADK provides a high-level interface for interacting with the Google Cloud Agent Registry service. This integration allows you to dynamically discover and use agents, tools, and other resources registered within your Google Cloud project.

## Initializing the Client

To get started, you need to initialize the `AgentRegistry` with your Google Cloud project ID and location:

```python
from google.adk.integrations.agent_registry import AgentRegistry

agent_registry_client = AgentRegistry(
    project_id="your-gcp-project-id",
    location="your-gcp-location"
)
```

The client automatically handles authentication using the default Google Cloud credentials from your environment.

## Interacting with Endpoints

The Agent Registry can store various types of endpoints. The `AgentRegistry` client provides methods to list, retrieve, and resolve these endpoints.

### Listing and Getting Endpoints

You can list all available endpoints or retrieve a specific endpoint by name.

- `list_endpoints()`: Fetches a list of endpoints. You can also filter the results.
- `get_endpoint()`: Retrieves the full details of a specific endpoint by its resource name.

### Resolving Model Names

A common use case is to resolve a registered endpoint to a specific model resource name that can be used with other Google Cloud services (like Vertex AI).

- `get_model_name()`: Takes an endpoint's resource name and returns the corresponding model resource name.

```python
# Example of resolving a model name
endpoint_name = "projects/your-gcp-project-id/locations/your-gcp-location/endpoints/your-endpoint-id"
model_name = agent_registry_client.get_model_name(endpoint_name)

print(f"Resolved model name: {model_name}")
```

## Using MCP Toolsets with Authentication

You can retrieve an MCP toolset from a registered MCP server. The `get_mcp_toolset` method now supports passing authentication details.

- `get_mcp_toolset()`: Constructs an `McpToolset` instance from a registered MCP Server.
  - `auth_scheme`: An `AuthScheme` to use for authenticating to the toolset.
  - `auth_credential`: An `AuthCredential` to use for the specified authentication scheme.

This allows the ADK to securely connect to MCP toolsets that require authentication.

```python
from google.adk.auth.auth_schemes import AuthScheme
from google.adk.auth.auth_credential import AuthCredential

# Example of retrieving an MCP toolset with authentication
mcp_server_name = "projects/your-gcp-project-id/locations/your-gcp-location/mcpServers/your-mcp-server"

# Define your authentication scheme and credentials
my_auth_scheme = AuthScheme(...)
my_auth_credential = AuthCredential(...)

mcp_toolset = agent_registry_client.get_mcp_toolset(
    mcp_server_name,
    auth_scheme=my_auth_scheme,
    auth_credential=my_auth_credential
)
```

## Using Remote A2A Agents with Custom HTTPX Client

When creating a `RemoteA2aAgent` from a registered A2A agent, you can now inject a custom `httpx.AsyncClient`. This is useful for advanced scenarios, such as configuring custom timeouts, proxies, or transport settings.

- `get_remote_a2a_agent()`: Creates a `RemoteA2aAgent` instance.
  - `httpx_client`: An optional `httpx.AsyncClient` to use for making requests.

```python
import httpx

# Example of injecting a custom httpx client
agent_name = "projects/your-gcp-project-id/locations/your-gcp-location/agents/your-a2a-agent"

custom_client = httpx.AsyncClient(
    timeout=httpx.Timeout(60.0),
    # ... other custom settings
)

remote_agent = agent_registry_client.get_remote_a2a_agent(
    agent_name,
    httpx_client=custom_client
)
```
