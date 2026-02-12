---
catalog_title: BigQuery Agent Analytics Plugin
catalog_description: In-depth agent analytics for behavior analysis and logging
catalog_icon: /adk-docs/integrations/assets/bigquery.png
catalog_tags: ["observability", "google"]
---

# BigQuery Agent Analytics plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.21.0</span><span class="lst-preview">Preview</span>
</div>

!!! important "Version Requirement"

    Use ADK Python version 1.21.0 or higher to make full use of the features described in this document.

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


# --- OpenTelemetry Initialization (Optional) ---
# Recommended for enabling distributed tracing (populates trace_id, span_id).
# If not configured, the plugin uses internal UUIDs for span correlation.
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    trace.set_tracer_provider(TracerProvider())
except ImportError:
    pass # OpenTelemetry is optional

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

## Tracing and Observability

The plugin supports **OpenTelemetry** for distributed tracing.

- **Automatic Span Management**: The plugin automatically generates spans for Agent execution, LLM calls, and Tool executions.
- **OpenTelemetry Integration**: If an OpenTelemetry `TracerProvider` is configured (as shown in the example above), the plugin will use valid OTel spans, populating `trace_id`, `span_id`, and `parent_span_id` with standard OTel identifiers. This allows you to correlate agent logs with other services in your distributed system.
- **Fallback Mechanism**: If OpenTelemetry is not installed or configured, the plugin automatically falls back to generating internal UUIDs for spans and uses the `invocation_id` as the trace ID. This ensures that the parent-child hierarchy (Agent -> Span -> Tool/LLM) is *always* preserved in the BigQuery logs, even without a full OTel setup.

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
-   **`log_session_metadata`** (`bool`, default: `True`): If True, logs metadata from the `session` object (e.g., `session.metadata`) into the `attributes` column.
-   **`custom_tags`** (`Dict[str, Any]`, default: `{}`): A dictionary of static tags (e.g., `{"env": "prod", "version": "1.0"}`) to be included in the `attributes` column for every event.


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

### Schema Reference

The events table (`agent_events_v2`) uses a flexible schema. The following table provides a comprehensive reference with example values.

| Field Name | Type | Mode | Description | Example Value |
|:---|:---|:---|:---|:---|
| **timestamp** | `TIMESTAMP` | `REQUIRED` | UTC timestamp of event creation. Acts as the primary ordering key and often the daily partitioning key. Precision is microsecond. | `2026-02-03 20:52:17 UTC` |
| **event_type** | `STRING` | `NULLABLE` | The canonical event category. Standard values include `LLM_REQUEST`, `LLM_RESPONSE`, `TOOL_STARTING`, `TOOL_COMPLETED`, `AGENT_STARTING`, `AGENT_COMPLETED`, `STATE_DELTA`. Used for high-level filtering. | `LLM_REQUEST` |
| **agent** | `STRING` | `NULLABLE` | The name of the agent responsible for this event. Defined during agent initialization or via the `root_agent_name` context. | `my_bq_agent` |
| **session_id** | `STRING` | `NULLABLE` | A persistent identifier for the entire conversation thread. Stays constant across multiple turns and sub-agent calls. | `04275a01-1649-4a30-b6a7-5b443c69a7bc` |
| **invocation_id** | `STRING` | `NULLABLE` | The unique identifier for a single execution turn or request cycle. Corresponds to `trace_id` in many contexts. | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **user_id** | `STRING` | `NULLABLE` | The identifier of the user (human or system) initiating the session. Extracted from the `User` object or metadata. | `test_user` |
| **trace_id** | `STRING` | `NULLABLE` | The **OpenTelemetry** Trace ID (32-char hex). Links all operations within a single distributed request lifecycle. | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **span_id** | `STRING` | `NULLABLE` | The **OpenTelemetry** Span ID (16-char hex). Uniquely identifies this specific atomic operation. | `69867a836cd94798be2759d8e0d70215` |
| **parent_span_id** | `STRING` | `NULLABLE` | The Span ID of the immediate caller. Used to reconstruct the parent-child execution tree (DAG). | `ef5843fe40764b4b8afec44e78044205` |
| **content** | `JSON` | `NULLABLE` | The primary event payload. Structure is polymorphic based on `event_type`. | `{"system_prompt": "You are...", "prompt": [{"role": "user", "content": "hello"}], "response": "Hi", "usage": {"total": 15}}` |
| **attributes** | `JSON` | `NULLABLE` | Metadata/Enrichment (usage stats, model info, custom tags). | `{"model": "gemini-2.5-flash", "usage_metadata": {"total_token_count": 15}, "state_delta": {"key": "val"}, "session_metadata": {"key": "val"}}` |
| **latency_ms** | `JSON` | `NULLABLE` | Performance metrics. Standard keys are `total_ms` (wall-clock duration) and `time_to_first_token_ms` (streaming latency). | `{"total_ms": 1250, "time_to_first_token_ms": 450}` |
| **status** | `STRING` | `NULLABLE` | High-level outcome. Values: `OK` (success) or `ERROR` (failure). | `OK` |
| **error_message** | `STRING` | `NULLABLE` | Human-readable exception message or stack trace fragment. Populated only when `status` is `ERROR`. | `Error 404: Dataset not found` |
| **is_truncated** | `BOOLEAN` | `NULLABLE` | `true` if `content` or `attributes` exceeded the BigQuery cell size limit (default 10MB) and were partially dropped. | `false` |
| **content_parts** | `RECORD` | `REPEATED` | Array of multi-modal segments (Text, Image, Blob). Used when content cannot be serialized as simple JSON (e.g., large binaries or GCS refs). | `[{"mime_type": "text/plain", "text": "hello"}]` |

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
  attributes JSON OPTIONS(description="Arbitrary key-value pairs for additional metadata (e.g., 'root_agent_name', 'model_version', 'usage_metadata', 'session_metadata', 'custom_tags')."),
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
    "model": "gemini-2.5-flash",
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

#### Tool usage (plugin lifecycle)

These events track the execution of tools by the agent.

**3. TOOL_STARTING**

Logged when an agent begins executing a tool.

```json
{
  "event_type": "TOOL_STARTING",
  "content": {
    "tool": "list_dataset_ids",
    "args": {
      "project_id": "bigquery-public-data"
    }
  }
}
```

**4. TOOL_COMPLETED**

Logged when a tool execution finishes.

```json
{
  "event_type": "TOOL_COMPLETED",
  "content": {
    "tool": "list_dataset_ids",
    "result": [
      "austin_311",
      "austin_bikeshare"
    ]
  },
  "latency_ms": {
    "total_ms": 467
  }
}
```

#### State Management

These events track changes to the agent's state, typically triggered by tools.

**5. STATE_DELTA**

Tracks changes to the agent's internal state (e.g., token cache updates).

```json
{
  "event_type": "STATE_DELTA",
  "attributes": {
    "state_delta": {
      "bigquery_token_cache": "{\"token\": \"ya29...\", \"expiry\": \"...\"}"
    }
  }
}
```

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
