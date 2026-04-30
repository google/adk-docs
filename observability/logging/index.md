# Agent activity logging

Supported in ADKPython v0.1.0Go v0.1.0

Agent Development Kit (ADK) provides flexible and powerful logging capabilities to monitor agent behavior and debug issues effectively.

## Logging philosophy

ADK's approach to logging is to provide detailed diagnostic information without being overly verbose by default. It is designed to be configured by the application developer, allowing you to tailor the log output to your specific needs, whether in a development or production environment.

- **Standard Library Integration:** ADK uses the standard logging facilities of the host language (e.g., Python's `logging` module, Go's `log` package).
- **Structured GenAI Logging:** ADK uses OpenTelemetry to log structured events for GenAI requests and responses, allowing for advanced monitoring and debugging in cloud environments.
- **User-Configured:** While ADK provides defaults and integration with its CLI tools, it is ultimately the responsibility of the application developer to configure logging to suit their specific environment.

## Logging schema

ADK emits logs using standard library facilities and structured GenAI events via OpenTelemetry.

### Structured GenAI logs

Structured GenAI logs emitted via OpenTelemetry follow the [Semantic Conventions for GenAI](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-events.md).

By default prompt content is elided in logs for security. You can enable prompt logging using environment variables or programmatic configuration (see Setup section below).

### Log levels (Python)

The following table describes what is logged at different levels in Python when using the standard logger:

| Level         | Description                                                                                                            | Type of Information Logged                                                                                                                                                                                            |
| ------------- | ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`DEBUG`**   | **Crucial for debugging.** The most verbose level for fine-grained diagnostic information.                             | - **Full LLM Prompts:** The complete request sent to the language model, including system instructions, history, and tools. - Detailed API responses from services. - Internal state transitions and variable values. |
| **`INFO`**    | General information about the agent's lifecycle.                                                                       | - Agent initialization and startup. - Session creation and deletion events. - Execution of a tool, including its name and arguments.                                                                                  |
| **`WARNING`** | Indicates a potential issue or deprecated feature use. The agent continues to function, but attention may be required. | - Use of deprecated methods or parameters. - Non-critical errors that the system recovered from.                                                                                                                      |
| **`ERROR`**   | A serious error that prevented an operation from completing.                                                           | - Failed API calls to external services (e.g., LLM, Session Service). - Unhandled exceptions during agent execution. - Configuration errors.                                                                          |

Note

It is recommended to use `INFO` or `WARNING` in production environments. Only enable `DEBUG` when actively troubleshooting an issue, as `DEBUG` logs can be very verbose and may contain sensitive information.

## Logging setup

### Logging in ADK Web

When running agents using the ADK's `adk web`, `adk api_server`, `adk deploy cloud_run` and `adk deploy gke` commands, you can control the log verbosity or destination.

#### Logging level

To start the web server with `DEBUG` level logging, run:

```bash
adk web --log_level DEBUG path/to/your/agents_dir
```

The available log levels for the `--log_level` option are: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, `CRITICAL`.

#### Capture prompt content

By default a prompt content is elided in logs for security. You can enable prompt logging using the environment variable:

```bash
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

Warning

The `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` setting logs the full content of user prompts and agent responses. This is useful for debugging but may capture sensitive data or PII. In production, set this to false or ensure you have appropriate data handling policies in place.

#### OTLP export

To export logs to an OTLP-compatible backend, set the standard OTel environment variables:

```bash
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="http://your-collector:4318/v1/logs"
adk web path/to/your/agents_dir
```

Note

You can also set the general `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable if you would like to send metrics and traces to the same endpoint in addition to logs.

#### GCP export setup

You can enable GCP export using the `-otel_to_cloud` flag:

```bash
adk web -otel_to_cloud path/to/your/agents_dir
```

### Python programmatic setup

In Python, ADK uses the standard `logging` module and OpenTelemetry for structured GenAI logs.

#### Logging level

To enable detailed logging, including `DEBUG` level messages, add the following to the top of your script:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
```

#### Capture prompt content

You can enable full prompt logging programmatically by setting an environment variable:

```python
import os

os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "true"
```

#### OTLP export

To export logs to an OpenTelemetry Collector (or an OTLP-compatible backend) programmatically:

```python
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

