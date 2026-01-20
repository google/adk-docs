# BigQuery Agent Analytics Plugin

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.21.0</span><span class="lst-preview">Preview</span>
</div>

!!! important "Version Requirement"

   Use the ***latest version*** of the ADK (version 1.21.0 or higher) to make full use of the features described in this document.

The BigQuery Agent Analytics Plugin significantly enhances the Agent Development Kit (ADK) by providing a robust solution for in-depth agent behavior analysis. Using the ADK Plugin architecture and the **BigQuery Storage Write API**, it captures and logs critical operational events directly into a Google BigQuery table, empowering you with advanced capabilities for debugging, real-time monitoring, and comprehensive offline performance evaluation.

Version 1.21.0 introduces **Hybrid Multimodal Logging**, allowing you to log large payloads (images, audio, blobs) by offloading them to Google Cloud Storage (GCS) while keeping a structured reference (`ObjectRef`) in BigQuery.

!!! example "Preview release"

    The BigQuery Agent Analytics Plugin is in Preview release. For more
    information, see the
    [launch stage descriptions](https://cloud.google.com/products#product-launch-stages).

!!! warning "BigQuery Storage Write API"

    This feature uses **BigQuery Storage Write API**, which is a paid service.
    For information on costs, see the
    [BigQuery documentation](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing).

## Use cases

-   **Agent workflow debugging and analysis:** Capture a wide range of
    *plugin lifecycle events* (LLM calls, tool usage) and *agent-yielded
    events* (user input, model responses), into a well-defined schema.
-   **High-volume analysis and debugging:** Logging operations are performed
    asynchronously using the Storage Write API to allow high throughput and low latency.
-   **Multimodal Analysis**: Log and analyze text, images, and other modalities. Large files are offloaded to GCS, making them accessible to BigQuery ML via Object Tables.
-   **Distributed Tracing**: Built-in support for OpenTelemetry-style tracing (`trace_id`, `span_id`) to visualize agent execution flows.

The agent event data recorded varies based on the ADK event type. For more
information, see [Event types and payloads](#event-types).

## Prerequisites

-   **Google Cloud Project** with the **BigQuery API** enabled.
-   **BigQuery Dataset:** Create a dataset to store logging tables before
    using the plugin. The plugin automatically creates the necessary events table within the dataset if the table does not exist.
-   **Google Cloud Storage Bucket (Optional):** If you plan to log multimodal content (images, audio, etc.), creating a GCS bucket is recommended for offloading large files.
-   **Authentication:**
    -   **Local:** Run `gcloud auth application-default login`.
    -   **Cloud:** Ensure your service account has the required permissions.

### IAM permissions

For the agent to work properly, the principal (e.g., service account, user account) under which the agent is running needs these Google Cloud roles:
* `roles/bigquery.jobUser` at Project Level to run BigQuery queries.
* `roles/bigquery.dataEditor` at Table Level to write log/event data.
* **If using GCS offloading:** `roles/storage.objectCreator` and `roles/storage.objectViewer` on the target bucket.

## Use with agent

You use the BigQuery Agent Analytics Plugin by configuring and registering it with
your ADK agent's App object. The following example shows an implementation of an
agent with this plugin, including GCS offloading:

```python title="my_bq_agent/agent.py"
# my_bq_agent/agent.py
import os
import google.auth
from google.adk.apps import App
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin, BigQueryLoggerConfig
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BIG_QUERY_DATASET_ID", "your-big-query-dataset-id")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "US") # default location is US in the plugin
GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME", "your-gcs-bucket-name") # Optional

if PROJECT_ID == "your-gcp-project-id":
    raise ValueError("Please set GOOGLE_CLOUD_PROJECT or update the code.")

# --- CRITICAL: Set environment variables BEFORE Gemini instantiation ---
os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = LOCATION
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
    table_id="agent_events_v2", # default table name is agent_events_v2
    config=bq_config,
    location=LOCATION
)

# --- Initialize Tools and Model ---
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials)
)

llm = Gemini(model="gemini-2.5-flash")

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

Test the plugin by running the agent and making a few requests through the chat
interface, such as ”tell me what you can do” or  "List datasets in my cloud project <your-gcp-project-id> “. These actions create events which are
recorded in your Google Cloud project BigQuery instance. Once these events have
been processed, you can view the data for them in the [BigQuery Console](https://console.cloud.google.com/bigquery), using this query

```sql
SELECT timestamp, event_type, content 
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events_v2`
ORDER BY timestamp DESC
LIMIT 20;
```

## Configuration options

You can customize the plugin using `BigQueryLoggerConfig`.

-   **`enabled`** (`bool`, default: `True`): To disable the plugin from logging agent data to the BigQuery table, set this parameter to False.
-   **`clustering_fields`** (`List[str]`, default: `["event_type", "agent", "user_id"]`): The fields used to cluster the BigQuery table when it is automatically created.
-   **`gcs_bucket_name`** (`Optional[str]`, default: `None`): The name of the GCS bucket to offload large content (images, blobs, large text) to. If not provided, large content may be truncated or replaced with placeholders.
-   **`connection_id`** (`Optional[str]`, default: `None`): The BigQuery connection ID (e.g., `us.my-connection`) to use as the authorizer for `ObjectRef` columns. Required for using `ObjectRef` with BigQuery ML.
-   **`max_content_length`** (`int`, default: `500 * 1024`): The maximum length (in characters) of text content to store **inline** in BigQuery before offloading to GCS (if configured) or truncating. Default is 500 KB.
-   **`batch_size`** (`int`, default: `1`): The number of events to batch before writing to BigQuery.
-   **`batch_flush_interval`** (`float`, default: `1.0`): The maximum time (in seconds) to wait before flushing a partial batch.
-   **`shutdown_timeout`** (`float`, default: `10.0`): Seconds to wait for logs to flush during shutdown.
-   **`event_allowlist`** (`Optional[List[str]]`, default: `None`): A list
    of event types to log. If `None`, all events are logged except those in
    `event_denylist`. For a comprehensive list of supported event types, refer
    to the [Event types and payloads](#event-types) section.
-   **`event_denylist`** (`Optional[List[str]]`, default: `None`): A list of
    event types to skip logging. For a comprehensive list of supported event
    types, refer to the [Event types and payloads](#event-types) section.
-   **`content_formatter`** (`Optional[Callable[[Any, str], Any]]`, default: `None`): An optional function to format event content before logging.
-   **`log_multi_modal_content`** (`bool`, default: `True`): Whether to log detailed content parts (including GCS references).
-   **`queue_max_size`** (`int`, default: `10000`): The maximum number of events to hold in the in-memory queue before dropping new events.
-   **`retry_config`** (`RetryConfig`, default: `RetryConfig()`): Configuration for retrying failed BigQuery writes (attributes: `max_retries`, `initial_delay`, `multiplier`, `max_delay`).


The following code sample shows how to define a configuration for the
BigQuery Agent Analytics plugin:

```python
import json
import re

from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryLoggerConfig

def redact_dollar_amounts(event_content: Any) -> str:
    """
    Custom formatter to redact dollar amounts (e.g., $600, $12.50)
    and ensure JSON output if the input is a dict.
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
    client_close_timeout=2.0, # Wait up to 2s for BQ client to close
    max_content_length=500, # Truncate content to 500 chars
    content_formatter=redact_dollar_amounts, # Redact the dollar amounts in the logging content
    queue_max_size=10000, # Max events to hold in memory
    # retry_config=RetryConfig(max_retries=3), # Optional: Configure retries
)

plugin = BigQueryAgentAnalyticsPlugin(..., config=config)
```


## Schema and production setup

The plugin automatically creates the table if it does not exist. However, for
production, we recommend creating the table manually using the following DDL, which utilizes the **JSON** type for flexibility and **REPEATED RECORD**s for multimodal content.

**Recommended DDL:**

```sql
CREATE TABLE `your-gcp-project-id.adk_agent_logs.agent_events_v2`
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
  attributes JSON OPTIONS(description="Arbitrary key-value pairs for additional metadata (e.g., 'root_agent_name', 'model_version', 'usage_metadata')."),
  latency_ms JSON OPTIONS(description="Latency measurements (e.g., total_ms)."),
  status STRING OPTIONS(description="The outcome of the event, typically 'OK' or 'ERROR'."),
  error_message STRING OPTIONS(description="Populated if an error occurs."),
  is_truncated BOOLEAN OPTIONS(description="Flag indicates if content was truncated.")
)
PARTITION BY DATE(timestamp)
CLUSTER BY event_type, agent, user_id;
```

### Event types and payloads {#event-types}

The `content` column now contains a **JSON** object specific to the `event_type`.
The `content_parts` column provides a structured view of the content, especially useful for images or offloaded data.

!!! note "Content Truncation"

    - Variable content fields are truncated to `max_content_length` (configured in `BigQueryLoggerConfig`, default 500KB).
    - If `gcs_bucket_name` is configured, large content is offloaded to GCS instead of being truncated, and a reference is stored in `content_parts.object_ref`.

#### LLM interactions (plugin lifecycle)

These events track the raw requests sent to and responses received from the
LLM.

<table>
  <thead>
    <tr>
      <th><strong>Event Type</strong></th>
      <th><strong>Content (JSON) Structure</strong></th>
      <th><strong>Attributes (JSON)</strong></th>
      <th><strong>Example Content (Simplified)</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>LLM_REQUEST</pre></p></td>
      <td><p><pre>
{
  "prompt": [
    {"role": "user", "content": "..."}
  ],
  "system_prompt": "..."
}
</pre></p></td>
      <td><p><pre>
{
  "tools": ["tool_a", "tool_b"],
  "llm_config": {"temperature": 0.5},
  "root_agent_name": "my_root_agent"
}
</pre></p></td>
      <td><p><pre>
{
  "prompt": [
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "system_prompt": "You are a helpful geography assistant."
}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>LLM_RESPONSE</pre></p></td>
      <td><p><pre>
{
  "response": "...",
  "usage": {...}
}
</pre></p></td>
      <td><p><pre>
{
  "model_version": "gemini-2.5-pro-001",
  "usage_metadata": {
    "prompt_token_count": 15,
    "candidates_token_count": 7,
    "total_token_count": 22
  }
}
</pre></p></td>
      <td><p><pre>
{
  "response": "The capital of France is Paris.",
  "usage": {
    "prompt": 15,
    "completion": 7,
    "total": 22
  }
}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>LLM_ERROR</pre></p></td>
      <td><p><pre>null</pre></p></td>
      <td><p><pre>{}</pre></p></td>
      <td><p><pre>null (See error_message column)</pre></p></td>
    </tr>
  </tbody>
</table>

#### Tool usage (plugin lifecycle)

These events track the execution of tools by the agent.

<table>
  <thead>
    <tr>
      <th><strong>Event Type</strong></th>
      <th><strong>Content (JSON) Structure</strong></th>
      <th><strong>Attributes (JSON)</strong></th>
      <th><strong>Example Content</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>TOOL_STARTING</pre></p></td>
      <td><p><pre>
{
  "tool": "...",
  "args": {...}
}
</pre></p></td>
      <td><p><pre>{}</pre></p></td>
      <td><p><pre>
{"tool": "list_datasets", "args": {"project_id": "my-project"}}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>TOOL_COMPLETED</pre></p></td>
      <td><p><pre>
{
  "tool": "...",
  "result": "..."
}
</pre></p></td>
      <td><p><pre>{}</pre></p></td>
      <td><p><pre>
{"tool": "list_datasets", "result": ["ds1", "ds2"]}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>TOOL_ERROR</pre></p></td>
      <td><p><pre>
{
  "tool": "...",
  "args": {...}
}
</pre></p></td>
      <td><p><pre>{}</pre></p></td>
      <td><p><pre>
{"tool": "list_datasets", "args": {}}
</pre></p></td>
    </tr>
  </tbody>
</table>

#### Agent lifecycle & Generic Events

<table>
  <thead>
    <tr>
      <th><strong>Event Type</strong></th>
      <th><strong>Content (JSON) Structure</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>INVOCATION_STARTING</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>INVOCATION_COMPLETED</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>AGENT_STARTING</pre></p></td>
      <td><p><pre>"You are a helpful agent..."</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>AGENT_COMPLETED</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>USER_MESSAGE_RECEIVED</pre></p></td>
      <td><p><pre>{"text_summary": "Help me book a flight."}</pre></p></td>
    </tr>

  </tbody>
</table>

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
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`,
UNNEST(content_parts) AS part
WHERE part.storage_mode = 'GCS_REFERENCE'
ORDER BY timestamp DESC
LIMIT 10;
```

## Advanced analysis queries

**Trace a specific conversation turn using trace_id**

```sql
SELECT timestamp, event_type, agent, JSON_VALUE(content, '$.response') as summary
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
WHERE trace_id = 'your-trace-id'
ORDER BY timestamp ASC;
```

**Token usage analysis (accessing JSON fields)**

```sql
SELECT
  AVG(CAST(JSON_VALUE(content, '$.usage.total') AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
WHERE event_type = 'LLM_RESPONSE';
```

**Querying Multimodal Content (using content_parts and ObjectRef)**

```sql
SELECT
  timestamp,
  part.mime_type,
  part.object_ref.uri as gcs_uri
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`,
UNNEST(content_parts) as part
WHERE part.mime_type LIKE 'image/%'
ORDER BY timestamp DESC;
```

**Analyze Multimodal Content with BigQuery Remote Model (Gemini)**

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
  `your-gcp-project-id.your-dataset-id.agent_events_v2` logs,
  UNNEST(logs.content_parts) AS parts
WHERE
  parts.mime_type LIKE 'image/%'
ORDER BY logs.timestamp DESC
LIMIT 1;
```

**Latency Analysis (LLM & Tools)**

```sql
SELECT
  event_type,
  AVG(CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64)) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
WHERE event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
GROUP BY event_type;
```

**Span Hierarchy & Duration Analysis**

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
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
WHERE trace_id = 'your-trace-id'
  AND event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
ORDER BY timestamp ASC;
```


### 7. AI-Powered Root Cause Analysis (Agent Ops)

Automatically analyze failed sessions to determine the root cause of errors using BigQuery ML and Gemini.

```sql
DECLARE failed_session_id STRING;
-- Find a recent failed session
SET failed_session_id = (
    SELECT session_id
    FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
    WHERE error_message IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 1
);

-- Reconstruct the full conversation context
WITH SessionContext AS (
    SELECT
        session_id,
        STRING_AGG(CONCAT(event_type, ': ', COALESCE(TO_JSON_STRING(content), '')), '\n' ORDER BY timestamp) as full_history
    FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
    WHERE session_id = failed_session_id
    GROUP BY session_id
)
-- Ask Gemini to diagnose the issue
SELECT
    session_id,
    AI.GENERATE(
        ('Analyze this conversation log and explain the root cause of the failure. Log: ', full_history),
        connection_id => 'your-gcp-project-id.us.my-connection',
        endpoint => 'gemini-2.5-flash'
    ).result AS root_cause_explanation
FROM SessionContext;
```


## Conversational Analytics in BigQuery

You can also use 
[BigQuery Conversational Analytics](https://cloud.google.com/bigquery/docs/conversational-analytics)
to analyze your agent logs using natural language. Use this tool to answer questions like:

*   "Show me the error rate over time"
*   "What are the most common tool calls?"
*   "Identify sessions with high token usage"

## Looker Studio Dashboard

You can visualize your agent's performance using our pre-built [Looker Studio Dashboard template](https://lookerstudio.google.com/c/reporting/f1c5b513-3095-44f8-90a2-54953d41b125/page/8YdhF).

To connect this dashboard to your own BigQuery table, use the following link format, replacing the placeholders with your specific project, dataset, and table IDs:

```text
https://lookerstudio.google.com/reporting/create?c.reportId=f1c5b513-3095-44f8-90a2-54953d41b125&ds.ds3.connector=bigQuery&ds.ds3.type=TABLE&ds.ds3.projectId=<your-project-id>&ds.ds3.datasetId=<your-dataset-id>&ds.ds3.tableId=<your-table-id>
```

## Additional resources

-   [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
-   [Introduction to Object Tables](https://cloud.google.com/bigquery/docs/object-tables-intro)
-   [Interactive Demo Notebook](https://github.com/haiyuan-eng-google/demo_BQ_agent_analytics_plugin_notebook)
