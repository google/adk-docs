# BigQuery Agent Analytics plugin for ADK

Supported in ADKPython v1.21.0

Version Requirement

Use ADK Python version 1.26.0 or higher to make full use of the features described in this document, including auto-schema-upgrade, tool provenance tracking, and HITL event tracing.

The BigQuery Agent Analytics Plugin significantly enhances the Agent Development Kit (ADK) by providing a robust solution for in-depth agent behavior analysis. Using the ADK Plugin architecture and the **BigQuery Storage Write API**, it captures and logs critical operational events directly into a Google BigQuery table, empowering you with advanced capabilities for debugging, real-time monitoring, and comprehensive offline performance evaluation.

Version 1.26.0 adds **Auto Schema Upgrade** (safely add new columns to existing tables), **Tool Provenance** tracking (LOCAL, MCP, SUB_AGENT, A2A, TRANSFER_AGENT, TRANSFER_A2A), and **HITL Event Tracing** for human-in-the-loop interactions. Version 1.27.0 adds **Automatic View Creation** (generate flat, query-friendly event views).

BigQuery Storage Write API

This feature uses **BigQuery Storage Write API**, which is a paid service. For information on costs, see the [BigQuery documentation](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing).

## Use cases

- **Agent workflow debugging and analysis:** Capture a wide range of *plugin lifecycle events* (LLM calls, tool usage) and *agent-yielded events* (user input, model responses), into a well-defined schema.
- **High-volume analysis and debugging:** Logging operations are performed asynchronously using the Storage Write API to allow high throughput and low latency.
- **Multimodal Analysis**: Log and analyze text, images, and other modalities. Large files are offloaded to GCS, making them accessible to BigQuery ML via Object Tables.
- **Distributed Tracing**: Built-in support for OpenTelemetry-style tracing (`trace_id`, `span_id`) to visualize agent execution flows.
- **Tool Provenance**: Track the origin of each tool call (local function, MCP server, sub-agent, A2A remote agent, or transfer agent).
- **Human-in-the-Loop (HITL) Tracing**: Dedicated event types for credential requests, confirmation prompts, and user input requests.
- **Queryable Event Views**: Automatically create flat, per-event-type BigQuery views (e.g., `v_llm_request`, `v_tool_completed`) to simplify downstream analytics by unnesting JSON payload data.

