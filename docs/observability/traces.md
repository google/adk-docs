# Agent activity traces

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.17.0</span><span class="lst-go">Go v1.0.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

Agent Development Kit (ADK) provides distributed tracing capabilities to help you visualize the end-to-end journey of a request as it travels through your agent's architecture. While metrics tell you *how long* a process took and logs tell you *what* happened, traces connect these events, showing you exactly *where* the time was spent and the hierarchical relationship between LLM reasoning, tool calls, and external APIs.

## Traces philosophy

ADK's approach to tracing is built on standard protocols to ensure seamless integration with your existing observability stack.

*   **OpenTelemetry Semantic Conventions:** ADK implements the OpenTelemetry (OTel) [Semantic Conventions for GenAI](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md). This ensures that trace spans and attributes are recorded under standard, predictable names.
*   **OTLP Wire Format:** ADK emits data using the standard OTLP format, ensuring that your traces will seamlessly integrate into any OTel-compatible backend (e.g., Google Cloud Trace, Jaeger, Grafana Tempo, Datadog).
*   **Hierarchical Visualization:** Traces are organized into "Spans." An agent run is a root span, which contains child spans for LLM operations, which may in turn contain child spans for tool executions. This creates a clear "waterfall" view of the agent's reasoning loop.
*   **Context Propagation:** ADK automatically passes trace context across process boundaries, ensuring that if your agent calls an external microservice via a tool, that service's spans are linked to the agent's root trace.

---

## Traces schema

When tracing is enabled, ADK automatically instruments key operations following the OpenTelemetry GenAI Semantic Conventions for Agents. A typical trace waterfall includes the following spans:

| Span Name | Type | Description | Key Attributes |
| :--- | :--- | :--- | :--- |
| **[`invoke_agent {agent.name}`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-client-span)** | Client / Internal Span | Describes GenAI agent invocation over a remote service or locally. Represents the lifecycle of an agent interaction.| `gen_ai.operation.name`, `gen_ai.agent.name`, `gen_ai.agent.description`, `gen_ai.conversation.id` |
| **[`invoke_workflow {workflow.name}`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-workflow-span)** | Child Span | Describes the invocation of a multi-step agentic workflow. | `gen_ai.operation.name`, `gen_ai.workflow.name`, `gen_ai.conversation.id`, `gen_ai.workflow.nested` (nested workflows only) |
| **[`execute_tool {tool.name}`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#execute-tool-span)**       | Child Span | Represents the execution of a specific tool or function call requested by the GenAI system.| `gen_ai.operation.name`, `gen_ai.tool.name`, `gen_ai.tool.description`, `gen_ai.tool.type`, `gen_ai.tool.call.id`, `error.type`|
| **[`generate_content {model.name}`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md)** | Internal Span | Represents the invocation of the underlying language model (via the GenAI SDK) to generate content. It tracks the request parameters, response details, and usage metrics. | `gen_ai.operation.name`, `gen_ai.system`, `gen_ai.request.model`, `gen_ai.agent.name`, `gen_ai.conversation.id`, `gen_ai.response.finish_reasons`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` |

---

## Traces export setup

### Traces export in ADK Web

If you are running your agent using the `adk web` or `adk api_server` CLI commands, you can configure trace exports.

#### OTLP export

To export traces to an OTLP-compatible backend, set the standard OTel environment variables:

```bash
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="http://your-collector:4318/v1/traces"
adk web path/to/your/agents_dir
```

> **Note:**  You can also set the general `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable if you would like to send metrics and logs to the same endpoint in addition to traces.


#### GCP export

To enable trace export to Google Cloud Trace, use the `--otel_to_cloud` flag:

```bash
adk web --otel_to_cloud path/to/your/agents_dir
```

#### Capture message content and payloads in spans

By default in local Python development, ADK records prompts, LLM responses, tool arguments, and tool responses as JSON attributes on spans under the `gcp.vertex.agent.*` namespace (`gcp.vertex.agent.llm_request`, `gcp.vertex.agent.llm_response`, `gcp.vertex.agent.tool_call_args`, `gcp.vertex.agent.tool_response`, and `gcp.vertex.agent.data`).

To prevent sensitive data or PII from being captured on these spans, set `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false`:

```bash
export ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false
adk web path/to/your/agents_dir
```

When set to `false` (or `0`), these payload attributes are replaced with empty JSON string placeholders (`"{}"`).

Additionally, you can configure prompt and response message content on spans following the OpenTelemetry GenAI Semantic Conventions via `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`:

```bash
export OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=SPAN_ONLY
```

The available values are `NO_CONTENT` (default), `EVENT_ONLY`, `SPAN_ONLY`, and `SPAN_AND_EVENT`. Capturing content on spans requires `SPAN_ONLY` or `SPAN_AND_EVENT`, along with opting into experimental GenAI semantic conventions via `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`.

!!! warning
    Span content capture records raw user inputs, model outputs, and tool call arguments. In production environments, ensure appropriate data governance policies are in place, or disable span content via `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false` (which is set automatically by `adk deploy agent_engine --otel_to_cloud`).

## Programmatic traces export

You can also configure trace export programmatically in your application code.

### Python programmatic setup

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

#### Capture prompt and span content programmatically

You can toggle span payload capture globally via environment variables:

```python
import os

# Disable custom ADK payload attributes on spans (sets attributes to "{}")
os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] = "false"

# Or configure OpenTelemetry GenAI span message capturing
os.environ["OTEL_SEMCONV_STABILITY_OPT_IN"] = "gen_ai_latest_experimental"
os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "SPAN_ONLY"
```

To configure content capture per invocation rather than process-wide, set `RunConfig.telemetry`:

```python
from google.adk.agents.run_config import RunConfig
from google.adk.telemetry import ContentCapturingMode, TelemetryConfig

run_config = RunConfig(
    telemetry=TelemetryConfig(
        capture_message_content=ContentCapturingMode.SPAN_ONLY,
        genai_semconv_stability_opt_in="experimental",
    ),
)
```

Setting `capture_message_content` to `SPAN_ONLY` or `SPAN_AND_EVENT` enables content capture on both experimental OpenTelemetry spans and ADK spans, while `EVENT_ONLY` or `NO_CONTENT` redacts span payloads.

### Kotlin programmatic setup

In Kotlin, ADK automatically uses the `GlobalOpenTelemetry` instance to export traces. You should configure your OpenTelemetry SDK before starting the agent.

#### OTLP export setup

To enable tracing and export spans to an OpenTelemetry Collector, configure the OpenTelemetry SDK and register it globally:

```kotlin
--8<-- "examples/kotlin/snippets/observability/SetupExample.kt:full_example"
```
