# Agent activity traces

Supported in ADKPython v1.17.0Go v1.0.0Kotlin v0.1.0

Agent Development Kit (ADK) provides distributed tracing capabilities to help you visualize the end-to-end journey of a request as it travels through your agent's architecture. While metrics tell you *how long* a process took and logs tell you *what* happened, traces connect these events, showing you exactly *where* the time was spent and the hierarchical relationship between LLM reasoning, tool calls, and external APIs.

## Traces philosophy

ADK's approach to tracing is built on standard protocols to ensure seamless integration with your existing observability stack.

- **OpenTelemetry Semantic Conventions:** ADK implements the OpenTelemetry (OTel) [Semantic Conventions for GenAI](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md). This ensures that trace spans and attributes are recorded under standard, predictable names.
- **OTLP Wire Format:** ADK emits data using the standard OTLP format, ensuring that your traces will seamlessly integrate into any OTel-compatible backend (e.g., Google Cloud Trace, Jaeger, Grafana Tempo, Datadog).
- **Hierarchical Visualization:** Traces are organized into "Spans." An agent run is a root span, which contains child spans for LLM operations, which may in turn contain child spans for tool executions. This creates a clear "waterfall" view of the agent's reasoning loop.
- **Context Propagation:** ADK automatically passes trace context across process boundaries, ensuring that if your agent calls an external microservice via a tool, that service's spans are linked to the agent's root trace.

______________________________________________________________________

## Traces schema

When tracing is enabled, ADK automatically instruments key operations following the OpenTelemetry GenAI Semantic Conventions for Agents. A typical trace waterfall includes the following spans:

| Span Name                                                                                                                                         | Type                   | Description                                                                                                                                                                | Key Attributes                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[`invoke_agent`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-client-span)** | Client / Internal Span | Describes GenAI agent invocation over a remote service or locally. Represents the lifecycle of an agent interaction.                                                       | `gen_ai.agent.name`, `gen_ai.system`                                                                                                                                                                                                                                         |
| **[`invoke_workflow`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-workflow-span)**  | Child Span             | Describes the invocation of a multi-step agentic workflow.                                                                                                                 | `gen_ai.workflow.name`, `gen_ai.system`                                                                                                                                                                                                                                      |
| **[`execute_tool`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#execute-tool-span)**        | Child Span             | Represents the execution of a specific tool or function call requested by the GenAI system.                                                                                | `gen_ai.tool.name`, `gen_ai.system`                                                                                                                                                                                                                                          |
| **[`generate_content {model.name}`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md)**               | Internal Span          | Represents the invocation of the underlying language model (via the GenAI SDK) to generate content. It tracks the request parameters, response details, and usage metrics. | `gen_ai.operation.name`, `gen_ai.system`, `gen_ai.request.model`, `gen_ai.agent.name`, `gen_ai.conversation.id`, `user.id`, `gen_ai.request.top_p`, `gen_ai.request.max_tokens`, `gen_ai.response.finish_reasons`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` |

______________________________________________________________________

## Traces export setup

### Traces export in ADK Web

If you are running your agent using the `adk web` or `adk api_server` CLI commands, you can configure trace exports.

#### OTLP export

To export traces to an OTLP-compatible backend, set the standard OTel environment variables:

```bash
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="http://your-collector:4318/v1/traces"
adk web path/to/your/agents_dir
```

> **Note:** You can also set the general `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable if you would like to send metrics and logs to the same endpoint in addition to traces.

#### GCP export

To enable trace export to Google Cloud Trace, use the `--otel_to_cloud` flag:

```bash
adk web --otel_to_cloud path/to/your/agents_dir
```

### Programmatic traces export

You can also configure trace export programmatically in your application code.

#### OTLP export setup

To enable tracing and export spans to an OpenTelemetry Collector programmatically:

```python
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = "http://your-collector:4318/v1/traces"
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers()
```

#### GCP export setup

To export traces to Google Cloud Trace programmatically, use the OpenTelemetry Google Cloud exporter. Here is an example in Python:

```python
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

gcp_exporters = get_gcp_exporters(
  enable_cloud_tracing = True,
)
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers([gcp_exporters])
```

### Kotlin programmatic setup

In Kotlin, ADK automatically uses the `GlobalOpenTelemetry` instance to export traces. You should configure your OpenTelemetry SDK before starting the agent.

#### OTLP export setup

To enable tracing and export spans to an OpenTelemetry Collector, configure the OpenTelemetry SDK and register it globally:

```kotlin
// 1. Configure OpenTelemetry (Traces)
// ADK Kotlin uses GlobalOpenTelemetry to resolve its tracer on the JVM.
val spanExporter = OtlpGrpcSpanExporter.builder().setEndpoint("http://localhost:4317").build()

val resource =
    Resource.getDefault()
        .merge(
            Resource.create(
                Attributes.of(AttributeKey.stringKey("service.name"), "my-kotlin-agent"),
            ),
        )

val tracerProvider =
    SdkTracerProvider.builder()
        .addSpanProcessor(BatchSpanProcessor.builder(spanExporter).build())
        .setResource(resource)
        .build()

OpenTelemetrySdk.builder().setTracerProvider(tracerProvider).buildAndRegisterGlobal()

// 2. Optional: Configure ADK Telemetry behavior
// Enable capturing full message content in traces (use with caution in production)
TelemetryConfig.captureMessageContent = true

// 3. Initialize Agent and Runner with LoggingPlugin for console output
val agent = LlmAgent(name = "my_agent", model = Gemini(name = "gemini-flash-latest"))

val runner =
    InMemoryRunner(
        App(appName = "my_agent", rootAgent = agent, plugins = listOf(LoggingPlugin())),
    )

// The runner will now automatically emit traces via GlobalOpenTelemetry
// and log activity to the console via the LoggingPlugin.
runner.run(
    userId = "user123",
    sessionId = "session456",
    newMessage = Content.fromText(Role.USER, "Hello!"),
)
```
