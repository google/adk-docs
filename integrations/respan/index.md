# Respan observability for ADK

Supported in ADKPython

[Respan](https://www.respan.ai/) captures ADK runner, agent, model, and tool spans so you can inspect complete agent workflows in the Respan platform. The ADK integration uses [`respan-instrumentation-google-adk`](https://pypi.org/project/respan-instrumentation-google-adk/), which wraps the OpenInference ADK instrumentor and adds Respan-specific span normalization before traces are exported.

## Overview

Use Respan with ADK to:

- **Trace agent runs**: Capture runner invocations, agent execution, model calls, and tool calls in one trace.
- **Debug failures**: Inspect span inputs, outputs, timing, and errors across nested ADK workflows.
- **Track production metadata**: Attach customer, thread, environment, and custom metadata to all spans from a request.
- **Route models through the Respan gateway**: Use ADK's LiteLLM adapter with Respan's OpenAI-compatible gateway when you want centralized model routing.

## Prerequisites

- Python 3.11, 3.12, or 3.13.
- A [Respan API key](https://platform.respan.ai/platform/api/api-keys).
- A Google API key if your ADK agent calls Gemini directly.

## Installation

Install the Respan SDK, the ADK instrumentor, and ADK:

```bash
pip install respan-ai respan-instrumentation-google-adk "google-adk[extensions]"
```

Set the required environment variables:

```bash
export RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
```

`RESPAN_API_KEY` sends traces to Respan. `GOOGLE_API_KEY` is used by direct Gemini model calls.

## Trace an ADK agent

Initialize Respan before running the ADK agent. All ADK runs started after initialization are traced automatically.

```python
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from respan import Respan
from respan_instrumentation_google_adk import GoogleADKInstrumentor

respan = Respan(
    instrumentations=[GoogleADKInstrumentor()],
    environment="development",
)

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="You are a concise assistant.",
)


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="respan-adk-demo",
        user_id="user_1",
    )
    runner = Runner(
        agent=agent,
        app_name="respan-adk-demo",
        session_service=session_service,
    )
    message = types.Content(
        role="user",
        parts=[types.Part(text="Say hello in one sentence.")],
    )

    async for event in runner.run_async(
        user_id="user_1",
        session_id=session.id,
        new_message=message,
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)

    respan.flush()
    respan.shutdown()


asyncio.run(main())
```

Open the [Respan traces page](https://platform.respan.ai/platform/traces) to see the ADK workflow with runner, agent, model, and tool spans.

## Add request metadata

Use `propagate_attributes()` to add per-request identifiers and metadata to all spans produced inside the context.

```python
from respan import Respan, propagate_attributes
from respan_instrumentation_google_adk import GoogleADKInstrumentor

respan = Respan(instrumentations=[GoogleADKInstrumentor()])


async def handle_user_request(user_id: str, message: str):
    with propagate_attributes(
        customer_identifier=user_id,
        thread_identifier="conversation_123",
        metadata={"source": "web"},
    ):
        return await run_adk_agent(message)
```

## Trace tool calls

ADK tools are captured as child tool spans with serialized inputs, outputs, and timing.

```python
from google.adk.agents import Agent


def get_weather(city: str) -> str:
    """Return a deterministic weather report for a city."""
    return f"{city}: sunny, 72F, light wind"


agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    instruction="Use the get_weather tool when weather is requested.",
    tools=[get_weather],
)
```

## Use the Respan gateway

ADK can route model calls through the Respan gateway with its LiteLLM adapter. This is useful when you want one OpenAI-compatible endpoint for multiple model providers.

```bash
export RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
export RESPAN_BASE_URL="https://api.respan.ai/api"
export RESPAN_MODEL="openai/gpt-5-mini"
```

```python
import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

agent = Agent(
    name="assistant",
    model=LiteLlm(
        model=os.getenv("RESPAN_MODEL", "openai/gpt-5-mini"),
        api_key=os.environ["RESPAN_API_KEY"],
        api_base=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
    ),
    instruction="You are a concise assistant.",
)
```

## Resources

- [Respan ADK tracing docs](https://www.respan.ai/docs/integrations/google-adk)
- [Respan ADK gateway docs](https://www.respan.ai/docs/integrations/gateway/google-adk)
- [Respan Python examples](https://github.com/respanai/respan-example-projects/tree/main/python/tracing/google-adk)
- [Respan platform](https://platform.respan.ai/platform/traces)
