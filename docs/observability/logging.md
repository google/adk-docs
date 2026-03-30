# Agent activity logging

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Agent Development Kit (ADK) provides flexible and powerful logging capabilities to monitor agent behavior and debug issues effectively. Understanding how to configure and interpret these logs is crucial for monitoring agent behavior and debugging issues effectively.

## Logging Philosophy

ADK's approach to logging is to provide detailed diagnostic information without being overly verbose by default. It is designed to be configured by the application developer, allowing you to tailor the log output to your specific needs, whether in a development or production environment.

- **Standard Library Integration:** ADK uses the standard logging facilities of the host language (e.g., Python's `logging` module, Go's `log` package).
- **Structured GenAI Logging:** ADK uses OpenTelemetry to log structured events for GenAI requests and responses, allowing for advanced monitoring and debugging in cloud environments.
- **User-Configured:** While ADK provides defaults and integration with its CLI tools, it is ultimately the responsibility of the application developer to configure logging to suit their specific environment.

---

## Configuring Logging in Python

In Python, ADK uses the standard `logging` module.

### Example Configuration

To enable detailed logging, including `DEBUG` level messages, add the following to the top of your script:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
```

### Configuring Logging with the ADK CLI (Python)

When running Python agents using the ADK's built-in web or API servers, you can easily control the log verbosity directly from the command line. The `adk web`, `adk api_server`, and `adk deploy cloud_run` commands all accept a `--log_level` option.

**Example using `adk web`:**

```bash
adk web --log_level DEBUG path/to/your/agents_dir
```

The available log levels for the `--log_level` option are: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, `CRITICAL`.

### Log Levels (Python)

| Level | Description | Type of Information Logged  |
| :--- | :--- | :--- |
| **`DEBUG`** | **Crucial for debugging.** | <ul><li>**Full LLM Prompts:** The complete request sent to the language model.</li><li>Detailed API responses.</li></ul> |
| **`INFO`** | General lifecycle info. | <ul><li>Agent initialization and startup.</li><li>Execution of a tool, including its name and arguments.</li></ul> |
| **`WARNING`** | Potential issues. | <ul><li>Use of deprecated methods.</li><li>Non-critical recovered errors.</li></ul> |
| **`ERROR`** | Serious errors. | <ul><li>Failed API calls to external services.</li><li>Unhandled exceptions.</li></ul> |

---

## Configuring Logging in Go

In Go, ADK uses the standard `log` package for general events and OpenTelemetry for GenAI activity logging.

### OpenTelemetry Logging

ADK Go uses OpenTelemetry (OTel) to log GenAI requests and responses. By default, prompt content is elided in logs for security. You can enable prompt logging using environment variables or programmatic configuration.

#### Enabling Prompt Logging

Set the following environment variable to `true` to include full prompts in your OTel logs:

```bash
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

#### Programmatic Configuration

You can configure telemetry providers using the `google.golang.org/adk/telemetry` package.

```go
import (
	"context"
	"google.golang.org/adk/telemetry"
)

func main() {
	ctx := context.Background()
	
	// Initialize telemetry with prompt content logging enabled
	tp, err := telemetry.New(ctx, 
		telemetry.WithGenAICaptureMessageContent(true),
		// Add other options like WithOtelToCloud(true) for GCP export
	)
	if err != nil {
		// handle error
	}
	defer tp.Shutdown(ctx)
	
	// Register as global OTel providers
	tp.SetGlobalOtelProviders()
	
	// Your ADK agent code follows...
}
```

### General Logging

General events (like server startup or HTTP requests) are logged using the standard Go `log` package. These logs are written to `stderr` by default.

### Configuring Logging with the ADK Go Launcher

When using the ADK Go `full.Launcher` or `prod.Launcher`, telemetry is automatically initialized. You can enable GCP export using the `-otel_to_cloud` flag:

```bash
go run main.go web -otel_to_cloud a2a
```

---

## Reading and Understanding the Logs

The structure of logs depends on your configuration. Structured GenAI logs emitted via OpenTelemetry follow the [Semantic Conventions for GenAI](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-events.md).

### Sample Python Log Entry

```text
2025-07-08 11:22:33,456 - DEBUG - google_adk.models.google_llm - LLM Request: contents { ... }
```

### Debugging with Logs: A Practical Example (Python)

**Scenario:** Your agent is not producing the expected output, and you suspect the prompt being sent to the LLM is incorrect.

1.  **Enable DEBUG Logging:** Set the logging level to `DEBUG`.
2.  **Inspect the Logs:** Look for `LLM Request:` from the `google_adk.models.google_llm` logger.
3.  **Analyze the Prompt:** Verify:
    -   Is the system instruction correct?
    -   Is the conversation history accurate?
    -   Are the correct tools being provided?
