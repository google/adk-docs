# BigQuery Logging Plugin

The `BigQueryLoggingPlugin` is a powerful tool for capturing and analyzing agent behavior by logging events to a BigQuery table. This plugin allows you to create a persistent, structured log of your agent's interactions, which can be used for debugging, auditing, and performance analysis.

## How it Works

The `BigQueryLoggingPlugin` hooks into the agent's lifecycle and logs various events to a specified BigQuery table. The plugin automatically creates the dataset and table if they don't exist.

The following events are logged:

*   **User Messages:** The initial input from the user.
*   **Agent Execution:** The start and completion of an agent's execution.
*   **LLM Requests and Responses:** The prompts sent to the language model and the responses received, including token usage.
*   **Tool Calls:** The arguments passed to a tool and the results returned.
*   **Errors:** Any errors that occur during model or tool execution.

## Configuration

To use the `BigQueryLoggingPlugin`, you need to configure it with your BigQuery project, dataset, and table information.

```python
from google.adk.plugins.bigquery_logging_plugin import BigQueryLoggingPlugin

# Configure the plugin with your BigQuery project, dataset, and table
bq_logging_plugin = BigQueryLoggingPlugin(
    project_id="your-gcp-project-id",
    dataset_id="your-bigquery-dataset-id",
    table_id="your-bigquery-table-id",  # Optional, defaults to "agent_events"
)
```

You can then add the plugin to your `App` or `Runner`:

```python
from google.adk.apps import App
from my_agent import root_agent

# Add the plugin to your App
my_app = App(
    root_agent=root_agent,
    plugins=[bq_logging_plugin],
)
```

### Advanced Configuration

The `BigQueryLoggingPlugin` can be further customized using the `BigQueryLoggerConfig` class.

```python
from google.adk.plugins.bigquery_logging_plugin import BigQueryLoggingPlugin, BigQueryLoggerConfig

# Define a custom content formatter to redact sensitive information
def redact_content(content):
    # Implement your redaction logic here
    return "REDACTED"

# Configure the logger to only log specific events and use the custom formatter
logger_config = BigQueryLoggerConfig(
    event_allowlist=["USER_INPUT", "MODEL_RESPONSE", "TOOL_CALL"],
    content_formatter=redact_content,
)

bq_logging_plugin = BigQueryLoggingPlugin(
    project_id="your-gcp-project-id",
    dataset_id="your-bigquery-dataset-id",
    config=logger_config,
)
```

## Schema

The BigQuery table created by the plugin has the following schema:

*   `timestamp`: The timestamp of the event.
*   `event_type`: The type of event (e.g., `USER_INPUT`, `MODEL_RESPONSE`, `TOOL_CALL`).
*   `agent`: The name of the agent that generated the event.
*   `session_id`: The ID of the session.
*   `invocation_id`: The ID of the invocation.
*   `user_id`: The ID of the user.
*   `content`: The content of the event, such as the user's message or the model's response.
*   `error_message`: Any error message associated with the event.
