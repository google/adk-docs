# Future AGI observability for ADK

Supported in ADKPython

[Future AGI](https://futureagi.com) is an observability and evaluation platform for AI agents. The [`traceai-google-adk`](https://pypi.org/project/traceai-google-adk/) package auto-instruments ADK agents and exports every agent run, model call, tool execution, and event-loop cycle to Future AGI as OpenTelemetry spans, where you can inspect the run tree, evaluate behavior, and run experiments.

## Overview

The `traceai-google-adk` package adds OpenTelemetry instrumentation for ADK, allowing you to:

- **Trace agent runs:** Capture every agent invocation, tool call, model request, and response with prompts, completions, parameters, and token usage.
- **Evaluate behavior:** Run pre-built or custom evaluators against the captured traces.
- **Debug agents:** Drill into hierarchical run trees to find failed tool calls, latency hotspots, and unexpected branches.

## Prerequisites

1. Sign up at [app.futureagi.com](https://app.futureagi.com).
1. Copy your `FI_API_KEY` and `FI_SECRET_KEY` from the dashboard.
1. Set the environment variables:

```bash
export FI_API_KEY=<your-fi-api-key>
export FI_SECRET_KEY=<your-fi-secret-key>
export GOOGLE_API_KEY=<your-google-api-key>
```

## Installation

```bash
pip install traceai-google-adk
```

The `traceai-google-adk` package declares `google-adk` and `google-genai` as runtime dependencies, so they install transitively.

## Sending Traces to Future AGI

Register the Future AGI tracer once at startup and attach the `GoogleADKInstrumentor` **before** running any agent. Every subsequent ADK agent invocation is captured automatically.

```python
import asyncio

from fi_instrumentation import register
from fi_instrumentation.fi_types import ProjectType
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from traceai_google_adk import GoogleADKInstrumentor

tracer_provider = register(
    project_type=ProjectType.OBSERVE,
    project_name="adk-weather-agent",
)
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city."""
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25°C.",
        }
    return {
        "status": "error",
        "error_message": f"Weather information for '{city}' is not available.",
    }


agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    description="Agent to answer weather questions.",
    instruction="You must use the available tools to find an answer.",
    tools=[get_weather],
)


async def main():
    runner = InMemoryRunner(agent=agent, app_name="weather_app")
    await runner.session_service.create_session(
        app_name="weather_app", user_id="user", session_id="session"
    )
    async for event in runner.run_async(
        user_id="user",
        session_id="session",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What is the weather in New York?")],
        ),
    ):
        if event.is_final_response():
            print(event.content.parts[0].text.strip())


if __name__ == "__main__":
    asyncio.run(main())
```

## View Traces in the Dashboard

Run the agent, then open your project in the [Future AGI dashboard](https://app.futureagi.com). Each ADK agent run produces a hierarchical trace with prompts, completions, model parameters, token usage, tool inputs and outputs, and event-loop cycles laid out for inspection.

## Resources

- [`traceai-google-adk` on PyPI](https://pypi.org/project/traceai-google-adk/)
- [`traceAI` on GitHub](https://github.com/future-agi/traceAI/tree/main/python/frameworks/google-adk)
- [Future AGI documentation](https://docs.futureagi.com)
