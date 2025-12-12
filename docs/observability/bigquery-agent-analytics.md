# BigQuery Agent Analytics Plugin

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.21.0+</span><span class="lst-preview">Preview</span>
</div>

!!! important "Version Requirement"

   We **strongly recommend** using the **latest version** of the ADK (version 1.21.0 or later) to make full use of the features described in this document.

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
    to the [Event types and payloads](#event-types-deprecated) section.
-   **`event_denylist`** (`Optional[List[str]]`, default: `None`): A list of
    event types to skip logging. For a comprehensive list of supported event
    types, refer to the [Event types and payloads](#event-types-deprecated) section.
-   **`content_formatter`** (`Optional[Callable[[Any, str], Any]]`, default: `None`): An optional function to format event content before logging.
-   **`log_multi_modal_content`** (`bool`, default: `True`): Whether to log detailed content parts (including GCS references).


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
  timestamp TIMESTAMP NOT NULLOPTIONS(description="The UTC time at which the event was logged."),
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
  attributes JSON OPTIONS(description="Arbitrary key-value pairs for additional metadata."),
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
  "llm_config": {"temperature": 0.5}
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
      <td><p><pre>{}</pre></p></td>
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

## Additional resources

-   [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
-   [Introduction to Object Tables](https://cloud.google.com/bigquery/docs/object-tables-intro)

<br>
<br>
<br>
<hr>

## Deprecated (v < 1.21.0)

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.19.0</span><span class="lst-preview">Preview</span>
</div>

The BigQuery Agent Analytics Plugin significantly enhances the Agent Development Kit (ADK) by providing a robust solution for in-depth agent behavior analysis. Using the ADK Plugin architecture and the BigQuery Storage Write API, it captures and logs critical operational events directly into a Google BigQuery table, empowering you with advanced capabilities for debugging, real-time monitoring, and comprehensive offline performance evaluation.

!!! example "Preview release"

    The BigQuery Agent Analytics Plugin is in Preview release. For more
    information, see the
    [launch stage descriptions](https://cloud.google.com/products#product-launch-stages).

!!! warning "BigQuery Storage Write API"

    This feature uses **BigQuery Storage Write API**, which is a paid service.
    For information on costs, see the
    [BigQuery documentation](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing).

### Use cases

-   **Agent workflow debugging and analysis:** Capture a wide range of
    *plugin lifecycle events* (LLM calls, tool usage) and *agent-yielded
    events* (user input, model responses), into a well-defined schema.
-   **High-volume analysis and debugging:** Logging operations are performed
    asynchronously in a separate thread to avoid blocking the main agent
    execution. Designed to handle high event volumes, the plugin preserves
    event order via timestamps.

The agent event data recorded varies based on the ADK event type. For more
information, see [Event types and payloads](#event-types-deprecated).

### Prerequisites

-   **Google Cloud Project** with the **BigQuery API** enabled.
-   **BigQuery Dataset:** Create a dataset to store logging tables before
    using the plugin. The plugin automatically would create the necessary events table within the dataset if the table does not exist. By default, this table is named agent_events, while you can customize this with the table_id parameter in the plugin configuration.
-   **Authentication:**
    -   **Local:** Run `gcloud auth application-default login`.
    -   **Cloud:** Ensure your service account has the required permissions.

#### IAM permissions

For the agent to work properly, the principal (e.g., service account, user account) under which the agent is running needs these Google Cloud roles:
*   `roles/bigquery.jobUser` at Project Level to run BigQuery queries in your project. This role doesn't grant access to any data on its own.
*   `roles/bigquery.dataEditor` at Table Level to write log/event data to a BigQuery Table of your choice.
If you need the agent to create this table, you need to grant the `roles/bigquery.dataEditor` on the BigQuery dataset where you want the table to be created.

### Use with agent

You use the BigQuery Agent Analytics Plugin by configuring and registering it with
your ADK agent's App object. The following example shows an implementation of an
agent with this plugin and BigQuery tools enabled:

```python title="my_bq_agent/agent.py"
# my_bq_agent/agent.py
import os
import google.auth
from google.adk.apps import App
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BIG_QUERY_DATASET_ID", "your-big-query-dataset-id")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "your-gcp-project-location") # use the location of your google cloud project

if PROJECT_ID == "your-gcp-project-id":
    raise ValueError("Please set GOOGLE_CLOUD_PROJECT or update the code.")
if DATASET_ID == "your-big-query-dataset-id":
    raise ValueError("Please set BIG_QUERY_DATASET_ID or update the code.")
if LOCATION == "your-gcp-project-location":
    raise ValueError("Please set GOOGLE_CLOUD_LOCATION or update the code.")

# --- CRITICAL: Set environment variables BEFORE Gemini instantiation ---
os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = LOCATION
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True' # Make sure you have Vertex AI API enabled

# --- Initialize the Plugin ---
bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, # project_id is required input from user
    dataset_id=DATASET_ID, # dataset_id is required input from user
    table_id="agent_events" # Optional: defaults to "agent_events". The plugin automatically creates this table if it doesn't exist.
)

# --- Initialize Tools and Model ---
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials)
)

llm = Gemini(
    model="gemini-2.5-flash",
)

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
    plugins=[bq_logging_plugin], # Register the plugin here
)
```

#### Run and test agent

Test the plugin by running the agent and making a few requests through the chat
interface, such as ”tell me what you can do” or  "List datasets in my cloud project <your-gcp-project-id> “. These actions create events which are
recorded in your Google Cloud project BigQuery instance. Once these events have
been processed, you can view the data for them in the [BigQuery Console](https://console.cloud.google.com/bigquery), using this query

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

### Configuration options

You can customize the plugin using `BigQueryLoggerConfig`.

-   **`enabled`** (`bool`, default: `True`): To disable the plugin from logging agent data to the BigQuery table, set this parameter to False.
-   **`event_allowlist`** (`Optional[List[str]]`, default: `None`): A list
    of event types to log. If `None`, all events are logged except those in
    `event_denylist`. For a comprehensive list of supported event types, refer
    to the [Event types and payloads](#event-types-deprecated) section.
-   **`event_denylist`** (`Optional[List[str]]`, default: `None`): A list of
    event types to skip logging. For a comprehensive list of supported event
    types, refer to the [Event types and payloads](#event-types-deprecated) section.
-   **`content_formatter`** (`Optional[Callable[[Any], str]]`, default:
    `None`): An optional function to format event content before logging. The
    following code illustrates how to implement the content formatter.
-   **`shutdown_timeout`** (`float`, default: `5.0`): Seconds to wait for
    logs to flush during shutdown.
-   **`client_close_timeout`** (`float`, default: `2.0`): Seconds to wait
    for the BigQuery client to close.
-   **`max_content_length`** (`int`, default: `500`): The maximum length of
    content parts before truncation.

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
    max_content_length=500, # Truncate content to 500 chars (default)
    content_formatter=redact_dollar_amounts, # Redact the dollar amounts in the logging content

)

plugin = BigQueryAgentAnalyticsPlugin(..., config=config)
```

### Schema and production setup

The plugin automatically creates the table if it does not exist. However, for
production, we recommend creating the table manually with **partitioning** and
**clustering** for performance and cost optimization.

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
  content STRING OPTIONS(description="The event-specific data (payload). Format varies by event_type."),
  error_message STRING OPTIONS(description="Populated if an error occurs during the processing of the event."),
  is_truncated BOOLEAN OPTIONS(description="Boolean flag indicates if the content field was truncated due to size limits.")
)
PARTITION BY DATE(timestamp)
CLUSTER BY event_type, agent, user_id;
```
### Event types and payloads {#event-types-deprecated}

The `content` column contains a formatted string specific to the `event_type`.
The following table descibes these events and corresponding content.

!!! note

    - All variable content fields (e.g., user input, model response, tool arguments, system prompt) 
    - are truncated to `max_content_length` characters 
    - (configured in `BigQueryLoggerConfig`, default 500) to manage log size.

#### LLM interactions (plugin lifecycle)

These events track the raw requests sent to and responses received from the
LLM.

<table>
  <thead>
    <tr>
      <th><strong>Event Type</strong></th>
      <th><strong>Trigger Condition</strong></th>
      <th><strong>Content Format Logic</strong></th>
      <th><strong>Example Content</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
LLM_REQUEST
</pre></p></td>
      <td><p><pre>
before_model_callback
</pre></p></td>
      <td><p><pre>
Model: {model} | Prompt: {prompt} | System Prompt: Model: {model} | Prompt: {formatted_contents} | System Prompt: {system_prompt} | Params: {params} | Available Tools: {tool_names}
</pre></p></td>
      <td><p><pre>
Model: gemini-2.5-flash | Prompt: user: Model: gemini-flash-2.5| Prompt: user: text: 'Hello'| System Prompt: You are a helpful assistant. | Params: {temperature=1.0} | Available Tools: ['bigquery_tool']
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
LLM_RESPONSE
</pre></p></td>
      <td><p><pre>
after_model_callback
</pre></p></td>
      <td><strong>If Tool Call:</strong> <code>Tool Name: {func_names} | Token
Usage: {usage}</code><br>
<br>
**If Text:** `Tool Name: text_response, text: '{text}' | Token Usage:
{usage}`</td>
      <td><p><pre>
Tool Name: text_response, text: 'Here is the data.' | Token Usage: {prompt: 10, candidates: 5, total: 15}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
LLM_ERROR
</pre></p></td>
      <td><p><pre>
on_model_error_callback
</pre></p></td>
      <td><code>None</code> (Error details are in <code>error_message</code>
column)</td>
      <td><p><pre>
None
</pre></p></td>
    </tr>
  </tbody>
</table>

#### Tool usage (plugin lifecycle)

These events track the execution of tools by the agent.

<table>
  <thead>
    <tr>
      <th><strong>Event Type</strong></th>
      <th><strong>Trigger Condition</strong></th>
      <th><strong>Content Format Logic</strong></th>
      <th><strong>Example Content</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
TOOL_STARTING
</pre></p></td>
      <td><p><pre>
before_tool_callback
</pre></p></td>
      <td><p><pre>
Tool Name: {name}, Description: {desc}, Arguments: {args}
</pre></p></td>
      <td><p><pre>
Tool Name: list_datasets, Description: Lists datasets..., Arguments: {'project_id': 'my-project'}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_COMPLETED
</pre></p></td>
      <td><p><pre>
after_tool_callback
</pre></p></td>
      <td><p><pre>
Tool Name: {name}, Result: {result}
</pre></p></td>
      <td><p><pre>
Tool Name: list_datasets, Result: ['dataset_1', 'dataset_2']
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_ERROR
</pre></p></td>
      <td><p><pre>
on_tool_error_callback
</pre></p></td>
      <td><code>Tool Name: {name}, Arguments: {args}</code> (Error details in
<code>error_message</code>)</td>
      <td><p><pre>
Tool Name: list_datasets, Arguments: {}
</pre></p></td>
    </tr>
  </tbody>
</table>

#### Agent lifecycle (plugin lifecycle)

These events track the start and end of agent execution, including
sub-agents.

<table>
  <thead>
    <tr>
      <th><strong>Event Type</strong></th>
      <th><strong>Trigger Condition</strong></th>
      <th><strong>Content Format Logic</strong></th>
      <th><strong>Example Content</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
INVOCATION_STARTING
</pre></p></td>
      <td><p><pre>
before_run_callback
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
INVOCATION_COMPLETED
</pre></p></td>
      <td><p><pre>
after_run_callback
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
AGENT_STARTING
</pre></p></td>
      <td><p><pre>
before_agent_callback
</pre></p></td>
      <td><p><pre>
Agent Name: {agent_name}
</pre></p></td>
      <td><p><pre>
Agent Name: sub_agent_researcher
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
AGENT_COMPLETED
</pre></p></td>
      <td><p><pre>
after_agent_callback
</pre></p></td>
      <td><p><pre>
Agent Name: {agent_name}
</pre></p></td>
      <td><p><pre>
Agent Name: sub_agent_researcher
</pre></p></td>
    </tr>
  </tbody>
</table>

#### User and generic events (Event stream)

These events are derived from the `Event` objects yielded by the agent or the
runner.

<table>
  <thead>
    <tr>
      <th><strong>Event Type</strong></th>
      <th><strong>Trigger Condition</strong></th>
      <th><strong>Content Format Logic</strong></th>
      <th><strong>Example Content</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
USER_MESSAGE_RECEIVED
</pre></p></td>
      <td><p><pre>
on_user_message_callback
</pre></p></td>
      <td><p><pre>
User Content: {formatted_message}
</pre></p></td>
      <td><p><pre>
User Content: text: 'Show me the sales data.'
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_CALL
</pre></p></td>
      <td><code>event.get_function_calls()</code> is true</td>
      <td><p><pre>
call: {func_name}
</pre></p></td>
      <td><p><pre>
call: list_datasets
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_RESULT
</pre></p></td>
      <td><code>event.get_function_responses()</code> is true</td>
      <td><p><pre>
resp: {func_name}
</pre></p></td>
      <td><p><pre>
resp: list_datasets
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
MODEL_RESPONSE
</pre></p></td>
      <td><code>event.content</code> has parts</td>
      <td><p><pre>
text: '{text}'
</pre></p></td>
      <td><p><pre>
text: 'I found 2 datasets.'
</pre></p></td>
    </tr>
  </tbody>
</table>

### Advanced analysis queries

The following example queries demonstrate how to extract information from the
recorded ADK agent event analytics data in BigQuery. You can run these queries
using the [BigQuery Console](https://console.cloud.google.com/bigquery).

Before executing these queries, ensure you update the GCP project ID, BigQuery dataset ID, and the table ID (defaulting to "agent_events" if unspecified) within the provided SQL.

**Trace a specific conversation turn**

```sql
SELECT timestamp, event_type, agent, content
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE invocation_id = 'your-invocation-id'
ORDER BY timestamp ASC;
```

**Daily invocation volume**

```sql
SELECT DATE(timestamp) as log_date, COUNT(DISTINCT invocation_id) as count
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'INVOCATION_STARTING'
GROUP BY log_date ORDER BY log_date DESC;
```

**Token usage analysis**

```sql
SELECT
  AVG(CAST(REGEXP_EXTRACT(content, r"Token Usage:.*total: ([0-9]+)") AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'LLM_RESPONSE';
```

**Error monitoring**

```sql
SELECT timestamp, event_type, error_message
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE error_message IS NOT NULL
ORDER BY timestamp DESC LIMIT 50;
```
