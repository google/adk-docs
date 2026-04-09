# Google Cloud Agent Registry Integration

The `AgentRegistry` client in the ADK provides a high-level interface for interacting with the Google Cloud Agent Registry service. This allows you to discover and integrate with registered agents and other resources within your Google Cloud project.

## Initializing the AgentRegistry Client

To get started, you need to initialize the `AgentRegistry` client with your Google Cloud project ID and location.

```python
from google.adk.integrations.agent_registry import AgentRegistry

agent_registry = AgentRegistry(
    project_id="your-gcp-project-id",
    location="your-gcp-location",
)
```

## Working with Endpoints

The `AgentRegistry` client now includes methods for discovering and resolving model endpoints.

### Listing Endpoints

You can list all available endpoints in your configured project and location using the `list_endpoints()` method.

```python
all_endpoints = agent_registry.list_endpoints()
print(all_endpoints)
```

### Getting a Specific Endpoint

If you know the name of a specific endpoint, you can retrieve its details with the `get_endpoint()` method.

```python
endpoint_details = agent_registry.get_endpoint("projects/your-gcp-project-id/locations/your-gcp-location/endpoints/your-endpoint-id")
print(endpoint_details)
```

### Resolving Model Names

The `get_model_name()` method simplifies the process of extracting a model resource name from an endpoint.

```python
model_name = agent_registry.get_model_name("projects/your-gcp-project-id/locations/your-gcp-location/endpoints/your-endpoint-id")
print(model_name)
```

## Authenticating MCP Toolsets

When retrieving an MCP toolset with `get_mcp_toolset()`, you can now provide authentication details using the `auth_scheme` and `auth_credential` parameters. This allows the ADK to handle authentication when communicating with the MCP server.

```python
from google.adk.auth import AuthScheme
from google.adk.auth.auth_credential import ServiceAccountCredential

# Example using a service account for authentication
auth_credential = ServiceAccountCredential(
    service_account_email="your-service-account@your-project.iam.gserviceaccount.com"
)

mcp_toolset = agent_registry.get_mcp_toolset(
    mcp_server_name="projects/your-gcp-project-id/locations/your-gcp-location/mcpServers/your-mcp-server",
    auth_scheme=AuthScheme.GOOGLE_ID_TOKEN,
    auth_credential=auth_credential
)
```

## Custom HTTPX Client for Remote A2A Agents

For advanced use cases, such as adding custom logging or telemetry, `get_remote_a2a_agent()` now supports injecting a custom `httpx.AsyncClient`.

```python
import httpx

# Create a custom httpx client
custom_client = httpx.AsyncClient(timeout=30.0)

remote_agent = agent_registry.get_remote_a2a_agent(
    agent_name="projects/your-gcp-project-id/locations/your-gcp-location/agents/your-agent-id",
    httpx_client=custom_client
)
```

This provides greater flexibility for controlling the HTTP communication between the ADK and the remote agent.
