---
catalog_title: Google Cloud Agent Registry
catalog_description: Connect with Google Cloud services as MCP tools and other agents.
catalog_icon: /adk-docs/integrations/assets/developer-tools-color.svg
catalog_tags: ["google", "mcp", "connectors", "a2a"]
---

# Google Cloud Agent Registry tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.26.0</span><span class="lst-preview">Preview</span>
</div>

The Google Cloud Agent Registry connector tool for Agent Development Kit (ADK)
lets you access a wide range of Google Cloud services for your agents. You can
use it to retrieve Model-Conversation-Tools (MCP) toolsets and remote A2A agents
from the [Google Cloud Agent Registry](https://cloud.google.com/agent-registry/docs/overview).
You can configure this tool to connect your agent to your Google Cloud projects
and dynamically access Cloud services enabled for that project.

!!! example "Preview release"
    The Google Cloud Agent Registry feature is a Preview release. For
    more information, see the
    [launch stage descriptions](https://cloud.google.com/products#product-launch-stages).

## `AgentRegistry` vs `ApiRegistry`

The `google.adk.integrations.agent_registry.AgentRegistry` class is the recommended
tool for interacting with the Google Cloud Agent Registry. It supports retrieving both
MCP toolsets and remote A2A agents.

An older class, `google.adk.tools.api_registry.ApiRegistry`, is still available for
interacting with the previous version of the service, the API Registry. For new
development, you should use `AgentRegistry`.

## Prerequisites

Before using the Agent Registry with your agent, you need to ensure the following:

-   **Google Cloud project:** Configure your agent to access AI models using an
    existing Google Cloud project.

-   **Agent Registry access:** The environment where your agent runs needs Google
    Cloud [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc)
    with the `agentregistry.viewer` role to list available resources.

-   **Cloud APIs:** In your Google Cloud project, enable the
    `agentregistry.googleapis.com` Google Cloud API.

-   **Resource Access:** The credentials used by the agent must have permissions to
    access the underlying services used by the tools or agents. For example, to
    use BigQuery tools, the service account needs BigQuery IAM roles like
    `bigquery.dataViewer` and `bigquery.jobUser`. For more information about
    required permissions, see [Authentication and access](#auth).

## Use with agent

When configuring the Agent Registry connector tool with an agent, you first
initialize the `AgentRegistry` class to establish a connection with the service,
and then use the `get_mcp_toolset()` or `get_remote_a2a_agent()` methods to
retrieve the desired resource.

### Retrieving an MCP Toolset

The following code example demonstrates how to create an agent that uses tools
from an MCP server listed in Agent Registry. This agent is designed to interact
with BigQuery:

```python
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.integrations.agent_registry import AgentRegistry

# Configure with your Google Cloud Project ID, location, and registered MCP server name
PROJECT_ID = "your-google-cloud-project-id"
LOCATION = "your-google-cloud-location"
MCP_SERVER_NAME = f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/your-mcp-server-name"

# Example header provider for BigQuery, a project header is required.
def header_provider(context):
    return {"x-goog-user-project": PROJECT_ID}

# Initialize AgentRegistry
agent_registry = AgentRegistry(
    project_id=PROJECT_ID,
    location=LOCATION,
    header_provider=header_provider
)

# Get the toolset for the specific MCP server
registry_tools = agent_registry.get_mcp_toolset(
    mcp_server_name=MCP_SERVER_NAME,
)

# Create an agent with the tools
root_agent = LlmAgent(
    model="gemini-1.5-flash", # Or your preferred model
    name="bigquery_assistant",
    instruction="""
Help user access their BigQuery data using the available tools.
    """,
    tools=[registry_tools],
)
```

### Retrieving a Remote A2A Agent

Here is an example of how to retrieve a remote A2A agent from the Agent Registry:

```python
from google.adk.integrations.agent_registry import AgentRegistry

# Configure with your Google Cloud Project ID, location, and registered agent name
PROJECT_ID = "your-google-cloud-project-id"
LOCATION = "your-google-cloud-location"
AGENT_NAME = f"projects/{PROJECT_ID}/locations/{LOCATION}/agents/your-agent-name"

# Initialize AgentRegistry
agent_registry = AgentRegistry(
    project_id=PROJECT_ID,
    location=LOCATION
)

# Get the remote A2A agent
remote_agent = agent_registry.get_remote_a2a_agent(
    agent_name=AGENT_NAME
)

# Now you can use the remote_agent in your application
# For example, you could add it to a router agent.
```

## Authentication and access {#auth}

Using the Agent Registry with your agent requires authentication for the services
the agent accesses. By default the tool uses Google Cloud
[Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc)
for authentication. When using this tool make sure your agent has the following
permissions and access:

-   **Agent Registry access:** The `AgentRegistry` class uses Application Default
    Credentials (`google.auth.default()`) to authenticate requests to the Google
    Cloud Agent Registry. Ensure the environment where the agent runs has
    credentials with the necessary permissions to view the Agent Registry
    resources, such as `agentregistry.viewer`.

-   **MCP Server and Tool access:** The `McpToolset` returned by `get_mcp_toolset`
    also uses the Google Cloud Application Default Credentials by default to
    authenticate calls to the actual MCP server endpoint. The credentials used
    must have the necessary permissions for both:
    1.  Accessing the MCP server itself.
    2.  Utilizing the underlying services and resources that the tools interact
        with.

-   **Remote A2A Agent access:** Similarly, the `RemoteA2aAgent` returned by
    `get_remote_a2a_agent` will use Application Default Credentials to communicate
    with the remote agent. The credentials must have the necessary permissions
    to invoke the remote agent's skills.

For example, when using MCP server tools that interact with BigQuery, the
account associated with the credentials, such as a service account, must be
granted appropriate BigQuery IAM roles, such as `bigquery.dataViewer` or
`bigquery.jobUser`, within your Google Cloud project to access datasets and run
queries. Additional headers for authentication or project context can be
injected via the `header_provider` argument in the `AgentRegistry` constructor.

## Configuration {#configuration}

The `AgentRegistry` object has the following configuration options:

-   **`project_id`** (str): The Google Cloud Project ID where the
    Agent Registry is located.
-   **`location`** (str): The location of the Agent Registry resources.
-   **`header_provider`** (Callable, optional): A function that takes the call
    context and returns a dictionary of additional HTTP headers to be sent with
    requests to the MCP server or remote agent. This is often used for dynamic
    authentication or project-specific headers.

The `get_mcp_toolset()` function has the following configuration options:

-   **`mcp_server_name`** (str): The full name of the registered MCP server from
    which to load tools, for example:
    `projects/my-project/locations/global/mcpServers/my-server`.

The `get_remote_a2a_agent()` function has the following configuration options:

-   **`agent_name`** (str): The full name of the registered agent from which to
    load the remote agent, for example:
    `projects/my-project/locations/global/agents/my-agent`.

## Additional resources

-   [Google Cloud Agent Registry](https://cloud.google.com/agent-registry/docs/overview)
    documentation
