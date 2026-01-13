# Agent Observability and Evalulation with Galileo

[Galileo](https://app.galileo.ai/) is an
AI evaluation and observability platform that delivers end-to-end tracing,
evaluation, and monitoring for AI applications.
Galileo supports direct OpenTelemetry (OTel)
trace ingestion from Google ADK for agent runs,
tool calls, and model requests.

For more information, see Galileo’s
[Google ADK integration](https://v2docs.galileo.ai/sdk-api/third-party-integrations/opentelemetry-and-openinference/google-adk)
docs.

## Prerequisites

- A [Galileo API key](https://v2docs.galileo.ai/references/faqs/find-keys#galileo-api-key)
- A Galileo Project and Log stream
- A [Google API Key](https://aistudio.google.com/app/apikey?)

## Install dependencies

```bash
pip install google-adk openinference-instrumentation-google-adk python-dotenv galileo
```

Optionally, use the `requirements.txt` from the [completed example](https://github.com/rungalileo/sdk-examples/tree/main/python/agent/google-adk).

## Set Environment Variables

Configure environment variables :

```env title="Update: my_agent/.env"
# Gemini environment variables
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY="YOUR_API_KEY"

# Galileo environment variables
GALILEO_API_KEY="YOUR_API_KEY"
GALILEO_PROJECT="YOUR_PROJECT"
GALILEO_LOG_STREAM="YOUR_LOG_STREAM"
```

## Configure OpenTelemetry (required)

You must configure an OTLP exporter and set a global tracer provider before
using any ADK components so that spans are emitted to Galileo.

```python
# my_agent/agent.py

from dotenv import load_dotenv

load_dotenv()

# OpenTelemetry imports
from opentelemetry.sdk import trace as trace_sdk

# Galileo span processor (auto-configures OTLP headers & endpoint from env vars)
from galileo import otel

# OpenInference instrumentation for Google ADK 
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

# Create tracer provider and register Galileo span processor
tracer_provider = trace_sdk.TracerProvider()
galileo_span_processor = otel.GalileoSpanProcessor()
tracer_provider.add_span_processor(galileo_span_processor)

# Instrument Google ADK with OpenInference (this captures inputs/outputs)
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)

```

## Example: Trace an ADK agent

Now you can add the agent code for a simple current time agent, after the code that
sets up the OTLP exporter and tracer provider:

```python
# my_agent/agent.py

from google.adk.agents.llm_agent import Agent

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}


root_agent = Agent(
    model="gemini-3-flash-preview",
    name="root_agent",
    description="Tells the current time in a specified city.",
    instruction=("You are a helpful assistant \
    that tells the current time in cities."
    "Use the 'get_current_time' tool for this purpose."),
    tools=[get_current_time],
)

```

Run the agent with:

```bash
adk run my_agent
```

And ask it a question:

```console
What is it in London?
```

```console
[root_agent]: The current time in London is 10:30 AM.
```

See the full
[Google ADK + OpenTelemetry Example Project](https://github.com/rungalileo/sdk-examples/tree/main/python/agent/google-adk)
for a completed example.

## View traces in Galileo

Select your Project and inspect the traces and spans in your Log Stream.

![Galileo Traces](../assets/galileo.png)

## Resources

- [Galileo Google ADK Integration Documentation](https://v2docs.galileo.ai/sdk-api/third-party-integrations/opentelemetry-and-openinference/google-adk):
Official documentation for integrating a Google ADK project
with Galileo using OpenTelemetry and OpenInference.
- [Google ADK + OpenTelemetry Example Project](https://github.com/rungalileo/sdk-examples/tree/main/python/agent/google-adk):
This is an example project demonstrating how to use Galileo
with the Google ADK. This example is a completed
[Google ADK Python Quickstart](../get-started/python.md)
with Galileo instrumented on top.
