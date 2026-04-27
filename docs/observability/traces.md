# Agent activity traces

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Agent Development Kit (ADK) provides distributed tracing capabilities to help you visualize the end-to-end journey of a request as it travels through your agent's architecture. While metrics tell you *how long* a process took and logs tell you *what* happened, traces connect these events, showing you exactly *where* the time was spent and the hierarchical relationship between LLM reasoning, tool calls, and external APIs.

## Traces Philosophy

ADK's approach to tracing is built on standard protocols to ensure seamless integration with your existing observability stack.

*   **OpenTelemetry Native:** ADK implements the OpenTelemetry (OTel) [Semantic Conventions for GenAI](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md). Your traces will render perfectly in any OTel-compatible backend (e.g., Jaeger, Zipkin, Datadog, Google Cloud Trace).
*   **Hierarchical Visualization:** Traces are organized into "Spans." An agent run is a root span, which contains child spans for LLM operations, which may in turn contain child spans for tool executions. This creates a clear "waterfall" view of the agent's reasoning loop.
*   **Context Propagation:** ADK automatically passes trace context across process boundaries, ensuring that if your agent calls an external microservice via a tool, that service's spans are linked to the agent's root trace.

---

## Core Trace Spans

When tracing is enabled, ADK automatically instruments key operations following the OpenTelemetry GenAI Semantic Conventions for Agents. A typical trace waterfall includes the following spans:

| Span Name | Type | Description | Key Attributes |
| :--- | :--- | :--- | :--- |
| **[`create_agent`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#create-agent-span)** | Client Span | Describes GenAI agent creation and is usually applicable when working with remote agent services. | `gen_ai.agent.name`, `gen_ai.system`, `server.address` |
| **[`invoke_agent`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-client-span)** | Client / Internal Span | Describes GenAI agent invocation over a remote service or locally. Represents the lifecycle of an agent interaction. | `gen_ai.agent.name`, `gen_ai.system` |
| **[`invoke_workflow`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-workflow-span)** | Child Span | Describes the invocation of a multi-step agentic workflow. | `gen_ai.workflow.name`, `gen_ai.system` |
| **[`execute_tool`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#execute-tool-span)** | Child Span | Represents the execution of a specific tool or function call requested by the GenAI system. | `gen_ai.tool.name`, `gen_ai.system` |

---

## Configuring Traces with the ADK CLI

If you are running your agent using the `adk web` or `adk api_server` CLI commands, you can enable OTLP trace exports via environment variables:
```bash
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="http://your-collector:4318/v1/traces"
export OTEL_TRACES_EXPORTER="otlp"

adk web path/to/your/agents_dir
```

## Configuring Traces in Python

In Python, ADK traces are captured by configuring the standard `opentelemetry` Python SDK.

### Example Configuration (OTLP Export)

To enable tracing and export spans to an OpenTelemetry Collector, set up your `TracerProvider` before initializing your agent:
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# 1. Define your service resource
resource = Resource.create({"service.name": "my-adk-agent"})

# 2. Configure the OTLP Exporter
exporter = OTLPSpanExporter(endpoint="http://your-collector:4318/v1/traces")
processor = BatchSpanProcessor(exporter)

# 3. Set the global TracerProvider
provider = TracerProvider(resource=resource)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# 4. Your ADK agent code follows...
# from google.adk.agents import Agent
# agent = Agent(name="my_agent", ...)
```
