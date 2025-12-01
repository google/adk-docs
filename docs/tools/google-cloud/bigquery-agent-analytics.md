# BigQuery Agent Analytics Plugin

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

## Use cases

-   **Agent workflow debugging and analysis:** Capture a wide range of
    *plugin lifecycle events* (LLM calls, tool usage) and *agent-yielded
    events* (user input, model responses), into a well-defined schema.
-   **High-volume analysis and debugging:** Logging operations are performed
    asynchronously in a separate thread to avoid blocking the main agent
    execution. Designed to handle high event volumes, the plugin preserves
    event order via timestamps.

The agent event data recorded varies based on the ADK event type. For more
information, see [Event types and payloads](#event-types).

## Prerequisites

-   **Google Cloud Project** with the **BigQuery API** enabled.
-   **BigQuery Dataset:** Create a dataset to store logging tables before
    using the plugin. The plugin automatically would create the necessary events table within the dataset if the table does not exist. By default, this table is named agent_events, while you can customize this with the table_id parameter in the plugin configuration.
-   **Authentication:**
    -   **Local:** Run `gcloud auth application-default login`.
    -   **Cloud:** Ensure your service account has the required permissions.

### IAM permissions

For the agent to work properly, the principal (e.g., service account, user account) under which the agent is running needs these Google Cloud roles:
*   `roles/bigquery.jobUser` at Project Level to run BigQuery queries in your project. This role doesn't grant access to any data on its own.
*   `roles/bigquery.dataEditor` at Table Level to write log/event data to a BigQuery Table of your choice.
If you need the agent to create this table, you need to grant the `roles/bigquery.dataEditor` on the BigQuery dataset where you want the table to be created.

## Use with agent

You use the BigQuery Analytics Plugin by configuring and registering it with
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

### Run and test agent

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

## Configuration options

You can customize the plugin using `BigQueryLoggerConfig`.

-   **`enabled`** (`bool`, default: `True`): To disable the plugin from logging agent data to the BigQuery table, set this parameter to False.
-   **`event_allowlist`** (`Optional[List[str]]`, default: `None`): A list
    of event types to log. If `None`, all events are logged except those in
    `event_denylist`. For a comprehensive list of supported event types, refer
    to the [Event types and payloads](#event-types) section.
-   **`event_denylist`** (`Optional[List[str]]`, default: `None`): A list of
    event types to skip logging. For a comprehensive list of supported event
    types, refer to the [Event types and payloads](#event-types) section.
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

## Schema and production setup

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
### Event types and payloads {#event-types}

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

## Advanced analysis queries

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

## Additional resources

-   [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
-   [BigQuery product documentation](https://cloud.google.com/bigquery/docs)
