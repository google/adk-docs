# Latitude observability for ADK

Supported in ADKPython

[Latitude](https://latitude.so) is an open-source observability and evaluation platform for LLM applications. Its [`latitude-telemetry`](https://pypi.org/project/latitude-telemetry/) Python SDK ships dedicated instrumentation for the Agent Development Kit, so every agent run, model generation, and tool call is exported as an OpenTelemetry trace you can inspect, search, and evaluate.

## Why Latitude for ADK?

ADK includes its own OpenTelemetry-based tracing. Latitude builds on it with a hosted (or self-hosted) platform purpose-built for agents:

- **Full agent traces:** The nested agent, generation, and tool-call hierarchy, captured automatically with no changes to how you call ADK.
- **Cost, tokens, and latency:** Aggregated at every level of the trace.
- **Sessions:** Group multi-turn conversations and multi-step agent runs into a single session.
- **Evaluations:** Score agent outputs offline or in production with LLM-as-judge or code-based evaluators.
- **Open source:** Run it fully self-hosted, or use the managed cloud.

## Prerequisites

- A **Latitude account** and **API key** (sign up at [console.latitude.so](https://console.latitude.so/login), or self-host).
- A **Latitude project slug**.
- A **Gemini API key** set as `GOOGLE_API_KEY`.

## Installation

```bash
pip install latitude-telemetry google-adk
```

Set the required environment variables:

```bash
export LATITUDE_API_KEY="your-api-key"
export LATITUDE_PROJECT="your-project-slug"
export GOOGLE_API_KEY="your-gemini-api-key"
```

`LATITUDE_API_KEY` and `LATITUDE_PROJECT` send traces to your Latitude project. `GOOGLE_API_KEY` is used by ADK's Gemini model calls.

## Use with agent

Pass the `google.adk` module to the Latitude SDK under the `google_adk` instrumentation key. Latitude registers an OpenTelemetry tracer provider and instruments ADK; you keep calling ADK exactly as you do today.

```python
import asyncio
import os

import google.adk
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from latitude_telemetry import Latitude, capture

latitude = Latitude(
    api_key=os.environ["LATITUDE_API_KEY"],
    project=os.environ["LATITUDE_PROJECT"],
    instrumentations={"google_adk": google.adk},
)


def get_weather(city: str) -> dict:
    """Returns the current weather for a city."""
    return {"status": "success", "report": f"The weather in {city} is sunny."}


agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    description="Agent that answers weather questions using tools.",
    instruction="Answer weather questions using get_weather.",
    tools=[get_weather],
)


async def weather_agent_run():
    runner = InMemoryRunner(agent=agent, app_name="weather_app")
    await runner.session_service.create_session(
        app_name="weather_app",
        user_id="user_123",
        session_id="session_abc",
    )

    async for event in runner.run_async(
        user_id="user_123",
        session_id="session_abc",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What's the weather in Barcelona?")],
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text


# Wrap a request or job with capture() to attach a user_id, session_id, tags,
# or metadata to every span produced inside it.
capture("weather-agent-run", lambda: asyncio.run(weather_agent_run()))

# Flush any pending spans and shut down before the process exits.
latitude.shutdown()
```

## What you get

Each agent run shows up in Latitude as a trace with nested spans:

- **Agent spans:** agent name, instructions, and configured tools
- **Generation spans:** model, input/output messages, and token usage
- **Tool spans:** tool calls with input arguments and output

Open your project in the [Latitude dashboard](https://console.latitude.so/login) to see the full agent, generation, and tool hierarchy, with token usage and latency aggregated at every level.

## Resources

- [Latitude documentation](https://docs.latitude.so)
- [Latitude ADK integration guide](https://docs.latitude.so/telemetry/frameworks/google-adk)
- [Latitude on GitHub](https://github.com/latitude-dev/latitude-llm)
