# Google Cloud Agent Registry

Supported in ADKPython v1.26.0Preview

The Agent Registry client library withins Agent Development Kit (ADK) allows developers to discover, look up, and connect to AI Agents and MCP Servers cataloged within the [Google Cloud Agent Registry](https://docs.cloud.google.com/agent-registry/overview). This enables dynamic composition of agent-based applications using governed components.

## Use cases

- **Accelerated Development**: Easily find and reuse existing agents and tools (MCP Servers) from the central catalog instead of rebuilding them.
- **Dynamic Integration**: Discover agent and MCP Server endpoints at runtime, making applications more robust to changes in the environment.
- **Enhanced Governance**: Utilize governed and verified components from the registry within your ADK applications.

## Prerequisites

- A [Google Cloud project](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects).
- The [Agent Registry API](https://docs.cloud.google.com/agent-registry/setup) enabled in your Google Cloud project.
- Authentication configured for your environment. You should log in using [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials) (`gcloud auth application-default login`).
- Environment variables `GOOGLE_CLOUD_PROJECT` set to your project ID and `GOOGLE_CLOUD_LOCATION` set to the appropriate region (e.g., `global`, `us-central1`).
- `google-adk` library installed.

## Installation

The [Agent Registry](https://docs.cloud.google.com/agent-registry/overview) integration is part of the core ADK library.

```bash
pip install google-adk
```

### Optional Dependencies

To use the full capabilities of the AgentRegistry integration, you may need to install additional extras depending on your use case:

**For A2A (Agent-to-Agent) Support:** If you plan to use `get_remote_a2a_agent` or interact with remote A2A-compliant agents, install the `a2a` extra:

```bash
pip install "google-adk[a2a]"
```

**For Agent Identity (GCP Auth Provider):** If you need to use the `GcpAuthProvider` (e.g., when `get_mcp_toolset` automatically resolves authentication via IAM bindings for registered MCP servers), install the `agent-identity` extra:

```bash
pip install "google-adk[agent-identity]"
```

## Use with Agent

The primary way to use the Agent Registry integration within an ADK agent is to dynamically fetch remote agents or toolsets using the AgentRegistry client.

```py
from google.adk.agents.llm_agent import LlmAgent
from google.adk.integrations.agent_registry import AgentRegistry
import os

# 1. Initialization
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

if not project_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")

registry = AgentRegistry(
    project_id=project_id,
    location=location,
)

# 2. Listing Resources
print("Listing Agents...")
agents_response = registry.list_agents()
for agent in agents_response.get("agents", []):
    print(f"  - {agent.get('name')} ({agent.get('displayName')})")

print("Listing MCP Servers...")
mcp_servers_response = registry.list_mcp_servers()
for server in mcp_servers_response.get("mcpServers", []):
    print(f"  - {server.get('name')} ({server.get('displayName')})")

# 3. Using a Remote A2A Agent
# Replace with the full resource name of your registered agent
agent_name = f"projects/{project_id}/locations/{location}/agents/YOUR_AGENT_ID"
my_remote_agent = registry.get_remote_a2a_agent(agent_name=agent_name)

# 4. Using an MCP Toolset
# Replace with the full resource name of your registered MCP server
mcp_server_name = f"projects/{project_id}/locations/{location}/mcpServers/YOUR_MCP_SERVER_ID"
my_mcp_toolset = registry.get_mcp_toolset(mcp_server_name=mcp_server_name)

# 5. Example Agent Composition
main_agent = LlmAgent(
    model="gemini-flash-latest", # Or your preferred model
    name="demo_agent",
    instruction="You can leverage registered tools and sub-agents.",
    tools=[my_mcp_toolset],
    sub_agents=[my_remote_agent],
)
```

## Authentication for Google MCP Servers and Remote A2A Agents

### Remote A2A Agents

If you are connecting to a Google A2A agent, you need to pass an `httpx.AsyncClient` configured with Google authentication headers to the `get_remote_a2a_agent` method.

Example:

```python
import httpx
import google.auth
from google.auth.transport.requests import Request

class GoogleAuth(httpx.Auth):
    def __init__(self):
        self.creds, _ = google.auth.default()
    def auth_flow(self, request):
        if not self.creds.valid:
            self.creds.refresh(Request())
        request.headers["Authorization"] = f"Bearer {self.creds.token}"
        yield request

httpx_client = httpx.AsyncClient(auth=GoogleAuth(), timeout=httpx.Timeout(60.0))
remote_agent = registry.get_remote_a2a_agent(
    f"projects/{project_id}/locations/{location}/agents/YOUR_AGENT_ID",
    httpx_client=httpx_client,
)
```

### Google MCP Servers

For Google MCP servers, authentication headers are automatically passed in. However, if automatic authentication is not working as expected, you can manually provide headers using the `header_provider` argument in the `AgentRegistry` constructor.

Example:

```python
import google.auth
from google.auth.transport.requests import Request
from google.adk.integrations.agent_registry import AgentRegistry

def google_auth_header_provider(context):
    creds, _ = google.auth.default()
    if not creds.valid:
        creds.refresh(Request())
    return {"Authorization": f"Bearer {creds.token}"}

registry = AgentRegistry(
    project_id=project_id,
    location=location,
    header_provider=google_auth_header_provider
)
```

## API Reference

The AgentRegistry class provides the following core methods:

- `list_mcp_servers(self, filter_str, page_size, page_token)`: Fetches a list of registered MCP Servers.
- `get_mcp_server(self, name)`: Retrieves detailed metadata of a specific MCP Server.
- `get_mcp_toolset(self, mcp_server_name)`: Constructs an ADK McpToolset instance from a registered MCP Server.
- `list_agents(self, filter_str, page_size, page_token)`: Fetches a list of registered A2A Agents.
- `get_agent_info(self, name)`: Retrieves detailed metadata of a specific A2A Agent.
- `get_remote_a2a_agent(self, agent_name)`: Creates an ADK RemoteA2aAgent instance for a registered A2A Agent.

## Configuration Options

The AgentRegistry constructor accepts the following arguments:

- `project_id` (str, required): The Google Cloud project ID.
- `location` (str, required): The Google Cloud location/region, such as "global", "us-central1".
- `header_provider` (Callable, optional): A callable that takes a ReadonlyContext and returns a dictionary of custom headers to be included in requests made by the [McpToolset](/tools-custom/mcp-tools/#mcptoolset-class) or [RemoteA2aAgent](/a2a/quickstart-consuming-go/#quickstart-consuming-a-remote-agent-via-a2a) to the target services. This does not affect headers used to call the Agent Registry API itself.

## Additional resources

- [Sample Agent Code](https://github.com/google/adk-python/tree/main/contributing/samples/agent_registry_agent)
- [Agent Registry Client](https://github.com/google/adk-python/blob/main/src/google/adk/integrations/agent_registry/agent_registry.py)
- [Google Auth Library](https://google-auth.readthedocs.io/en/latest/)
