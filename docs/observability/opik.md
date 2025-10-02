# Agent Observability with Opik

[Opik](https://www.comet.com/opik/) is Comet's observability, evaluation, and optimization platform for LLM and agent workloads. It captures the full execution context of your Google ADK applications—including agent runs, tool invocations, model calls, and custom business logic—so you can debug faster, monitor cost and latency, and ship production-ready agents with confidence.

## Why Opik for ADK?

Opik extends ADK's native OpenTelemetry support with:

- **Rich span data** – Every agent, tool, and LLM call is logged with prompts, responses, metadata, and token usage for all model calls.
- **Automatic cost tracking** – Built-in cost calculators let you surface spend per span, per agent, or per project without additional code.
- **Multi-agent visualization** – The `track_adk_agent_recursive` helper renders hierarchical graphs of complex agent workflows directly in the UI.
- **Thread-aware tracing** – ADK session IDs are automatically mapped to Opik threads so multi-turn conversations stay grouped together.
- **Error analytics** – Exceptions raised inside agents, models, or tools are captured with stack traces and surfaced in the Opik dashboard.

## Installation

Install Opik alongside Google ADK:

```bash
pip install opik google-adk
```

## Configure Opik

Initialize the Opik Python SDK using whichever method fits your deployment. The quickest way during development is:

```bash
opik configure
```

You can also call `opik.configure()` from code or set the `OPIK_API_KEY`, `OPIK_WORKSPACE`, and `OPIK_PROJECT_NAME` environment variables. See the [Python SDK configuration guide](https://www.comet.com/docs/opik/tracing/sdk_configuration/) for the full matrix covering cloud, enterprise, and self-hosted deployments.

## Configure Google ADK

Opik works with any ADK-supported model provider. For the example below we authenticate to Gemini through Google AI Studio:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY="<your-gemini-api-key>"
```

If you deploy on Vertex AI instead, set `GOOGLE_GENAI_USE_VERTEXAI=TRUE` and configure `GOOGLE_CLOUD_PROJECT` plus `GOOGLE_CLOUD_LOCATION` (or use Application Default Credentials).

## Basic agent setup with OpikTracer

The `OpikTracer` automatically captures agent execution, tool calls, and model interactions. Attach it to your ADK agents as shown below:

```python
from google.adk.agents import LlmAgent
from google.adk import runners
from opik.integrations.adk import OpikTracer

weather_agent = LlmAgent(
    name="weather_agent",
    instruction="You provide friendly weather updates.",
    model="gemini-2.0-flash",
)

tracer = OpikTracer(project_name="adk-weather-demo")

runner = runners.Runner(
    agent=weather_agent,
    app_name="weather_app",
    before_agent_callback=tracer.before_agent_callback,
    after_agent_callback=tracer.after_agent_callback,
    before_model_callback=tracer.before_model_callback,
    after_model_callback=tracer.after_model_callback,
)

response = runner.run(user_request="What's the weather in New York?")
tracer.flush()  # ensure spans are delivered before the script exits
```

Open the Opik dashboard and navigate to your project to inspect the trace. You will see the agent span, the downstream LLM call, tool invocations (if any), token usage, and cost estimates.

## Multi-agent and session workflows

For complex graphs, instrument your root agent with `track_adk_agent_recursive` to automatically trace every nested ADK agent:

```python
from opik.integrations.adk import track_adk_agent_recursive

track_adk_agent_recursive(weather_agent)
```

When you run ADK sessions, Opik maps the `session_id` to a thread so multi-turn conversations stay grouped. Metadata such as `user_id` and `app_name` is recorded automatically.

## Hybrid tracing with `@track`

The Opik tracer is fully compatible with the [`@opik.track`](https://www.comet.com/docs/opik/tracing/log_traces/#track) decorator. You can:

- Call ADK agents from inside tracked functions and keep parent/child span relationships intact.
- Decorate tool functions to capture custom business logic alongside ADK-managed spans.

## Troubleshooting

- Always await all events when using `Runner.run_async`. Exiting early prevents the tracer from closing spans.
- Call `tracer.flush()` before your script exits to guarantee that buffered spans are delivered.
- Keep `opik` and `google-adk` up to date to benefit from the latest integration improvements.

## Additional resources

- [Opik ADK integration reference](https://www.comet.com/docs/opik/python-sdk-reference/integrations/adk/overview/)
- [Opik tracing overview](https://www.comet.com/docs/opik/tracing/log_traces)
- [Opik self-host installation guide](https://www.comet.com/docs/opik/self-host/overview)
