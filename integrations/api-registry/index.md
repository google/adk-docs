# Google Cloud API Registry tool for ADK

Supported in ADKPython v1.20.0Preview

The Google Cloud API Registry connector tool for Agent Development Kit (ADK) lets you access a wide range of Google Cloud services for your agents as Model Context Protocol (MCP) servers through the [Google Cloud API Registry](https://docs.cloud.google.com/api-registry/docs/overview). You can configure this tool to connect your agent to your Google Cloud projects and dynamically access Cloud services enabled for that project.

Preview release

The Google Cloud API Registry feature is a Preview release. For more information, see the [launch stage descriptions](https://cloud.google.com/products#product-launch-stages).

## Prerequisites

Before using the API Registry with your agent, you need to ensure the following:

- **Google Cloud project:** Configure your agent to access AI models using an existing Google Cloud project.
- **API Registry access:** The environment where your agent runs needs Google Cloud [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc) with the `apiregistry.viewer` role to list available MCP servers.
- **Cloud APIs:** In your Google Cloud project, enable the *cloudapiregistry.googleapis.com* and *apihub.googleapis.com* Google Cloud APIs.
- **MCP Server and Tool access:** Make sure you enable the MCP Servers in the API Registry for the Google Cloud services in your Cloud Project that you want access with your agent. You can enable this in the Cloud Console or use a gcloud command such as: `gcloud beta api-registry mcp enable bigquery.googleapis.com --project={PROJECT_ID}`. The credentials used by the agent must have permissions to access the MCP server and the underlying services used by the tools. For example, to use BigQuery tools, the service account needs BigQuery IAM roles like `bigquery.dataViewer` and `bigquery.jobUser`. For more information about required permissions, see [Authentication and access](#auth).

You can check what MCP servers are enabled with API Registry using the following gcloud command:

```console
gcloud beta api-registry mcp servers list --project={PROJECT_ID}.
```

## Use with agent

When configuring the API Registry connector tool with an agent, you first initialize the ***ApiRegistry*** class to establish a connection with Cloud services, and then use the `get_toolset()` function to retrieve a toolset for a specific MCP server registered in the API Registry. The following code example demonstrates how to create an agent that uses tools from an MCP server listed in API Registry. This agent is designed to interact with BigQuery:

```python
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.api_registry import ApiRegistry

# Configure with your Google Cloud Project ID and registered MCP server name
PROJECT_ID = "your-google-cloud-project-id"
MCP_SERVER_NAME = "projects/your-google-cloud-project-id/locations/global/mcpServers/your-mcp-server-name"

# Example header provider for BigQuery, a project header is required.
def header_provider(context):
    return {"x-goog-user-project": PROJECT_ID}

# Initialize ApiRegistry
api_registry = ApiRegistry(
    api_registry_project_id=PROJECT_ID,
    header_provider=header_provider
)

# Get the toolset for the specific MCP server
registry_tools = api_registry.get_toolset(
    mcp_server_name=MCP_SERVER_NAME,
    # Optionally filter tools:
    #tool_filter=["list_datasets", "run_query"]
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

For the complete code for this example, see the [api_registry_agent](https://github.com/google/adk-python/tree/main/contributing/samples/api_registry_agent/) sample. For information on the configuration options, see [Configuration](#configuration). For information on the authentication for this tool, see [Authentication and access](#auth).

## Authentication and access

Using the API Registry with your agent requires authentication for the services the agent accesses. By default the tool uses Google Cloud [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc) for authentication. When using this tool make sure your agent has the following permissions and access:

- **API Registry access:** The `ApiRegistry` class uses Application Default Credentials (`google.auth.default()`) to authenticate requests to the Google Cloud API Registry to list the available MCP servers. Ensure the environment where the agent runs has credentials with the necessary permissions to view the API Registry resources, such as `apiregistry.viewer`.

- **MCP Server and Tool access:** The `McpToolset` returned by `get_toolset` also uses the Google Cloud Application Default Credentials by default to authenticate calls to the actual MCP server endpoint. The credentials used must have the necessary permissions for both:

  1. Accessing the MCP server itself.
  1. Utilizing the underlying services and resources that the tools interact with.

- **MCP Tool user role:** Allow the account used by your agent to call MCP tools through the API registry by granting the MCP tool user role: `gcloud projects add-iam-policy-binding {PROJECT_ID} --member={member} --role="roles/mcp.toolUser"`

For example, when using MCP server tools that interact with BigQuery, the account associated with the credentials, such as a service account, must be granted appropriate BigQuery IAM roles, such as `bigquery.dataViewer` or `bigquery.jobUser`, within your Google Cloud project to access datasets and run queries. In the case of the bigquery MCP server, a `"x-goog-user-project": PROJECT_ID` header is required to use its tools Additional headers for authentication or project context can be injected via the `header_provider` argument in the `ApiRegistry` constructor.

## Configuration

The ***APIRegistry*** object has the following configuration options:

- **`api_registry_project_id`** (str): The Google Cloud Project ID where the API Registry is located.
- **`location`** (str, optional): The location of the API Registry resources. Defaults to `"global"`.
- **`header_provider`** (Callable, optional): A function that takes the call context and returns a dictionary of additional HTTP headers to be sent with requests to the MCP server. This is often used for dynamic authentication or project-specific headers.

The `get_toolset()` function has the following configuration options:

- **`mcp_server_name`** (str): The full name of the registered MCP server from which to load tools, for example: `projects/my-project/locations/global/mcpServers/my-server`.

- **`tool_filter`** (Union\[ToolPredicate, List[str]\], optional): Specifies which tools to include in the toolset.

  - If a list of strings, only tools with names in the list are included.
  - If a `ToolPredicate` function, the function is called for each tool, and only tools for which it returns `True` are included.
  - If `None`, all tools from the MCP server are included.

- **`tool_name_prefix`** (str, optional): A prefix to add to the name of each tool in the resulting toolset.

## Additional resources

- [api_registry_agent](https://github.com/google/adk-python/tree/main/contributing/samples/api_registry_agent/) ADK code sample
- [Google Cloud API Registry](https://docs.cloud.google.com/api-registry/docs/overview) documentation