The agent event data recorded varies based on the ADK event type. For more information, see [Event types and payloads](#event-types).

## Prerequisites

- **Google Cloud Project** with the **BigQuery API** enabled.
- **BigQuery Dataset:** Create a dataset to store logging tables before using the plugin. The plugin automatically creates the necessary events table within the dataset if the table does not exist.
- **Google Cloud Storage Bucket (Optional):** If you plan to log multimodal content (images, audio, etc.), creating a GCS bucket is recommended for offloading large files.
- **Authentication:**
  - **Local:** Run `gcloud auth application-default login`.
  - **Cloud:** Ensure your service account has the required permissions.

Note: Gemini model selector `gemini-flash-latest`

Most code examples in ADK documentation use `gemini-flash-latest` to select the [latest available](https://ai.google.dev/gemini-api/docs/models#latest) Gemini Flash version. However, if you access Gemini from a regional endpoint, such as `us-central1`, this selection string may not work. In that case, use a specific model version string from the [Gemini models](https://ai.google.dev/gemini-api/docs/models) page or Google Cloud [Gemini models](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models) list.

### IAM permissions

For the agent to work properly, the principal (e.g., service account, user account) under which the agent is running needs these Google Cloud roles: * `roles/bigquery.jobUser` at Project Level to run BigQuery queries. * `roles/bigquery.dataEditor` at Table Level to write log/event data. * **If using GCS offloading:** `roles/storage.objectCreator` and `roles/storage.objectViewer` on the target bucket.

## Use with agent

You use the BigQuery Agent Analytics Plugin by configuring and registering it with your ADK agent's App object. The following example shows an implementation of an agent with this plugin, including GCS offloading:

my_bq_agent/agent.py

```python
# my_bq_agent/agent.py
import os
import google.auth
from google.adk.apps import App
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin, BigQueryLoggerConfig
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig


# --- OpenTelemetry TracerProvider Setup (Optional) ---
# ADK includes OpenTelemetry as a core dependency.
# Configuring a TracerProvider enables full distributed tracing
# (populates trace_id, span_id with standard OTel identifiers).
# If no TracerProvider is configured, the plugin falls back to internal
# UUIDs for span correlation while still preserving the parent-child hierarchy.
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
trace.set_tracer_provider(TracerProvider())

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BIG_QUERY_DATASET_ID", "your-big-query-dataset-id")
# GOOGLE_CLOUD_LOCATION must be a valid Agent Platform region (e.g., "us-central1").
# BQ_LOCATION is the BigQuery dataset location, which can be a multi-region
# like "US" or "EU", or a single region like "us-central1".
VERTEX_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
BQ_LOCATION = os.environ.get("BQ_LOCATION", "US")
GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME", "your-gcs-bucket-name") # Optional

if PROJECT_ID == "your-gcp-project-id":
    raise ValueError("Please set GOOGLE_CLOUD_PROJECT or update the code.")

# --- CRITICAL: Set environment variables BEFORE Gemini instantiation ---
os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = VERTEX_LOCATION
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

# --- Initialize the Plugin with Config ---
bq_config = BigQueryLoggerConfig(
    enabled=True,
    gcs_bucket_name=GCS_BUCKET, # Enable GCS offloading for multimodal content
    log_multi_modal_content=True,
    max_content_length=500 * 1024, # 500 KB limit for inline text
    batch_size=1, # Default is 1 for low latency, increase for high throughput
    shutdown_timeout=10.0
)

bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id=DATASET_ID,
    table_id="agent_events", # default table name is agent_events
    config=bq_config,
    location=BQ_LOCATION
)

# --- Initialize Tools and Model ---
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials)
)

llm = Gemini(model="gemini-flash-latest")

root_agent = Agent(
    model=llm,
    name='my_bq_agent',
    instruction="You are a helpful assistant with access to BigQuery tools.",
    tools=[bigquery_toolset]
)

# --- Create the App ---
app = App(
    name="my_bq_agent",
    root_agent=root_agent,
    plugins=[bq_logging_plugin],
)
```

### Run and test agent

Test the plugin by running the agent and making a few requests through the chat interface, such as "tell me what you can do" or "List datasets in my cloud project ". These actions create events which are recorded in your Google Cloud project BigQuery instance. Once these events have been processed, you can view the data for them in the [BigQuery Console](https://console.cloud.google.com/bigquery), using this query

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

## Deploy to Agent Runtime with the plugin

You can deploy an agent with the BigQuery Agent Analytics plugin to [Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview). This section walks through the steps to deploy using the ADK CLI, and alternatively using the Agent Platform SDK programmatically.

Version Requirement

Use ADK Python version **1.24.0 or higher** to deploy with this plugin to Agent Runtime. Earlier versions had an issue where the plugin's asynchronous log writer could be terminated by the serverless runtime before flushing pending events. Starting from 1.24.0, the plugin performs a synchronous flush at the end of each invocation to ensure all events are written.

### Prerequisites

Before deploying, ensure you have completed the general [Agent Runtime setup](/deploy/agent-runtime/deploy/#setup-cloud-project), including:

1. A Google Cloud project with the **Agent Platform API** and **Cloud Resource Manager API** enabled.
1. A **BigQuery dataset** in the target project (or a cross-project dataset with the correct permissions).
1. A **Cloud Storage staging bucket** for deployment artifacts.
1. The deploying service account has the IAM roles listed in [IAM permissions](#iam-permissions).
1. Your coding environment is [authenticated](/deploy/agent-runtime/deploy/#prerequisites-coding-env) with `gcloud auth login` and `gcloud auth application-default login`.

### Step 1: Define the agent and plugin

Create your agent project folder with an `App` object that includes the plugin. The `App` object is required for Agent Runtime deployments with plugins.

```text
my_bq_agent/
├── __init__.py
├── agent.py
└── requirements.txt
```

my_bq_agent/__init__.py

```python
from . import agent
```

my_bq_agent/agent.py

```python
import os
import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models.google_llm import Gemini
from google.adk.plugins.bigquery_agent_analytics_plugin import (
    BigQueryAgentAnalyticsPlugin,
    BigQueryLoggerConfig,
)
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BQ_DATASET", "agent_analytics")
# BQ_LOCATION is the BigQuery dataset location (multi-region "US"/"EU" or
# a single region like "us-central1"). This is separate from the Agent Platform
# region used by GOOGLE_CLOUD_LOCATION.
BQ_LOCATION = os.environ.get("BQ_LOCATION", "US")

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# --- Plugin ---
bq_analytics_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id=DATASET_ID,
    location=BQ_LOCATION,
    config=BigQueryLoggerConfig(
        batch_size=1,
        batch_flush_interval=0.5,
        log_session_metadata=True,
    ),
)

# --- Tools ---
credentials, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials)
)

# --- Agent ---
root_agent = Agent(
    model=Gemini(model="gemini-flash-latest"),
    name="my_bq_agent",
    instruction="You are a helpful assistant with access to BigQuery tools.",
    tools=[bigquery_toolset],
)

# --- App (required for Agent Runtime with plugins) ---
app = App(
    name="my_bq_agent",
    root_agent=root_agent,
    plugins=[bq_analytics_plugin],
)
```

my_bq_agent/requirements.txt

```text
google-adk[bigquery]
google-cloud-bigquery-storage
pyarrow
opentelemetry-api
opentelemetry-sdk
```

### Step 2: Deploy using ADK CLI

Use the `adk deploy agent_engine` command to deploy the agent. The `--adk_app` flag tells the CLI which `App` object to use:

```shell
PROJECT_ID=your-gcp-project-id
LOCATION=us-central1

adk deploy agent_engine \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --staging_bucket=gs://your-staging-bucket \
    --display_name="My BQ Analytics Agent" \
    --adk_app=agent.app \
    my_bq_agent
```

`--adk_app` flag

The `--adk_app` flag specifies the module path and variable name of the `App` object (in the format `module.variable`). In this example, `agent.app` refers to the `app` variable in `agent.py`. This ensures the deployment correctly picks up the plugin configuration.

Once successfully deployed, you should see output like:

```shell
AgentEngine created. Resource name: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944
```

Note the **Resource name** for the next step.

### Step 3: Test the deployed agent

After deployment, you can query the agent using the Agent Platform SDK:

test_deployed_agent.py

```python
import uuid
import vertexai

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
AGENT_ID = "751619551677906944"  # from deployment output

vertexai.init(project=PROJECT_ID, location=LOCATION)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

agent = client.agent_engines.get(
    name=f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ID}"
)

user_id = f"test_user_{uuid.uuid4().hex[:8]}"
for chunk in agent.stream_query(
    message="List datasets in my project", user_id=user_id
):
    print(chunk, end="", flush=True)
```

### Step 4: Verify events in BigQuery

After sending a few queries to the deployed agent, verify that events are being logged by querying your BigQuery table:

```sql
SELECT timestamp, event_type, agent, content
FROM `your-gcp-project-id.agent_analytics.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

You should see events such as `INVOCATION_STARTING`, `LLM_REQUEST`, `LLM_RESPONSE`, `TOOL_STARTING`, `TOOL_COMPLETED`, and `INVOCATION_COMPLETED`.

### Alternative: Deploy using the Agent Platform SDK

You can also deploy programmatically using the Agent Platform SDK directly. This is useful for CI/CD pipelines or custom deployment workflows:

deploy.py

```python
import vertexai
from vertexai import agent_engines
from my_bq_agent.agent import app

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://your-staging-bucket"

vertexai.init(
    project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET
)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

remote_app = client.agent_engines.create(
    agent=app,
    config={
        "display_name": "My BQ Analytics Agent",
        "staging_bucket": STAGING_BUCKET,
        "requirements": [
            "google-adk[bigquery]",
            "google-cloud-aiplatform[agent_engines]",
            "google-cloud-bigquery-storage",
            "pyarrow",
            "opentelemetry-api",
            "opentelemetry-sdk",
        ],
    },
)
print(f"Deployed agent: {remote_app.api_resource.name}")
```

### Troubleshooting

If events are not appearing in your BigQuery table after deployment:

1. **Check ADK version**: Ensure `google-adk>=1.24.0` is in your requirements. Earlier versions do not flush pending events before the serverless runtime suspends the process.

1. **Enable debug logging**: Add the following to the top of your `agent.py` to surface any silent errors:

   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logging.getLogger("google_adk").setLevel(logging.DEBUG)
   ```

1. **Check IAM permissions**: The Agent Runtime service account needs `roles/bigquery.dataEditor` on the target table and `roles/bigquery.jobUser` on the project. For **cross-project** logging, also ensure the BigQuery API is enabled in the source project and the service account has `bigquery.tables.updateData` on the destination table.

1. **Verify plugin initialization**: In Cloud Logging, filter by `resource.type="reasoning_engine"` and look for plugin startup messages or error logs.

1. **Use immediate flush for debugging**: Set `batch_size=1` and `batch_flush_interval=0.1` in `BigQueryLoggerConfig` to rule out buffering issues.

## Tracing and Observability

The plugin supports **OpenTelemetry** for distributed tracing. OpenTelemetry is included as a core dependency of ADK and is always available.

- **Automatic Span Management**: The plugin automatically generates spans for Agent execution, LLM calls, and Tool executions.
- **OpenTelemetry Integration**: If a `TracerProvider` is configured (as shown in the example above), the plugin will use valid OTel spans, populating `trace_id`, `span_id`, and `parent_span_id` with standard OTel identifiers. This allows you to correlate agent logs with other services in your distributed system.
- **Fallback Mechanism**: If no `TracerProvider` is configured (i.e., only the default no-op provider is active), the plugin automatically falls back to generating internal UUIDs for spans and uses the `invocation_id` as the trace ID. This ensures that the parent-child hierarchy (Agent -> Span -> Tool/LLM) is *always* preserved in the BigQuery logs, even without a configured `TracerProvider`.

## Configuration options

The `BigQueryAgentAnalyticsPlugin` constructor accepts the following parameters:

- **`project_id`** (`str`): The Google Cloud project ID.
- **`dataset_id`** (`str`): The BigQuery dataset ID.
- **`table_id`** (`Optional[str]`, default: `None`): The BigQuery table ID. Overrides `table_id` in `BigQueryLoggerConfig` if both are set.
- **`config`** (`Optional[BigQueryLoggerConfig]`, default: `None`): A `BigQueryLoggerConfig` instance for detailed configuration.
- **`location`** (`str`, default: `"US"`): The BigQuery dataset location (e.g., `"US"`, `"EU"`, `"us-central1"`).
- **`credentials`** (`Optional[google.auth.credentials.Credentials]`, default: `None`): Explicit Google credentials for the plugin's BigQuery and GCS clients. If `None`, the plugin uses [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials). Use this for service-account, impersonated, or cross-project setups.

The constructor also accepts `**kwargs`, which are forwarded directly to `BigQueryLoggerConfig`. This lets you pass config fields (like `batch_size` or `enabled`) without creating a separate config object:

```python
plugin = BigQueryAgentAnalyticsPlugin(
    project_id="my-project",
    dataset_id="my_dataset",
    batch_size=10,           # forwarded to BigQueryLoggerConfig
    shutdown_timeout=5.0,    # forwarded to BigQueryLoggerConfig
)
```

- **`enabled`** (`bool`, default: `True`): To disable the plugin from logging agent data to the BigQuery table, set this parameter to False.
- **`table_id`** (`str`, default: `"agent_events"`): The BigQuery table ID within the dataset. Can also be overridden by the `table_id` parameter on the `BigQueryAgentAnalyticsPlugin` constructor, which takes precedence.
- **`clustering_fields`** (`List[str]`, default: `["event_type", "agent", "user_id"]`): The fields used to cluster the BigQuery table when it is automatically created.
- **`gcs_bucket_name`** (`Optional[str]`, default: `None`): The name of the GCS bucket to offload large content (images, blobs, large text) to. If not provided, large content may be truncated or replaced with placeholders.
- **`connection_id`** (`Optional[str]`, default: `None`): The BigQuery connection ID (e.g., `us.my-connection`) to use as the authorizer for `ObjectRef` columns. Required for using `ObjectRef` with BigQuery ML.
- **`max_content_length`** (`int`, default: `500 * 1024`): The maximum length (in characters) of text content to store **inline** in BigQuery before offloading to GCS (if configured) or truncating. Default is 500 KB.
- **`batch_size`** (`int`, default: `1`): The number of events to batch before writing to BigQuery.
- **`batch_flush_interval`** (`float`, default: `1.0`): The maximum time (in seconds) to wait before flushing a partial batch.
- **`shutdown_timeout`** (`float`, default: `10.0`): Seconds to wait for logs to flush during shutdown.
- **`event_allowlist`** (`Optional[List[str]]`, default: `None`): A list of event types to log. If `None`, all events are logged except those in `event_denylist`. For a comprehensive list of supported event types, refer to the [Event types and payloads](#event-types) section.
- **`event_denylist`** (`Optional[List[str]]`, default: `None`): A list of event types to skip logging. For a comprehensive list of supported event types, refer to the [Event types and payloads](#event-types) section.
- **`content_formatter`** (`Optional[Callable[[Any, str], Any]]`, default: `None`): An optional function to format event content before logging. The function receives two arguments: the raw content and the event type string (e.g., `"LLM_REQUEST"`).
- **`log_multi_modal_content`** (`bool`, default: `True`): Whether to log detailed content parts (including GCS references).
- **`queue_max_size`** (`int`, default: `10000`): The maximum number of events to hold in the in-memory queue before dropping new events.
- **`retry_config`** (`RetryConfig`, default: `RetryConfig()`): Configuration for retrying failed BigQuery writes. Sub-fields: `max_retries` (default `3`), `initial_delay` (default `1.0` seconds), `multiplier` (default `2.0`), `max_delay` (default `10.0` seconds).
- **`log_session_metadata`** (`bool`, default: `True`): If True, logs session information into the `attributes` column, including `session_id`, `app_name`, `user_id`, and the session `state` dictionary (e.g., custom state like gchat thread-id, customer_id). State keys prefixed with `temp:` or `secret:` are automatically redacted. See [Built-in redaction](#built-in-redaction).
- **`custom_tags`** (`Dict[str, Any]`, default: `{}`): A dictionary of static tags (e.g., `{"env": "prod", "version": "1.0"}`) to be included in the `attributes` column for every event.
- **`auto_schema_upgrade`** (`bool`, default: `True`): When enabled, the plugin automatically adds new columns to an existing table when the plugin schema evolves. Only additive changes are made (columns are never dropped or altered). A version label (`adk_schema_version`) on the table ensures the diff runs at most once per schema version. Safe to leave enabled.
- **`create_views`** (`bool`, default: `True`): Added in 1.27.0. When enabled, automatically generates per-event-type BigQuery views that unnest structured JSON data (such as `content` or `attributes`) into flat, typed columns, significantly simplifying SQL queries.
- **`view_prefix`** (`str`, default: `"v"`): Prefix for auto-created view names. The default `"v"` produces views like `v_llm_request`. Set a distinct prefix per table when multiple plugin instances share the same dataset to avoid view-name collisions (e.g., `"v_staging"` produces `v_staging_llm_request`). Must be non-empty.

The following code sample shows how to define a configuration for the BigQuery Agent Analytics plugin:

```python
import json
import re

from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryLoggerConfig

def redact_dollar_amounts(event_content: Any, event_type: str) -> str:
    """
    Custom formatter to redact dollar amounts (e.g., $600, $12.50)
    and ensure JSON output if the input is a dict.

    Args:
        event_content: The raw content of the event.
        event_type: The event type string (e.g., "LLM_REQUEST", "LLM_RESPONSE").
    """
    text_content = ""
    if isinstance(event_content, dict):
        text_content = json.dumps(event_content)
    else:
        text_content = str(event_content)

    # Regex to find dollar amounts: $ followed by digits, optionally with commas or decimals.
    # Examples: $600, $1,200.50, $0.99
    redacted_content = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d+)?', 'xxx', text_content)

    return redacted_content

config = BigQueryLoggerConfig(
    enabled=True,
    event_allowlist=["LLM_REQUEST", "LLM_RESPONSE"], # Only log these events
    # event_denylist=["TOOL_STARTING"], # Skip these events
    shutdown_timeout=10.0, # Wait up to 10s for logs to flush on exit
    max_content_length=500, # Truncate content to 500 chars
    content_formatter=redact_dollar_amounts, # Redact the dollar amounts in the logging content
    queue_max_size=10000, # Max events to hold in memory
    auto_schema_upgrade=True, # Automatically add new columns to existing tables
    create_views=True, # Automatically create per-event-type views
    # retry_config=RetryConfig(max_retries=3), # Optional: Configure retries
)

plugin = BigQueryAgentAnalyticsPlugin(..., config=config)
```

### Public methods

The plugin exposes several public methods for lifecycle management:

- **`await plugin.flush()`**: Flush all pending events to BigQuery. Call this before shutdown to avoid data loss.

- **`await plugin.shutdown(timeout=None)`**: Gracefully shut down the plugin, flushing pending events and releasing resources. The optional `timeout` parameter overrides `shutdown_timeout` from the config.

- **`await plugin.create_analytics_views()`**: Manually (re-)create all per-event-type analytics views. Useful after a schema upgrade or when views need to be refreshed.

- **Async context manager**: The plugin supports `async with` for automatic startup and shutdown:

  ```python
  async with BigQueryAgentAnalyticsPlugin(
      project_id=PROJECT_ID, dataset_id=DATASET_ID
  ) as plugin:
      # plugin is initialized and ready to use
      ...
  # plugin.shutdown() is called automatically on exit
  ```

## Schema and production setup

### Schema Reference

The events table (`agent_events`) uses a flexible schema. The following table provides a comprehensive reference with example values.

| Field Name         | Type        | Mode       | Description                                                                                                                                                                                                                                                                                                                                                      | Example Value                                                                                                                                                                                                |
| ------------------ | ----------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **timestamp**      | `TIMESTAMP` | `REQUIRED` | UTC timestamp of event creation. Acts as the primary ordering key and the daily partitioning key. Precision is microsecond.                                                                                                                                                                                                                                      | `2026-02-03 20:52:17 UTC`                                                                                                                                                                                    |
| **event_type**     | `STRING`    | `NULLABLE` | The canonical event category. Standard values include `LLM_REQUEST`, `LLM_RESPONSE`, `LLM_ERROR`, `TOOL_STARTING`, `TOOL_COMPLETED`, `TOOL_ERROR`, `AGENT_STARTING`, `AGENT_COMPLETED`, `STATE_DELTA`, `INVOCATION_STARTING`, `INVOCATION_COMPLETED`, `USER_MESSAGE_RECEIVED`, and HITL events (see [HITL events](#hitl-events)). Used for high-level filtering. | `LLM_REQUEST`                                                                                                                                                                                                |
| **agent**          | `STRING`    | `NULLABLE` | The name of the agent responsible for this event. Defined during agent initialization or via the `root_agent_name` context.                                                                                                                                                                                                                                      | `my_bq_agent`                                                                                                                                                                                                |
| **session_id**     | `STRING`    | `NULLABLE` | A persistent identifier for the entire conversation thread. Stays constant across multiple turns and sub-agent calls.                                                                                                                                                                                                                                            | `04275a01-1649-4a30-b6a7-5b443c69a7bc`                                                                                                                                                                       |
| **invocation_id**  | `STRING`    | `NULLABLE` | The unique identifier for a single execution turn or request cycle. Corresponds to `trace_id` in many contexts.                                                                                                                                                                                                                                                  | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40`                                                                                                                                                                     |
| **user_id**        | `STRING`    | `NULLABLE` | The identifier of the user (human or system) initiating the session. Extracted from the `User` object or metadata.                                                                                                                                                                                                                                               | `test_user`                                                                                                                                                                                                  |
| **trace_id**       | `STRING`    | `NULLABLE` | The **OpenTelemetry** Trace ID (32-char hex). Links all operations within a single distributed request lifecycle.                                                                                                                                                                                                                                                | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40`                                                                                                                                                                     |
| **span_id**        | `STRING`    | `NULLABLE` | The **OpenTelemetry** Span ID (16-char hex). Uniquely identifies this specific atomic operation.                                                                                                                                                                                                                                                                 | `69867a836cd94798be2759d8e0d70215`                                                                                                                                                                           |
| **parent_span_id** | `STRING`    | `NULLABLE` | The Span ID of the immediate caller. Used to reconstruct the parent-child execution tree (DAG).                                                                                                                                                                                                                                                                  | `ef5843fe40764b4b8afec44e78044205`                                                                                                                                                                           |
| **content**        | `JSON`      | `NULLABLE` | The primary event payload. Structure is polymorphic based on `event_type`.                                                                                                                                                                                                                                                                                       | `{"system_prompt": "You are...", "prompt": [{"role": "user", "content": "hello"}], "response": "Hi", "usage": {"total": 15}}`                                                                                |
| **attributes**     | `JSON`      | `NULLABLE` | Metadata/Enrichment (usage stats, model info, tool provenance, custom tags).                                                                                                                                                                                                                                                                                     | `{"model": "gemini-flash-latest", "usage_metadata": {"total_token_count": 15}, "session_metadata": {"session_id": "...", "app_name": "...", "user_id": "...", "state": {}}, "custom_tags": {"env": "prod"}}` |
| **latency_ms**     | `JSON`      | `NULLABLE` | Performance metrics. Standard keys are `total_ms` (wall-clock duration) and `time_to_first_token_ms` (streaming latency).                                                                                                                                                                                                                                        | `{"total_ms": 1250, "time_to_first_token_ms": 450}`                                                                                                                                                          |
| **status**         | `STRING`    | `NULLABLE` | High-level outcome. Values: `OK` (success) or `ERROR` (failure).                                                                                                                                                                                                                                                                                                 | `OK`                                                                                                                                                                                                         |
| **error_message**  | `STRING`    | `NULLABLE` | Human-readable exception message or stack trace fragment. Populated only when `status` is `ERROR`.                                                                                                                                                                                                                                                               | `Error 404: Dataset not found`                                                                                                                                                                               |
| **is_truncated**   | `BOOLEAN`   | `NULLABLE` | `true` if `content` or `attributes` exceeded the BigQuery cell size limit (default 10MB) and were partially dropped.                                                                                                                                                                                                                                             | `false`                                                                                                                                                                                                      |
| **content_parts**  | `RECORD`    | `REPEATED` | Array of multi-modal segments (Text, Image, Blob). Used when content cannot be serialized as simple JSON (e.g., large binaries or GCS refs).                                                                                                                                                                                                                     | `[{"mime_type": "text/plain", "text": "hello"}]`                                                                                                                                                             |

The plugin automatically creates the table if it does not exist. However, for production, we recommend creating the table manually using the following DDL, which utilizes the **JSON** type for flexibility and **REPEATED RECORD**s for multimodal content.

**Recommended DDL:**

```sql
CREATE TABLE `your-gcp-project-id.adk_agent_logs.agent_events`
(
  timestamp TIMESTAMP NOT NULL OPTIONS(description="The UTC time at which the event was logged."),
  event_type STRING OPTIONS(description="Indicates the type of event being logged (e.g., 'LLM_REQUEST', 'TOOL_COMPLETED')."),
  agent STRING OPTIONS(description="The name of the ADK agent or author associated with the event."),
  session_id STRING OPTIONS(description="A unique identifier to group events within a single conversation or user session."),
  invocation_id STRING OPTIONS(description="A unique identifier for each individual agent execution or turn within a session."),
  user_id STRING OPTIONS(description="The identifier of the user associated with the current session."),
  trace_id STRING OPTIONS(description="OpenTelemetry trace ID for distributed tracing."),
  span_id STRING OPTIONS(description="OpenTelemetry span ID for this specific operation."),
  parent_span_id STRING OPTIONS(description="OpenTelemetry parent span ID to reconstruct hierarchy."),
  content JSON OPTIONS(description="The event-specific data (payload) stored as JSON."),
  content_parts ARRAY<STRUCT<
    mime_type STRING,
    uri STRING,
    object_ref STRUCT<
      uri STRING,
      version STRING,
      authorizer STRING,
      details JSON
    >,
    text STRING,
    part_index INT64,
    part_attributes STRING,
    storage_mode STRING
  >> OPTIONS(description="Detailed content parts for multi-modal data."),
  attributes JSON OPTIONS(description="Arbitrary key-value pairs for additional metadata (e.g., 'root_agent_name', 'model_version', 'usage_metadata', 'session_metadata', 'custom_tags')."),
  latency_ms JSON OPTIONS(description="Latency measurements (e.g., total_ms)."),
  status STRING OPTIONS(description="The outcome of the event, typically 'OK' or 'ERROR'."),
  error_message STRING OPTIONS(description="Populated if an error occurs."),
  is_truncated BOOLEAN OPTIONS(description="Flag indicates if content was truncated.")
)
PARTITION BY DATE(timestamp)
CLUSTER BY event_type, agent, user_id;
```

### Automatically Created Views (1.27.0+)

When `create_views=True` (the default in 1.27.0 and higher), the plugin automatically generates views for each event type that unnest common JSON structures into flat, typed columns. This significantly simplifies SQL, eliminating the need to write complex `JSON_VALUE` or `JSON_QUERY` functions explicitly.

View names follow the convention `{view_prefix}_{event_type_lowercase}` (for example, with the default prefix `"v"`, `LLM_REQUEST` becomes `v_llm_request`). Set `view_prefix` in `BigQueryLoggerConfig` to a distinct value when multiple plugin instances write to different tables in the same dataset, preventing view-name collisions:

```python
# Two plugins in the same dataset with distinct view prefixes
plugin_prod = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_prod",
    config=BigQueryLoggerConfig(view_prefix="v_prod"),
)
# Creates views: v_prod_llm_request, v_prod_tool_completed, ...

plugin_staging = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_staging",
    config=BigQueryLoggerConfig(view_prefix="v_staging"),
)
# Creates views: v_staging_llm_request, v_staging_tool_completed, ...
```

You can also call the public async method `await plugin.create_analytics_views()` to manually refresh views, for example after a schema upgrade.

Every view includes these **common columns**: `timestamp`, `event_type`, `agent`, `session_id`, `invocation_id`, `user_id`, `trace_id`, `span_id`, `parent_span_id`, `status`, `error_message`, `is_truncated`.

The following table lists all 16 auto-created views and their event-specific columns:

| View Name                         | Event-Specific Columns                                                                                                                                                                                                                                                                                  |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`v_user_message_received`**     | *(common columns only)*                                                                                                                                                                                                                                                                                 |
| **`v_llm_request`**               | `model` (STRING), `request_content` (JSON), `llm_config` (JSON), `tools` (JSON)                                                                                                                                                                                                                         |
| **`v_llm_response`**              | `response` (JSON), `usage_prompt_tokens` (INT64), `usage_completion_tokens` (INT64), `usage_total_tokens` (INT64), `usage_cached_tokens` (INT64), `total_ms` (INT64), `ttft_ms` (INT64), `model_version` (STRING), `usage_metadata` (JSON), `cache_metadata` (JSON), `context_cache_hit_rate` (FLOAT64) |
| **`v_llm_error`**                 | `total_ms` (INT64)                                                                                                                                                                                                                                                                                      |
| **`v_tool_starting`**             | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING)                                                                                                                                                                                                                                        |
| **`v_tool_completed`**            | `tool_name` (STRING), `tool_result` (JSON), `tool_origin` (STRING), `total_ms` (INT64)                                                                                                                                                                                                                  |
| **`v_tool_error`**                | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING), `total_ms` (INT64)                                                                                                                                                                                                                    |
| **`v_agent_starting`**            | `agent_instruction` (STRING)                                                                                                                                                                                                                                                                            |
| **`v_agent_completed`**           | `total_ms` (INT64)                                                                                                                                                                                                                                                                                      |
| **`v_invocation_starting`**       | *(common columns only)*                                                                                                                                                                                                                                                                                 |
| **`v_invocation_completed`**      | *(common columns only)*                                                                                                                                                                                                                                                                                 |
| **`v_state_delta`**               | `state_delta` (JSON)                                                                                                                                                                                                                                                                                    |
| **`v_hitl_credential_request`**   | `tool_name` (STRING), `tool_args` (JSON)                                                                                                                                                                                                                                                                |
| **`v_hitl_confirmation_request`** | `tool_name` (STRING), `tool_args` (JSON)                                                                                                                                                                                                                                                                |
| **`v_hitl_input_request`**        | `tool_name` (STRING), `tool_args` (JSON)                                                                                                                                                                                                                                                                |
| **`v_a2a_interaction`**           | `response_content` (JSON), `a2a_task_id` (STRING), `a2a_context_id` (STRING), `a2a_request` (JSON), `a2a_response` (JSON)                                                                                                                                                                               |

### Event types and payloads

The `content` column now contains a **JSON** object specific to the `event_type`. The `content_parts` column provides a structured view of the content, especially useful for images or offloaded data.

Content Truncation

- Variable content fields are truncated to `max_content_length` (configured in `BigQueryLoggerConfig`, default 500KB).
- If `gcs_bucket_name` is configured, large content is offloaded to GCS instead of being truncated, and a reference is stored in `content_parts.object_ref`.

#### LLM interactions (plugin lifecycle)

These events track the raw requests sent to and responses received from the LLM.

**1. LLM_REQUEST**

Captures the prompt sent to the model, including conversation history and system instructions.

```json
{
  "event_type": "LLM_REQUEST",
  "content": {
    "system_prompt": "You are a helpful assistant...",
    "prompt": [
      {
        "role": "user",
        "content": "hello how are you today"
      }
    ]
  },
  "attributes": {
    "root_agent_name": "my_bq_agent",
    "model": "gemini-flash-latest",
    "tools": ["list_dataset_ids", "execute_sql"],
    "llm_config": {
      "temperature": 0.5,
      "top_p": 0.9
    }
  }
}
```

**2. LLM_RESPONSE**

Captures the model's output and token usage statistics.

```json
{
  "event_type": "LLM_RESPONSE",
  "content": {
    "response": "text: 'Hello! I'm doing well...'",
    "usage": {
      "completion": 19,
      "prompt": 10129,
      "total": 10148
    }
  },
  "attributes": {
    "root_agent_name": "my_bq_agent",
    "model_version": "gemini-flash-latest",
    "usage_metadata": {
      "prompt_token_count": 10129,
      "candidates_token_count": 19,
      "total_token_count": 10148
    }
  },
  "latency_ms": {
    "time_to_first_token_ms": 2579,
    "total_ms": 2579
  }
}
```

**3. LLM_ERROR**

Logged when an LLM call fails with an exception. The error message is captured and the span is closed.

```json
{
  "event_type": "LLM_ERROR",
  "content": null,
  "attributes": {
    "root_agent_name": "my_bq_agent"
  },
  "error_message": "Error 429: Resource exhausted",
  "latency_ms": {
    "total_ms": 350
  }
}
```

#### Tool usage (plugin lifecycle)

These events track the execution of tools by the agent. Each tool event includes a `tool_origin` field that classifies the tool's provenance:

| Tool Origin      | Description                                                                                    |
| ---------------- | ---------------------------------------------------------------------------------------------- |
| `LOCAL`          | `FunctionTool` instances (local Python functions)                                              |
| `MCP`            | Model Context Protocol tools (`McpTool` instances)                                             |
| `SUB_AGENT`      | `AgentTool` instances (sub-agents)                                                             |
| `A2A`            | Remote Agent-to-Agent instances (`RemoteA2aAgent`)                                             |
| `TRANSFER_AGENT` | `TransferToAgentTool` instances (generic agent transfer)                                       |
| `TRANSFER_A2A`   | `TransferToAgentTool` instances that transfer to a `RemoteA2aAgent` (classified at call-level) |
| `UNKNOWN`        | Unclassified tools                                                                             |

**4. TOOL_STARTING**

Logged when an agent begins executing a tool.

```json
{
  "event_type": "TOOL_STARTING",
  "content": {
    "tool": "list_dataset_ids",
    "args": {
      "project_id": "bigquery-public-data"
    },
    "tool_origin": "LOCAL"
  }
}
```

**5. TOOL_COMPLETED**

Logged when a tool execution finishes.

```json
{
  "event_type": "TOOL_COMPLETED",
  "content": {
    "tool": "list_dataset_ids",
    "result": [
      "austin_311",
      "austin_bikeshare"
    ],
    "tool_origin": "LOCAL"
  },
  "latency_ms": {
    "total_ms": 467
  }
}
```

**6. TOOL_ERROR**

Logged when a tool execution fails with an exception. Captures the tool name, arguments, tool origin, and error message.

```json
{
  "event_type": "TOOL_ERROR",
  "content": {
    "tool": "list_dataset_ids",
    "args": {
      "project_id": "nonexistent-project"
    },
    "tool_origin": "LOCAL"
  },
  "error_message": "Error 404: Dataset not found",
  "latency_ms": {
    "total_ms": 150
  }
}
```

#### State Management

These events track changes to the agent's state, typically triggered by tools.

**7. STATE_DELTA**

Tracks changes to the agent's internal state (e.g., custom application state updated by tools).

Built-in redaction

State keys prefixed with `temp:` or `secret:` are automatically redacted to `[REDACTED]` in the logged `state_delta`. See [Built-in redaction](#built-in-redaction) for details.

```json
{
  "event_type": "STATE_DELTA",
  "attributes": {
    "state_delta": {
      "customer_tier": "enterprise",
      "last_query_dataset": "bigquery-public-data.samples"
    }
  }
}
```

#### Agent lifecycle & Generic Events

| **Event Type**          | **Content (JSON) Structure**                 |
| ----------------------- | -------------------------------------------- |
| `INVOCATION_STARTING`   | `{}`                                         |
| `INVOCATION_COMPLETED`  | `{}`                                         |
| `AGENT_STARTING`        | `"You are a helpful agent..."`               |
| `AGENT_COMPLETED`       | `{}`                                         |
| `USER_MESSAGE_RECEIVED` | `{"text_summary": "Help me book a flight."}` |

#### Human-in-the-Loop (HITL) Events

The plugin automatically detects calls to ADK's synthetic HITL tools and emits dedicated event types for them. These events are logged **in addition to** the normal `TOOL_STARTING` / `TOOL_COMPLETED` events.

The following HITL tool names are recognized:

- `adk_request_credential` — Request for user credentials (e.g., OAuth tokens)
- `adk_request_confirmation` — Request for user confirmation before proceeding
- `adk_request_input` — Request for free-form user input

| **Event Type**                        | **Trigger**                            | **Content (JSON) Structure**                            |
| ------------------------------------- | -------------------------------------- | ------------------------------------------------------- |
| `HITL_CREDENTIAL_REQUEST`             | Agent calls `adk_request_credential`   | `{"tool": "adk_request_credential", "args": {...}}`     |
| `HITL_CREDENTIAL_REQUEST_COMPLETED`   | User provides credential response      | `{"tool": "adk_request_credential", "result": {...}}`   |
| `HITL_CONFIRMATION_REQUEST`           | Agent calls `adk_request_confirmation` | `{"tool": "adk_request_confirmation", "args": {...}}`   |
| `HITL_CONFIRMATION_REQUEST_COMPLETED` | User provides confirmation response    | `{"tool": "adk_request_confirmation", "result": {...}}` |
| `HITL_INPUT_REQUEST`                  | Agent calls `adk_request_input`        | `{"tool": "adk_request_input", "args": {...}}`          |
| `HITL_INPUT_REQUEST_COMPLETED`        | User provides input response           | `{"tool": "adk_request_input", "result": {...}}`        |

HITL request events are detected from `function_call` parts in `on_event_callback`. HITL completion events are detected from `function_response` parts in both `on_event_callback` and `on_user_message_callback`.

Views for HITL events

Auto-created views exist only for the three **request** event types (`v_hitl_credential_request`, `v_hitl_confirmation_request`, `v_hitl_input_request`). The three `*_COMPLETED` event types are logged to the base table but do not have dedicated views. Query them directly from the `agent_events` table using `WHERE event_type LIKE 'HITL_%_COMPLETED'`.

#### A2A Interaction Events

When your agent communicates with a remote agent via the Agent-to-Agent (A2A) protocol, the plugin logs an `A2A_INTERACTION` event capturing the request and response details.

**A2A_INTERACTION**

Logged when an A2A remote agent call completes.

```json
{
  "event_type": "A2A_INTERACTION",
  "content": {
    "response_content": "The remote agent's response...",
    "a2a_task_id": "task-abc123",
    "a2a_context_id": "ctx-def456",
    "a2a_request": { ... },
    "a2a_response": { ... }
  }
}
```

#### GCS Offloading Examples (Multimodal & Large Text)

When `gcs_bucket_name` is configured, large text and multimodal content (images, audio, etc.) are automatically offloaded to GCS. The `content` column will contain a summary or placeholder, while `content_parts` contains the `object_ref` pointing to the GCS URI.

**Offloaded Text Example**

```json
{
  "event_type": "LLM_REQUEST",
  "content_parts": [
    {
      "part_index": 1,
      "mime_type": "text/plain",
      "storage_mode": "GCS_REFERENCE",
      "text": "AAAA... [OFFLOADED]",
      "object_ref": {
        "uri": "gs://haiyuan-adk-debug-verification-1765319132/2025-12-10/e-f9545d6d/ae5235e6_p1.txt",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "text/plain"}}
      }
    }
  ]
}
```

**Offloaded Image Example**

```json
{
  "event_type": "LLM_REQUEST",
  "content_parts": [
    {
      "part_index": 2,
      "mime_type": "image/png",
      "storage_mode": "GCS_REFERENCE",
      "text": "[MEDIA OFFLOADED]",
      "object_ref": {
        "uri": "gs://haiyuan-adk-debug-verification-1765319132/2025-12-10/e-f9545d6d/ae5235e6_p2.png",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "image/png"}}
      }
    }
  ]
}
```

**Querying Offloaded Content (Get Signed URLs)**

```sql
SELECT
  timestamp,
  event_type,
  part.mime_type,
  part.storage_mode,
  part.object_ref.uri AS gcs_uri,
  -- Generate a signed URL to read the content directly (requires connection_id configuration)
  STRING(OBJ.GET_ACCESS_URL(part.object_ref, 'r').access_urls.read_url) AS signed_url
