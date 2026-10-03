# Agent activity logging

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

Agent Development Kit (ADK) provides flexible and powerful logging capabilities
to monitor agent behavior and debug issues effectively.

## Logging philosophy

ADK's approach to logging is to provide detailed diagnostic information without
being overly verbose by default. It is designed to be configured by the
application developer, allowing you to tailor the log output to your specific
needs, whether in a development or production environment.

- **Standard Library Integration:** ADK uses the standard logging facilities of
  the host language (e.g., Python's `logging` module, Go's `log` package).
- **Structured GenAI Logging:** ADK uses OpenTelemetry to log structured events
  for GenAI requests and responses, allowing for advanced monitoring and
  debugging in cloud environments.
- **User-Configured:** While ADK provides defaults and integration with its CLI
  tools, it is ultimately the responsibility of the application developer to
  configure logging to suit their specific environment.

## Logging schema

ADK emits logs using standard library facilities and structured GenAI events via
OpenTelemetry.

### Structured GenAI logs

Structured GenAI logs emitted via OpenTelemetry follow the [Semantic Conventions
for
GenAI](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-events.md).

By default prompt content is elided in logs for security. You can enable prompt
logging using environment variables or programmatic configuration. See
[Capture prompt content](#capture-prompt-content-in-adk-web) for `adk web`, and
[Capture prompt content programmatically](#capture-prompt-content)
for setup in code.

### Log levels (Python)

The following table describes what is logged at different levels in Python when
using the standard logger:

| Level | Description | Type of Information Logged  |
| :--- | :--- | :--- |
| **`DEBUG`** | **Crucial for debugging.** The most verbose level for fine-grained diagnostic information. | <ul><li>**Full LLM Prompts:** The complete request sent to the language model, including system instructions, history, and tools.</li><li>Detailed API responses from services.</li><li>Internal state transitions and variable values.</li></ul> |
| **`INFO`** | General information about the agent's lifecycle. | <ul><li>Agent initialization and startup.</li><li>Session creation and deletion events.</li><li>Execution of a tool, including its name and arguments.</li></ul> |
| **`WARNING`** | Indicates a potential issue or deprecated feature use. The agent continues to function, but attention may be required. | <ul><li>Use of deprecated methods or parameters.</li><li>Non-critical errors that the system recovered from.</li></ul> |
| **`ERROR`** | A serious error that prevented an operation from completing. | <ul><li>Failed API calls to external services (e.g., LLM, Session Service).</li><li>Unhandled exceptions during agent execution.</li><li>Configuration errors.</li></ul> |

!!! note
    It is recommended to use `INFO` or `WARNING` in production environments.
    Only enable `DEBUG` when actively troubleshooting an issue, as `DEBUG` logs
    can be very verbose and may contain sensitive information.

## Logging in ADK Web

When running agents using the ADK's `adk web`, `adk api_server`, `adk deploy
cloud_run` and `adk deploy gke` commands, you can control the log verbosity or
destination.

### Logging level in ADK Web

To start the web server with `DEBUG` level logging, run:

```bash
adk web --log_level DEBUG path/to/your/agents_dir
```

The available log levels for the `--log_level` option are: `DEBUG`, `INFO`
(default), `WARNING`, `ERROR`, `CRITICAL`.

### Capture prompt content in ADK Web

By default a prompt content is elided in logs for security. You can enable
prompt logging using the environment variable:

```bash
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

The available values for this variable are: `NO_CONTENT`, `EVENT_ONLY`,
`SPAN_ONLY`, and `SPAN_AND_EVENT`. A boolean `true` or `1` means `EVENT_ONLY`,
which records content on the emitted log events; any value outside these four
falls back to `NO_CONTENT`. To record content on the inference span, `SPAN_ONLY`
and `SPAN_AND_EVENT` also require
`OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`.

!!! warning
    The `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` setting logs the
    full content of user prompts and agent responses. This is useful for
    debugging but may capture sensitive data or PII. In production, set this to
    false or ensure you have appropriate data handling policies in place.

### OTLP export in ADK Web

To export logs to an OTLP-compatible backend, set the standard OTel environment
variables:

```bash
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="http://your-collector:4318/v1/logs"
adk web path/to/your/agents_dir
```

!!! note
    You can also set the general `OTEL_EXPORTER_OTLP_ENDPOINT` environment
    variable if you would like to send metrics and traces to the same endpoint
    in addition to logs.


### GCP export setup in ADK Web

You can enable GCP export using the `--otel_to_cloud` flag:

```bash
adk web --otel_to_cloud path/to/your/agents_dir
```

## Programmatic setup

Programmatic setup configures the underlying logging framework and
OpenTelemetry exporters from your own code, for system-level diagnostics and
production observability. ADK uses the following logging facilities:

- **Python:** ADK uses the standard `logging` module and OpenTelemetry for
  structured GenAI logs.
- **Go:** ADK uses the `google.golang.org/adk/v2/telemetry` package for
  OpenTelemetry configuration, and the standard `log` package for general
  events, which it writes to `stderr` by default.
- **Kotlin:** ADK uses standard JVM logging facilities, defaulting to Flogger,
  and OpenTelemetry for structured GenAI logs.

### Logging level

You can set the logging level for your ADK agent using standard logging controls, as follows:

=== "Python"

    To enable detailed logging, including `DEBUG` level messages, add the following
    to the top of your script:

    ```python
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    ```

=== "Go"

    General events (such as server startup or HTTP requests) are logged using the standard Go `log` package and written to `stderr` by default.

=== "Kotlin"

    ADK uses standard JVM logging facilities (defaulting to Flogger). Configure your JVM logger backend, such as `java.util.logging` or SLF4J, to adjust log verbosity.

### Capture prompt content

=== "Python"

    You can enable full prompt logging programmatically by setting an environment
    variable:

    ```python
    import os

    os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "true"
    ```

    To scope content capture to a single run instead of the whole process, set
    `RunConfig.telemetry` rather than the environment variable:

    ```python
    from google.adk.agents.run_config import RunConfig
    from google.adk.telemetry import ContentCapturingMode, TelemetryConfig

    run_config = RunConfig(
        telemetry=TelemetryConfig(
            capture_message_content=ContentCapturingMode.SPAN_AND_EVENT,
        ),
    )
    ```

=== "Go"

    You can enable full prompt logging when initializing telemetry by exporting `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true`:

    ```go
    package main

    import (
    	"context"
    	"os"

    	"google.golang.org/adk/v2/telemetry"
    )

    func main() {
    	ctx := context.Background()

    	// Enable GenAI message content capture via the OpenTelemetry environment variable
    	os.Setenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")

    	tp, err := telemetry.New(ctx)
    	if err != nil {
    		// handle error
    	}
    	defer tp.Shutdown(ctx)
    	tp.SetGlobalOtelProviders()
    }
    ```

=== "Kotlin"

    You can enable full prompt logging by configuring the global `TelemetryConfig`:

    ```kotlin
    --8<-- "examples/kotlin/snippets/observability/LoggingExamples.kt:capture_content"
    ```

### OTLP export

=== "Python"

    To export logs to an OpenTelemetry Collector (or an OTLP-compatible backend)
    programmatically:

    ```python
    from google.adk.telemetry.setup import maybe_set_otel_providers
    import os

    os.environ["OTEL_EXPORTER_OTLP_LOGS_ENDPOINT"] = "http://your-collector:4318/v1/logs"
    os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
    maybe_set_otel_providers()
    ```

=== "Go"

    To export logs to an OTLP-compatible backend, configure the standard
    OpenTelemetry environment variables, such as `OTEL_EXPORTER_OTLP_ENDPOINT`
    or `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`. The ADK telemetry package uses these
    settings automatically when initialized.

=== "Kotlin"

    ADK Kotlin's OpenTelemetry integration emits **traces only** — it registers no
    `LoggerProvider`, so there is no OTLP log export. Application logs go to your JVM
    logging backend. To configure trace export, see the [Traces](traces.md)
    documentation.

### GCP export setup

=== "Python"

    To export logs to Google Cloud Logging programmatically, use the OpenTelemetry
    Google Cloud exporter. Here is an example in Python:

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

    !!! note "Log routing in Python"

        Outside Agent Engine, ADK preserves the OpenTelemetry event name, which
        Cloud Logging uses to route records to logs named after each event type.
        Account for these log names when configuring filters and export sinks,
        including sinks that write to BigQuery.

        On Agent Engine, detected through `GOOGLE_CLOUD_AGENT_ENGINE_ID`, ADK
        clears the event name so records use the configured log name instead.
        The default is `aiplatform.googleapis.com/reasoning_engine_stdout`.
        The event type remains available in the `event.name` label.

=== "Go"

    To export logs to Google Cloud Logging, use the `WithOtelToCloud` option:

    ```go
    package main

    import (
    	"context"
    	"google.golang.org/adk/v2/telemetry"
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

=== "Kotlin"

    ADK Kotlin emits no OpenTelemetry log records, so there is nothing for Cloud Logging
    to receive; application logs go to your JVM logging backend. ADK Kotlin **traces** can
    be sent to Google Cloud by pointing a standard OTLP exporter at `telemetry.googleapis.com`
    — see [OTLP with Google Cloud](https://cloud.google.com/stackdriver/docs/otlp/overview)
    for the required credentials, quota project and `roles/telemetry.writer` grant.

## Activity logging with plugins

ADK provides built-in plugins that capture agent activity, including user
messages, model requests and responses, tool calls, and (with
`DebugLoggingPlugin`) session state. These plugins require no changes to your
agent logic.

### Console logging with `LoggingPlugin`

To print structured activity logs to the console during execution, attach
`LoggingPlugin` to your `App`:

=== "Python"

    ```python
    from google.adk.apps import App
    from google.adk.plugins import LoggingPlugin

    app = App(
        name="my_app",
        root_agent=root_agent,
        plugins=[LoggingPlugin()],
    )
    ```

=== "Go"

    ```go
    package main

    import (
    	"context"
    	"log"
    	"os"

    	"google.golang.org/adk/v2/agent"
    	"google.golang.org/adk/v2/cmd/launcher"
    	"google.golang.org/adk/v2/cmd/launcher/full"
    	"google.golang.org/adk/v2/plugin"
    	"google.golang.org/adk/v2/plugin/loggingplugin"
    	"google.golang.org/adk/v2/runner"
    )

    func main() {
    	ctx := context.Background()
    	logPlugin := loggingplugin.MustNew("logging_plugin")

    	config := &launcher.Config{
    		AgentLoader: agent.NewSingleLoader(rootAgent),
    		PluginConfig: runner.PluginConfig{
    			Plugins: []*plugin.Plugin{logPlugin},
    		},
    	}

    	l := full.NewLauncher()
    	if err := l.Execute(ctx, config, os.Args[1:]); err != nil {
    		log.Fatalf("run failed: %v", err)
    	}
    }
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/observability/LoggingExamples.kt:logging_plugin"
    ```

### Full debug capture to a file with `DebugLoggingPlugin`

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.23.0</span><span class="lst-kotlin">Kotlin v0.6.0</span>
</div>

To record complete interaction data as human-readable YAML appended to
`adk_debug.yaml` rather than truncated console output, use
`DebugLoggingPlugin`:

=== "Python"

    ```python
    from google.adk.apps import App
    from google.adk.plugins import DebugLoggingPlugin

    app = App(
        name="my_app",
        root_agent=root_agent,
        plugins=[
            DebugLoggingPlugin(
                output_path="adk_debug.yaml",
                include_session_state=True,
                include_system_instruction=True,
            ),
        ],
    )
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/observability/LoggingExamples.kt:debug_logging_plugin"
    ```

!!! warning
    The output file holds raw prompts, tool arguments, and session state.
    Although ADK automatically redacts credentials and `temp:`-scoped state
    keys in Python, treat the output file as sensitive.

## Understanding log output

### Sample Python log entry

```text
2025-07-08 11:22:33,456 - DEBUG - google_adk.google.adk.models.google_llm - LLM Request: contents { ... }
```

| Log Segment                     | Format Specifier | Meaning                                        |
| ------------------------------- | ---------------- | ---------------------------------------------- |
| `2025-07-08 11:22:33,456`       | `%(asctime)s`    | Timestamp                                      |
| `DEBUG`                         | `%(levelname)s`  | Severity level                                 |
| `google_adk.google.adk.models.google_llm`  | `%(name)s`       | Logger name (the module that produced the log) |
| `LLM Request: contents { ... }` | `%(message)s`    | The actual log message                         |

By reading the logger name, you can immediately pinpoint the source of the log
and understand its context within the agent's architecture.
ADK loggers are named `google_adk.` followed by the module's fully-qualified
name, so every ADK logger is a child of the `google_adk` logger. Configure them
as a group with `logging.getLogger("google_adk")`.

### Debugging example

After enabling `DEBUG` logging (see [Logging level](#logging-level) above), run
your agent and look for messages from the
`google_adk.google.adk.models.google_llm` logger.
The output shows the full LLM request and response:

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
