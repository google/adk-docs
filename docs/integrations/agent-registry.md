---
catalog_title: Google Cloud Agent Registry
catalog_description: Discover and connect to AI Agents and MCP Servers
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["google", "mcp", "connectors"]
---

# Google Cloud Agent Registry

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.26.0</span><span class="lst-go">Go v2.1.0</span><span class="lst-preview">Preview</span>
</div>

The Agent Registry client library within Agent Development Kit (ADK) allows
developers to discover, look up, and connect to AI Agents and MCP Servers
cataloged within the [Google Cloud Agent
Registry](https://docs.cloud.google.com/agent-registry/overview). This enables
dynamic composition of agent-based applications using governed components.

## Use cases

- **Accelerated Development**: Easily find and reuse existing agents and tools
  (MCP Servers) from the central catalog instead of rebuilding them.
- **Dynamic Integration**: Discover agent and MCP Server endpoints at runtime,
  making applications more robust to changes in the environment.
- **Enhanced Governance**: Utilize governed and verified components from the
  registry within your ADK applications.

## Prerequisites

- A [Google Cloud
  project](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects).
- The [Agent Registry API](https://docs.cloud.google.com/agent-registry/setup)
  enabled in your Google Cloud project.
- Authentication configured for your environment. You should log in using
  [Application Default
  Credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
  (`gcloud auth application-default login`).
- Environment variables `GOOGLE_CLOUD_PROJECT` set to your project ID and
  `GOOGLE_CLOUD_LOCATION` set to the appropriate region (e.g., `global`,
  `us-central1`).
- ADK installed for your language, as described in
  [Installation](#installation).

For more information on connecting to Google Cloud from ADK agents, see
[Connect to Google Cloud and Agent Platform](/get-started/google-cloud/).

## Installation

The [Agent Registry](https://docs.cloud.google.com/agent-registry/overview)
integration is part of the core ADK library.

=== "Python"

    ```bash
    pip install google-adk
    ```

    ### Required dependencies

    The `google.adk.integrations.agent_registry` module imports both the A2A SDK
    and the Agent Identity auth provider at module scope, so importing
    `AgentRegistry` raises `ImportError` on a core-only install. Install both the
    `a2a` and `agent-identity` extras:

    ```bash
    pip install "google-adk[a2a,agent-identity]"
    ```

=== "Go"

    ```bash
    go get google.golang.org/adk/v2
    ```

    The client lives in the `google.golang.org/adk/v2/agentregistry` package of
    the core module, so there is nothing extra to install.

## Use with Agent

The primary way to use the Agent Registry integration within an ADK agent is to
dynamically fetch remote agents or toolsets using the Agent Registry client.

=== "Python"

    ```py
    --8<-- "examples/inline/python/integrations/agent-registry/001-use-with-agent.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/integrations/agent-registry/002-use-with-agent.go.txt"
    ```

## Authentication for Google MCP Servers and Remote A2A Agents

### Remote A2A Agents

Calls to a remote A2A agent are not authenticated for you. If you are connecting
to a Google A2A agent, supply an authenticated HTTP client when you create the
remote agent.

=== "Python"

    Pass an `httpx.AsyncClient` configured with Google authentication headers to
    the `get_remote_a2a_agent` method.

    ```python
    --8<-- "examples/inline/python/integrations/agent-registry/003-remote-a2a-agents.py"
    ```

=== "Go"

    Pass an authenticated `*http.Client` with `WithA2AHTTPClient`, or static
    headers with `WithA2AHeaders`.

    ```go
    --8<-- "examples/inline/go/integrations/agent-registry/004-remote-a2a-agents.go.txt"
    ```

    Set any timeout on the client's `Transport` rather than with
    `http.Client.Timeout`, which applies to the whole request and would truncate
    a streaming response.

### Google MCP Servers

For Google MCP servers, authentication headers are automatically passed in.

=== "Python"

    If automatic authentication is not working as expected, you can manually
    provide headers using the `header_provider` argument in the `AgentRegistry`
    constructor.

    ```python
    --8<-- "examples/inline/python/integrations/agent-registry/005-google-mcp-servers.py"
    ```

=== "Go"

    Requests to a `*.googleapis.com` endpoint reuse the credentials of the
    registry client itself. For any other endpoint, or to override that default,
    pass `WithMCPHTTPClient` and `WithMCPHeaders`.

    ```go
    --8<-- "examples/inline/go/integrations/agent-registry/006-google-mcp-servers.go.txt"
    ```

    Headers set this way are applied to every request the toolset sends to the
    MCP server. They do not affect calls to the Agent Registry API itself.

## API Reference

=== "Python"

    The AgentRegistry class provides the following core methods:

    - `list_mcp_servers(self, filter_str, page_size, page_token)`: Fetches a list
      of registered MCP Servers.
    - `get_mcp_server(self, name)`: Retrieves detailed metadata of a specific MCP
      Server.
    - `get_mcp_toolset(self, mcp_server_name)`: Constructs an ADK McpToolset
      instance from a registered MCP Server.
    - `list_agents(self, filter_str, page_size, page_token)`: Fetches a list of
      registered A2A Agents.
    - `get_agent_info(self, name)`: Retrieves detailed metadata of a specific A2A
      Agent.
    - `get_remote_a2a_agent(self, agent_name)`: Creates an ADK RemoteA2aAgent
      instance for a registered A2A Agent.

=== "Go"

    The `agentregistry.Client` type exposes three discovery methods per resource
    kind: `List*` returns a single page, `Get*` returns one resource by its full
    resource name, and `All*` returns an `iter.Seq2` that fetches pages on demand.

    - `ListAgents(ctx, opts ...ListOption)`, `GetAgent(ctx, name)`,
      `AllAgents(ctx, opts ...ListOption)`: registered A2A agents.
    - `ListMCPServers(ctx, opts ...ListOption)`, `GetMCPServer(ctx, name)`,
      `AllMCPServers(ctx, opts ...ListOption)`: registered MCP servers.
    - `ListEndpoints(ctx, opts ...ListOption)`, `GetEndpoint(ctx, name)`,
      `AllEndpoints(ctx, opts ...ListOption)`: registered model endpoints.
    - `RemoteAgent(ctx, name, opts ...RemoteAgentOption)`: resolves a registered
      A2A agent into an `agent.Agent` usable as a sub-agent.
    - `MCPToolset(ctx, name, opts ...MCPToolsetOption)`: resolves a registered MCP
      server into a `tool.Toolset`.

    The list options are `WithFilter`, `WithPageSize`, and `WithPageToken`. The
    `All*` iterators manage the page token themselves. A non-2xx response from the
    Agent Registry API is returned as an `*agentregistry.APIError` carrying the
    `StatusCode` and the response `Body`.

## Configuration Options

=== "Python"

    The AgentRegistry constructor accepts the following arguments:

    - `project_id` (str, required): The Google Cloud project ID.
    - `location` (str, required): The Google Cloud location/region, such as
      "global", "us-central1".
    - `header_provider` (Callable, optional): A callable that takes a
      ReadonlyContext and returns a dictionary of custom headers to be included in
      requests made by the [McpToolset](/tools-custom/mcp-tools/#mcptoolset-class)
      that `get_mcp_toolset` returns, to the target MCP server. These headers do
      not affect calls to the Agent Registry API itself, and they do not affect
      requests made by
      [RemoteA2aAgent](/a2a/quickstart-consuming/#quickstart-consuming-a-remote-agent-via-a2a).
      For those requests, pass an authenticated `httpx.AsyncClient` to
      `get_remote_a2a_agent`, as shown in
      [Remote A2A Agents](#remote-a2a-agents).

=== "Go"

    The `agentregistry.New` constructor takes a `Config` struct:

    - `ProjectID` (string, required): The Google Cloud project ID.
    - `Location` (string, required): The Google Cloud location/region, such as
      "global", "us-central1".
    - `HTTPClient` (`*http.Client`, optional): The client used for Agent Registry
      API calls. When it is nil, ADK builds one from Application Default
      Credentials and resolves the endpoint, including mTLS, from
      `GOOGLE_API_USE_MTLS_ENDPOINT` and `GOOGLE_API_USE_CLIENT_CERTIFICATE`. This
      client is also reused for [McpToolset](/tools-custom/mcp-tools/) traffic to
      `*.googleapis.com` endpoints, but never for
      [A2A](/a2a/quickstart-consuming-go/) traffic.

    Egress to the resolved endpoints is configured per call instead:
    `WithA2AHTTPClient` and `WithA2AHeaders` on `RemoteAgent`,
    `WithMCPHTTPClient` and `WithMCPHeaders` on `MCPToolset`.

## Additional resources
- [Sample Agent Code (Python)](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/agent_registry_agent)
- [Sample Agent Code (Go)](https://github.com/google/adk-go/tree/main/examples/agentregistry)
- [Agent Registry Client (Python)](https://github.com/google/adk-python/blob/main/src/google/adk/integrations/agent_registry/agent_registry.py)
- [Agent Registry Client (Go)](https://pkg.go.dev/google.golang.org/adk/v2/agentregistry)
- [Google Auth Library](https://google-auth.readthedocs.io/en/latest/)