FROM `your-gcp-project-id.your-dataset-id.agent_events`,
UNNEST(content_parts) AS part
WHERE part.storage_mode = 'GCS_REFERENCE'
ORDER BY timestamp DESC
LIMIT 10;
```

## Advanced analysis queries

### Trace a specific conversation turn using trace_id

```sql
SELECT timestamp, event_type, agent, JSON_VALUE(content, '$.response') as summary
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE trace_id = 'your-trace-id'
ORDER BY timestamp ASC;
```

### Token usage analysis

Using the `v_llm_response` view (recommended):

```sql
SELECT
  AVG(usage_total_tokens) as avg_tokens,
  AVG(usage_prompt_tokens) as avg_prompt_tokens,
  AVG(usage_completion_tokens) as avg_completion_tokens
FROM `your-gcp-project-id.your-dataset-id.v_llm_response`;
```

Or using the base table with JSON extraction:

```sql
SELECT
  AVG(CAST(JSON_VALUE(content, '$.usage.total') AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'LLM_RESPONSE';
```

### Querying Multimodal Content (using content_parts and ObjectRef)

```sql
SELECT
  timestamp,
  part.mime_type,
  part.object_ref.uri as gcs_uri
FROM `your-gcp-project-id.your-dataset-id.agent_events`,
UNNEST(content_parts) as part
WHERE part.mime_type LIKE 'image/%'
ORDER BY timestamp DESC;
```

### Analyze Multimodal Content with BigQuery Remote Model (Gemini)

```sql
SELECT
  logs.session_id,
  -- Get a signed URL for the image
  STRING(OBJ.GET_ACCESS_URL(parts.object_ref, "r").access_urls.read_url) as signed_url,
  -- Analyze the image using a remote model (e.g., gemini-pro-vision)
  AI.GENERATE(
    ('Describe this image briefly. What company logo?', parts.object_ref)
  ) AS generated_result
FROM
  `your-gcp-project-id.your-dataset-id.agent_events` logs,
  UNNEST(logs.content_parts) AS parts
WHERE
  parts.mime_type LIKE 'image/%'
ORDER BY logs.timestamp DESC
LIMIT 1;
```

### Latency Analysis (LLM & Tools)

Using views (recommended):

```sql
-- LLM latency
SELECT AVG(total_ms) as avg_llm_ms, AVG(ttft_ms) as avg_ttft_ms
FROM `your-gcp-project-id.your-dataset-id.v_llm_response`;

-- Tool latency by tool name
SELECT tool_name, tool_origin, AVG(total_ms) as avg_tool_ms
FROM `your-gcp-project-id.your-dataset-id.v_tool_completed`
GROUP BY tool_name, tool_origin
ORDER BY avg_tool_ms DESC;
```

Or using the base table:

```sql
SELECT
  event_type,
  AVG(CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64)) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
GROUP BY event_type;
```

### Span Hierarchy & Duration Analysis

```sql
SELECT
  span_id,
  parent_span_id,
  event_type,
  timestamp,
  -- Extract duration from latency_ms for completed operations
  CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64) as duration_ms,
  -- Identify the specific tool or operation
  COALESCE(
    JSON_VALUE(content, '$.tool'),
    'LLM_CALL'
  ) as operation
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE trace_id = 'your-trace-id'
  AND event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
