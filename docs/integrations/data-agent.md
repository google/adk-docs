---
catalog_title: Data Agents
catalog_description: Analyze data with AI-powered agents
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["data", "google"]
---

# Google Cloud Data Agents tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.23.0</span>
</div>

These are a set of tools aimed to provide integration with data agents powered by the [Conversational Analytics API](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/overview).

Data agents are AI-powered agents that help you analyze your data using natural language. When configuring a data agent, you can choose from supported data sources, including **BigQuery**, **Looker**, and **Looker Studio**.

The `DataAgentToolset` includes the following read-only tools by default:

* **`list_accessible_data_agents`**: Lists data agents you have permission to access in a specified Google Cloud project. Supports an optional `location` override as well as automatic or manual pagination (`page_size` and `page_token`).
* **`get_data_agent_info`**: Retrieves details and published context about a specific data agent given its full resource name (`projects/{project}/locations/{location}/dataAgents/{agent}`).
* **`ask_data_agent`**: Sends a natural language question to a specific data agent and returns its response.

If you set `enable_data_agent_modification=True` in `DataAgentToolConfig`, the toolset also includes the following tools:

* **`create_data_agent`**: Creates a new data agent with the given `data_agent_id` in a Google Cloud project from a JSON `agent_config` that follows the [`DataAgent` resource schema](https://docs.cloud.google.com/gemini/data-agents/reference/rest/v1/projects.locations.dataAgents#DataAgent). The `location` argument is optional.
* **`update_data_agent`**: Updates an existing data agent from a JSON `agent_config` and a comma-separated `update_mask` of camelCase field names (for example, `displayName,description`). Every field listed in `update_mask` must also be present in `agent_config`.
* **`delete_data_agent`**: Deletes an existing data agent given its full resource name.

These modification tools wait for the underlying long-running operation to complete, up to `data_agent_modification_timeout_seconds`.

## Prerequisites

Before using these tools, complete the following steps in Google Cloud:

* Enable the Gemini Data Analytics API (`geminidataanalytics.googleapis.com`) in your Google Cloud project.
* Ensure that the credentials used by the toolset have the required IAM permissions for data agents and their underlying data sources.
* The `get_data_agent_info` and `ask_data_agent` tools require an existing data agent. You can create one using `create_data_agent` (when `enable_data_agent_modification=True`) or by following one of these guides:
    * [Build a data agent using HTTP and Python](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-http)
    * [Build a data agent using the Python SDK](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-sdk)
    * [Create a data agent in BigQuery Studio](https://docs.cloud.google.com/bigquery/docs/create-data-agents#create_a_data_agent)

## Authentication

The `DataAgentToolset` requires a `DataAgentCredentialsConfig` and supports several authentication mechanisms. You must provide either `credentials`, `external_access_token_key`, or a `client_id` and `client_secret` pair. By default, `DataAgentCredentialsConfig` uses the `https://www.googleapis.com/auth/bigquery` OAuth scope, which you can override using `scopes` when configuring OAuth client credentials.

!!! example "Experimental"
    The `DataAgentCredentialsConfig` class extends `BaseGoogleCredentialsConfig`, which is
    experimental and should not be used for production projects.

### Application Default Credentials

You should use this approach for local development and running on Google Cloud services, such as Cloud Run and GKE.

```python
import google.auth
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# Load Application Default Credentials
credentials, project_id = google.auth.default()

# Configure the toolset
credentials_config = DataAgentCredentialsConfig(credentials=credentials)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### Service Account

You can explicitly provide a service account file or info.

```python
from google.oauth2 import service_account
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# Load Service Account credentials
credentials = service_account.Credentials.from_service_account_file('path/to/key.json')

# Configure the toolset
credentials_config = DataAgentCredentialsConfig(credentials=credentials)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### External Access Token

For applications that need to act on behalf of an end-user, you can pass user credentials directly instantiated from an access token, such as from an OAuth2 flow or an external IDP.

```python
from google.oauth2.credentials import Credentials
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# Assume 'user_token' is obtained via an external OAuth flow
credentials = Credentials(token=user_token)

# Configure the toolset
credentials_config = DataAgentCredentialsConfig(credentials=credentials)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### External Auth Providers

If you are integrating with an external authentication provider where the token is managed by the platform, such as Gemini Enterprise, use `external_access_token_key`.

```python
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# The key used to look up the access token in the session state
credentials_config = DataAgentCredentialsConfig(
    external_access_token_key="YOUR_AUTH_ID"
)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### Interactive Auth (ADK Web)

When using the `adk web` interface for interactive sessions, you can provide OAuth 2.0 client credentials to trigger a login flow. This mechanism works for both local development and when your ADK agent is deployed to environments like Cloud Run.

```python
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# Provide OAuth 2.0 Client ID and Secret
credentials_config = DataAgentCredentialsConfig(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

## Configuration

You can customize tool behavior using [`DataAgentToolConfig`](../api-reference/python/google-adk.html#google.adk.tools.data_agent.DataAgentToolConfig):

* **`max_query_result_rows`** (`int`, default: `50`): Maximum number of rows that `ask_data_agent` returns for each data result.
* **`location`** (`str | None`, default: `None`): The default Google Cloud location (for example, `global`, `us`, or `eu`), used to select the API endpoint. Tools that take a `location` argument use this value when the argument is not set, falling back to `global`. Other tools use the location from the data agent's resource name, except `ask_data_agent`, which uses this value if set.
* **`api_endpoint`** (`str | None`, default: `None`): Optional custom API endpoint for Conversational Analytics API requests. If provided, this overrides the default or location-derived API endpoint.
* **`enable_data_agent_modification`** (`bool`, default: `False`): When `True`, the toolset also includes `create_data_agent`, `update_data_agent`, and `delete_data_agent`. When `False`, the toolset is read-only.
* **`data_agent_modification_timeout_seconds`** (`int`, default: `60`): Total timeout in seconds when polling long-running create, update, or delete operations. Must be greater than `0`.
* **`data_agent_modification_poll_interval_seconds`** (`int`, default: `2`): Poll interval in seconds while waiting for a create, update, or delete operation to complete. Must be greater than `0`.

!!! warning "Use with caution"

    Setting `enable_data_agent_modification=True` allows the agent to create, update, and delete data agents in your Google Cloud project. Ensure that the credentials used by the toolset are restricted to authorized projects with the minimum necessary IAM permissions. You can also pass `tool_filter` to `DataAgentToolset` to expose only specific tools (for example, excluding `delete_data_agent`).

```python
import google.auth
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig
from google.adk.tools.data_agent.config import DataAgentToolConfig

credentials, _ = google.auth.default()
credentials_config = DataAgentCredentialsConfig(credentials=credentials)

tool_config = DataAgentToolConfig(
    max_query_result_rows=100,
    enable_data_agent_modification=True,
    data_agent_modification_timeout_seconds=120,
)
data_agent_toolset = DataAgentToolset(
    credentials_config=credentials_config,
    data_agent_tool_config=tool_config,
)
```

## Sample Code

The following sample code demonstrates how to use the `DataAgentToolset` in an ADK agent using Application Default Credentials (ADC).

```py
--8<-- "examples/python/snippets/tools/built-in-tools/data_agent.py"
```

Note: If you want to query BigQuery tables and datasets directly as a tool, see [BigQuery tool for ADK](bigquery.md).