os.environ["OTEL_EXPORTER_OTLP_LOGS_ENDPOINT"] = "http://your-collector:4318/v1/logs"
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers()
```

#### GCP export setup

To export logs to Google Cloud Logging programmatically, use the OpenTelemetry Google Cloud exporter. Here is an example in Python:

```python
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

gcp_exporters = get_gcp_exporters(
  enable_cloud_logging = True,
)
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers([gcp_exporters])
```

### Go programmatic setup

In Go, ADK uses the `google.golang.org/adk/telemetry` package for OpenTelemetry configuration and the standard `log` package for general events.

#### Capture prompt content

You can enable full prompt logging programmatically when initializing telemetry:

```go
package main

import (
    "context"
    "google.golang.org/adk/telemetry"
)

func main() {
    ctx := context.Background()
    tp, err := telemetry.New(ctx,
        telemetry.WithGenAICaptureMessageContent(true),
    )
    if err != nil {
        // handle error
    }
    defer tp.Shutdown(ctx)
    tp.SetGlobalOtelProviders()
}
```

#### OTLP export

To export logs to an OTLP-compatible backend, configure the standard OpenTelemetry environment variables (e.g., `OTEL_EXPORTER_OTLP_ENDPOINT` or `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`). The ADK telemetry package will automatically use these settings when initialized.

#### GCP export setup

To export logs to Google Cloud Logging, use the `WithOtelToCloud` option:

```go
package main

import (
    "context"
    "google.golang.org/adk/telemetry"
)

func main() {
    ctx := context.Background()
    tp, err := telemetry.New(ctx,
        telemetry.WithOtelToCloud(true),
    )
    if err != nil {
        // handle error
    }
    defer tp.Shutdown(ctx)
    tp.SetGlobalOtelProviders()
}
```

If using the Go launcher, you can also enable GCP export via the CLI flag:

```bash
go run main.go web -otel_to_cloud
```

General events (like server startup or HTTP requests) are logged using the standard Go `log` package. These logs are written to `stderr` by default.

## Understanding log output

### Sample Python log entry

```text
2025-07-08 11:22:33,456 - DEBUG - google_adk.models.google_llm - LLM Request: contents { ... }
```

| Log Segment                     | Format Specifier | Meaning                                        |
| ------------------------------- | ---------------- | ---------------------------------------------- |
| `2025-07-08 11:22:33,456`       | `%(asctime)s`    | Timestamp                                      |
| `DEBUG`                         | `%(levelname)s`  | Severity level                                 |
| `google_adk.models.google_llm`  | `%(name)s`       | Logger name (the module that produced the log) |
| `LLM Request: contents { ... }` | `%(message)s`    | The actual log message                         |

By reading the logger name, you can immediately pinpoint the source of the log and understand its context within the agent's architecture.

### Debugging example

After enabling `DEBUG` logging (see [Logging level](#logging-level) above), run your agent and look for messages from the `google.adk.models.google_llm` logger. The output shows the full LLM request and response:

```text
2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm -
LLM Request:
-----------------------------------------------------------
System Instruction:
      You roll dice and answer questions about the outcome of the dice rolls.
      ...
-----------------------------------------------------------
Contents:
{"parts":[{"text":"Roll a 6 sided dice"}],"role":"user"}
{"parts":[{"function_call":{"args":{"sides":6},"name":"roll_die"}}],"role":"model"}
{"parts":[{"function_response":{"name":"roll_die","response":{"result":2}}}],"role":"user"}
-----------------------------------------------------------
Functions:
roll_die: {'sides': {'type': <Type.INTEGER: 'INTEGER'>}}
check_prime: {'nums': {'items': {'type': <Type.INTEGER: 'INTEGER'>}, 'type': <Type.ARRAY: 'ARRAY'>}}
-----------------------------------------------------------
2025-07-10 15:26:14,309 - INFO - google_adk.google.adk.models.google_llm -
LLM Response:
-----------------------------------------------------------
Text:
I have rolled a 6 sided die, and the result is 2.
...
```

From this output you can verify:

- Is the system instruction correct?
- Is the conversation history (`user` and `model` turns) accurate?
- Are the correct tools being provided to the model?
- Are the tools correctly called by the model?
- How long it takes for the model to respond?