ORDER BY timestamp ASC;
```

### Error Analysis (LLM & Tool Errors)

Using views (recommended):

```sql
-- Tool errors with provenance
SELECT timestamp, agent, tool_name, tool_origin, error_message, total_ms
FROM `your-gcp-project-id.your-dataset-id.v_tool_error`
ORDER BY timestamp DESC
LIMIT 20;

-- LLM errors
SELECT timestamp, agent, error_message, total_ms
FROM `your-gcp-project-id.your-dataset-id.v_llm_error`
ORDER BY timestamp DESC
LIMIT 20;
```

### Tool Provenance Analysis

Using the `v_tool_completed` view (recommended):

```sql
SELECT
  tool_origin,
  tool_name,
  COUNT(*) as call_count,
  AVG(total_ms) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.v_tool_completed`
GROUP BY tool_origin, tool_name
ORDER BY call_count DESC;
```

### HITL Interaction Analysis

```sql
SELECT
  timestamp,
  event_type,
  session_id,
  JSON_VALUE(content, '$.tool') as hitl_tool,
  content
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type LIKE 'HITL_%'
ORDER BY timestamp DESC
LIMIT 20;
```

### AI-Powered Root Cause Analysis (Agent Ops)

Automatically analyze failed sessions to determine the root cause of errors using BigQuery ML and Gemini.

