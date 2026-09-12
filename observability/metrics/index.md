# Agent activity metrics

Supported in ADKPython v1.32.0Kotlin v0.1.0

Agent Development Kit (ADK) provides built-in, vendor-neutral metrics collection to help you understand the performance, cost, and usage patterns of your agents. While logs provide a detailed narrative of *what* happened, metrics give you aggregated, quantitative data to answer *how often* and *how fast* things are happening.

## Metrics philosophy

ADK's approach to metrics is designed to be lightweight, standardized, and entirely agnostic to your choice of monitoring backend.

- **OpenTelemetry Semantic Conventions:** ADK implements the OpenTelemetry (OTel) [Semantic Conventions for GenAI](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-metrics.md). This ensures that metrics are recorded under standard, predictable attribute and metric names.
- **OTLP Wire Format:** ADK emits data using the standard OTLP format, ensuring that your metrics will seamlessly integrate into any OTel-compatible backend (e.g., Prometheus, Datadog, SigNoz, Google Cloud Monitoring).
- **Cost and Performance Focused:** Metrics are significantly less costly and more performant than logs or traces when performing analytics over large swathes of data. ADK tracks the most critical signals for LLM applications: token consumption, request latency, and tool execution reliability.
- **Vendor-Neutral Export:** ADK does not lock you into a specific metrics pipeline. You instantiate standard OTel meter providers and export data wherever your infrastructure demands.

______________________________________________________________________

## Metrics schema

When metrics are enabled, ADK automatically instruments the agent's lifecycle, workflow steps, and tool executions based on the OpenTelemetry GenAI Semantic Conventions. The following core metrics are emitted:

| Metric Name                               | Type                | Description                                                                                            | Key Attributes (Dimensions)                                                                                                                |
| ----------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **`gen_ai.invoke_agent.duration`**        | Histogram (seconds) | The total time taken for an agent to process a prompt and return a response.                           | `gen_ai.agent.name`, `error.type`                                                                                                          |
| **`gen_ai.invoke_workflow.duration`**     | Histogram (seconds) | The time taken to run a workflow.                                                                      | `gen_ai.operation.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (nested workflows only), `error.type`                            |
| **`gen_ai.execute_tool.duration`**        | Histogram (seconds) | The execution latency of individual tools called by the agent. Useful for spotting slow external APIs. | `gen_ai.agent.name`, `gen_ai.tool.name`, `gen_ai.tool.type`, `error.type`                                                                  |
| **`gen_ai.invoke_agent.inference_calls`** | Histogram (count)   | The number of inference (model) calls made during one agent invocation.                                | `gen_ai.agent.name`                                                                                                                        |
| **`gen_ai.invoke_agent.tool_calls`**      | Histogram (count)   | The number of tool calls made during one agent invocation.                                             | `gen_ai.agent.name`                                                                                                                        |
| **`gen_ai.client.operation.duration`**    | Histogram (seconds) | The latency of a single model `generate_content` call.                                                 | `gen_ai.agent.name`, `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `error.type`        |
| **`gen_ai.client.token.usage`**           | Histogram (tokens)  | Token consumption per model call, split into input and output by `gen_ai.token.type`.                  | `gen_ai.agent.name`, `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.token.type` |

______________________________________________________________________

## Metrics export setup

### Metrics export in ADK Web

If you are running your agent using the `adk web` or `adk api_server` CLI commands, you can configure metrics export.

#### OTLP export

To export metrics to an OTLP-compatible backend, set the standard OTel environment variables:

```bash
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="http://your-collector:4318/v1/metrics"
adk web path/to/your/agents_dir
```

> **Note:** You can also set the general `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable if you would like to send traces and logs to the same endpoint in addition to metrics.

#### GCP export

To enable metrics export to Google Cloud Monitoring, use the `--otel_to_cloud` flag:

```bash
adk web --otel_to_cloud path/to/your/agents_dir
```

### Programmatic metrics export

You can also configure metrics export programmatically in your application code.

#### OTLP export setup

To enable metrics and export them to an OpenTelemetry Collector (or an OTLP-compatible backend) programmatically:

```python
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

os.environ["OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"] = "http://your-collector:4318/v1/metrics"
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers()
```

#### GCP export setup

To export metrics to Google Cloud Monitoring programmatically, use the OpenTelemetry Google Cloud exporter. Here is an example in Python:

```python
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

gcp_exporters = get_gcp_exporters(
  enable_cloud_metrics = True,
)
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers([gcp_exporters])
```

### Kotlin programmatic setup

In Kotlin, ADK uses the standard `GlobalOpenTelemetry` to manage metrics. Configuring your OpenTelemetry SDK with a `MeterProvider` will enable metric collection.

#### OTLP export setup

To enable metrics and export them to an OpenTelemetry Collector, configure the OpenTelemetry SDK with the appropriate metrics exporter:

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
