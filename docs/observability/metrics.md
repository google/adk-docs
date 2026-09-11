# Agent activity metrics

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.32.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

Agent Development Kit (ADK) provides built-in, vendor-neutral metrics collection to help you understand the performance, cost, and usage patterns of your agents. While logs provide a detailed narrative of *what* happened, metrics give you aggregated, quantitative data to answer *how often* and *how fast* things are happening.

## Metrics philosophy

ADK's approach to metrics is designed to be lightweight, standardized, and entirely agnostic to your choice of monitoring backend.

*   **OpenTelemetry Semantic Conventions:** ADK implements the OpenTelemetry (OTel) [Semantic Conventions for GenAI](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-metrics.md). This ensures that metrics are recorded under standard, predictable attribute and metric names.
*   **OTLP Wire Format:** ADK emits data using the standard OTLP format, ensuring that your metrics will seamlessly integrate into any OTel-compatible backend (e.g., Prometheus, Datadog, SigNoz, Google Cloud Monitoring).
*   **Cost and Performance Focused:** Metrics are significantly less costly and more performant than logs or traces when performing analytics over large swathes of data. ADK tracks the most critical signals for LLM applications: token consumption, request latency, and tool execution reliability.
*   **Vendor-Neutral Export:** ADK does not lock you into a specific metrics pipeline. You instantiate standard OTel meter providers and export data wherever your infrastructure demands.

---

## Metrics schema

When metrics are enabled, ADK automatically instruments the agent's lifecycle, workflow steps, and tool executions based on the OpenTelemetry GenAI Semantic Conventions. The following core metrics are emitted:

| Metric Name | Type | Description | Key Attributes (Dimensions) |
| :--- | :--- | :--- | :--- |
| **`gen_ai.invoke_agent.duration`** | Histogram (seconds) | The total time taken for an agent to process a prompt and return a response. | `gen_ai.agent.name`, `error.type` |
| **`gen_ai.invoke_workflow.duration`** | Histogram (seconds) | The time taken to run a workflow. | `gen_ai.operation.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (nested workflows only), `error.type` |
| **`gen_ai.execute_tool.duration`** | Histogram (seconds) | The execution latency of individual tools called by the agent. Useful for spotting slow external APIs. | `gen_ai.agent.name`, `gen_ai.tool.name`, `gen_ai.tool.type`, `error.type` |
| **`gen_ai.invoke_agent.inference_calls`** | Histogram (count) | The number of inference (model) calls made during one agent invocation. | `gen_ai.agent.name` |
| **`gen_ai.invoke_agent.tool_calls`** | Histogram (count) | The number of tool calls made during one agent invocation. | `gen_ai.agent.name` |
| **`gen_ai.client.operation.duration`** | Histogram (seconds) | The latency of a single model `generate_content` call. | `gen_ai.agent.name`, `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `error.type` |
| **`gen_ai.client.token.usage`** | Histogram (tokens) | Token consumption per model call, split into input and output by `gen_ai.token.type`. | `gen_ai.agent.name`, `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.token.type` |

### Experimental metrics

ADK emits additional telemetry under the `adk.experimental.*` namespace, which covers span attributes as well as the metrics below. Nothing in it is part of an OpenTelemetry semantic convention yet, so names, attributes, and meaning can still change between releases. Explore them freely, and expect to revisit anything long-lived you build on them as the names settle.

The metrics below aggregate token spend and call counts over a whole agent invocation or a whole workflow, the grain above the single model call that `gen_ai.client.*` measures, so you can ask what one turn cost without summing model calls yourself.

They are off by default. To turn them on, set the environment variable:

```bash
export ADK_EXPERIMENTAL_TELEMETRY=true
```

You can also opt in per request, which takes precedence over the environment variable:

```python
from google.adk.agents.run_config import RunConfig
from google.adk.telemetry import TelemetryConfig

run_config = RunConfig(
    telemetry=TelemetryConfig(adk_experimental_telemetry_opt_in=True)
)
```

When neither is set, none of the metrics below are recorded.

The eight `invoke_workflow` rows need one more thing: telemetry schema v2, which is the default on Vertex AI Agent Engine and off everywhere else. Set `ADK_TELEMETRY_SCHEMA_VERSION_OPT_IN=2` anywhere else, or those rows stay empty. The `invoke_agent` rows are unaffected, and an app built on the `Workflow` engine records per-node datapoints under either version.

| Metric Name | Type | Description | Key Attributes (Dimensions) |
| :--- | :--- | :--- | :--- |
| **`adk.experimental.invoke_agent.input_tokens`** | Histogram (tokens) | Input (prompt) tokens summed over one agent invocation, including server-side tool results and cached prompt tokens. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.output_tokens`** | Histogram (tokens) | Output (completion) tokens summed over one agent invocation, including reasoning tokens and the tokens spent emitting tool calls. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.total_tokens`** | Histogram (tokens) | Input plus output tokens for one agent invocation. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.cache_read.input_tokens`** | Histogram (tokens) | Input tokens served from a provider-managed cache, summed over one agent invocation. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.reasoning.output_tokens`** | Histogram (tokens) | Output tokens spent on reasoning (chain-of-thought / extended thinking), summed over one agent invocation. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.tool.input_tokens`** | Histogram (tokens) | Input tokens from server-side tool results the model fed back to itself within one request, such as code execution or search grounding. Zero for client-side function tools. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_workflow.input_tokens`** | Histogram (tokens) | The `input_tokens` above, summed across every agent that ran in one workflow invocation. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (nested workflows only) |
| **`adk.experimental.invoke_workflow.output_tokens`** | Histogram (tokens) | The `output_tokens` above, summed across every agent that ran in one workflow invocation. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (nested workflows only) |
| **`adk.experimental.invoke_workflow.total_tokens`** | Histogram (tokens) | The `total_tokens` above, summed across every agent that ran in one workflow invocation. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (nested workflows only) |
| **`adk.experimental.invoke_workflow.cache_read.input_tokens`** | Histogram (tokens) | The `cache_read.input_tokens` above, summed across every agent that ran in one workflow invocation. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (nested workflows only) |
| **`adk.experimental.invoke_workflow.reasoning.output_tokens`** | Histogram (tokens) | The `reasoning.output_tokens` above, summed across every agent that ran in one workflow invocation. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (nested workflows only) |
| **`adk.experimental.invoke_workflow.tool.input_tokens`** | Histogram (tokens) | The `tool.input_tokens` above, summed across every agent that ran in one workflow invocation. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (nested workflows only) |
| **`adk.experimental.invoke_workflow.inference_calls`** | Histogram (count) | The number of inference (model) calls made across one workflow invocation. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (nested workflows only) |
| **`adk.experimental.invoke_workflow.tool_calls`** | Histogram (count) | The number of tool calls made across one workflow invocation. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (nested workflows only) |

!!! warning
    A nested workflow records a datapoint of its own, and its totals are also
    folded into every workflow enclosing it, so summing an `invoke_workflow`
    metric across all datapoints double counts.

`gen_ai.workflow.nested` is set only on nested workflows, so excluding it leaves the outermost workflow alone, and that datapoint covers the whole turn. The workflow metrics carry no agent dimension, since a value spanning a whole workflow cannot be attributed to a single agent. They carry two names instead: `gen_ai.workflow.name` joins to `gen_ai.invoke_workflow.duration`, while `adk.experimental.root_agent.name` identifies the app, and the two disagree when a turn enters at a sub-agent.

---

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
--8<-- "examples/kotlin/snippets/observability/SetupExample.kt:full_example"
```