```sql
DECLARE failed_session_id STRING;
-- Find a recent failed session
SET failed_session_id = (
    SELECT session_id
    FROM `your-gcp-project-id.your-dataset-id.agent_events`
    WHERE error_message IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 1
);

-- Reconstruct the full conversation context
WITH SessionContext AS (
    SELECT
        session_id,
        STRING_AGG(CONCAT(event_type, ': ', COALESCE(TO_JSON_STRING(content), '')), '\n' ORDER BY timestamp) as full_history
    FROM `your-gcp-project-id.your-dataset-id.agent_events`
    WHERE session_id = failed_session_id
    GROUP BY session_id
)
-- Ask Gemini to diagnose the issue
SELECT
    session_id,
    AI.GENERATE(
        ('Analyze this conversation log and explain the root cause of the failure. Log: ', full_history),
        endpoint => 'gemini-flash-latest'
    ).result AS root_cause_explanation
FROM SessionContext;
```

## Conversational Analytics in BigQuery

You can also use [BigQuery Conversational Analytics](https://cloud.google.com/bigquery/docs/conversational-analytics) to analyze your agent logs using natural language. Use this tool to answer questions like:

- "Show me the error rate over time"
- "What are the most common tool calls?"
- "Identify sessions with high token usage"

## Consuming logged data with BigQuery Agent Analytics SDK

The [BigQuery Agent Analytics SDK](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/tree/main) provides a convenient way to consume and analyze the data logged by the BigQuery Agent Analytics plugin. The SDK offers pre-built utilities for querying, aggregating, and visualizing your agent's operational data directly from BigQuery.

### Dashboard

The BigQuery Agent Analytics SDK includes an [example Jupyter notebook](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/blob/main/examples/dashboard_v2.ipynb) that demonstrates how to query and visualize your agent's performance data. Use it as a starting point to build your own custom dashboards tailored to your BigQuery Agent Analytics dataset.

## Security: Avoid logging sensitive credentials

Do not log OAuth tokens, API keys, or client secrets

The BigQuery Agent Analytics plugin captures detailed event payloads, including tool arguments, LLM prompts, and authentication-related events (such as HITL credential requests). If your agent uses **authenticated tools** (e.g., `AuthenticatedFunctionTool` with OAuth2), the plugin may log sensitive values such as `client_secret`, `access_token`, or API keys into the `content` column of your BigQuery table.

This is a known concern ([google/adk-python#3845](https://github.com/google/adk-python/issues/3845)) and can lead to credential exposure in your analytics data.

The plugin includes **built-in redaction** that automatically protects common secrets. For additional control, you can layer custom redaction on top.

### Built-in redaction

The plugin automatically redacts values for the following well-known key names (case-insensitive) wherever they appear in `content` or `attributes` JSON:

`client_secret`, `access_token`, `refresh_token`, `id_token`, `api_key`, `password`

In addition, any state key prefixed with **`temp:`** or **`secret:`** is automatically replaced with `[REDACTED]` in the logged `state_delta`. This means ADK session state stored under the `secret:` scope (such as OAuth tokens cached by credential services) is never persisted in BigQuery.

No configuration required

Built-in redaction is always active for structured attributes and state logging, and applies recursively to nested dictionaries and JSON-encoded strings within attribute values. Custom `content_formatter` runs **first** on raw content, so use it to add masking for secrets that may appear in free-form payloads.

### Use `content_formatter` to redact additional secrets

Provide a custom `content_formatter` function in `BigQueryLoggerConfig` to strip or mask sensitive fields before they are written:

```python
import json
import re
from typing import Any

SENSITIVE_KEYS = {"client_secret", "access_token", "refresh_token", "api_key", "secret"}

def redact_credentials(event_content: Any, event_type: str) -> str:
    """Redact OAuth secrets and tokens from logged content."""
    if isinstance(event_content, dict):
        text = json.dumps(event_content)
    else:
        text = str(event_content)

    for key in SENSITIVE_KEYS:
        # Redact values in JSON-like strings: "client_secret": "GOCSPX-xxx"
        text = re.sub(
            rf'("{key}"\s*:\s*)"[^"]*"',
            rf'\1"[REDACTED]"',
            text,
            flags=re.IGNORECASE,
        )
    return text

config = BigQueryLoggerConfig(
    content_formatter=redact_credentials,
    # ... other options
)
```

### Use `event_denylist` to skip credential events

If you do not need to log authentication-related events, exclude them entirely:

```python
config = BigQueryLoggerConfig(
    event_denylist=[
        "HITL_CREDENTIAL_REQUEST",
        "HITL_CREDENTIAL_REQUEST_COMPLETED",
    ],
    # ... other options
)
```

### General best practices

- **Never hardcode secrets** in agent source code. Use environment variables or a secret manager (e.g., Google Cloud Secret Manager) for OAuth client secrets and API keys.
- **Restrict BigQuery table access** using IAM to limit who can read logged event data.
- **Audit your logs** periodically to verify no unexpected sensitive data is being captured.

## Multiprocessing and fork safety

The plugin is fork-aware: it sets `GRPC_ENABLE_FORK_SUPPORT=1` before loading the gRPC C-core library and registers an `os.register_at_fork` handler that resets inherited runtime state (gRPC channels, write streams, event loops) in child processes. This means the plugin can survive `os.fork()` without leaking file descriptors or sending data on a parent's connection.

However, **`spawn` is the recommended multiprocessing start method** for production deployments. `fork` copies the parent's address space — including any in-flight gRPC state — and the post-fork reset adds latency to the first write in each child. With `spawn`, each worker initializes the plugin cleanly.

For Gunicorn deployments specifically:

- Prefer `--preload` combined with lazy plugin initialization (the plugin defers setup until the first event is logged), or
- Initialize the plugin inside a `post_fork` hook so each worker gets its own client.

Note

The fork-safety mechanism resets runtime state only. It does **not** replay events that were queued but not yet flushed in the parent process at the time of fork. Call `await plugin.flush()` before forking if you need to guarantee delivery.

## Feedback

We welcome your feedback on BigQuery Agent Analytics. If you have questions, suggestions, or encounter any issues, please reach out to the team at bqaa-feedback@google.com.

## Additional resources

- [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [Introduction to Object Tables](https://docs.cloud.google.com/bigquery/docs/object-table-introduction)
- [Interactive Demo Notebook](https://github.com/haiyuan-eng-google/demo_BQ_agent_analytics_plugin_notebook)
