---
catalog_title: Langfuse
catalog_description: Trace, evaluate, and debug ADK agents with open-source observability
catalog_icon: /integrations/assets/langfuse.png
catalog_tags: ["observability", "evaluation"]
---

# Langfuse observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Langfuse](https://langfuse.com) is an open-source LLM engineering platform for
observability, evaluation, and prompt management. It captures detailed traces
from ADK agents using [OpenInference
instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
over OpenTelemetry, so you can debug, evaluate, and iterate on agent apps in
development and production.

## Overview

Langfuse captures traces from ADK using OpenTelemetry, giving you:

- **Automatic tracing**: Capture every agent run, tool call, and model request
  with full context
- **User and session tracking**: Map `user_id` and `session_id` from
  `runner.run()` / `runner.run_async()` to Langfuse users and sessions without
  extra code
- **Evaluations and scores**: Attach user feedback, guardrail results, or
  LLM-as-a-judge outcomes to traces
- **Prompt management**: Version and manage prompts alongside your traces
- **Cloud or self-hosted**: Use [Langfuse Cloud](https://cloud.langfuse.com) or
  [self-host](https://langfuse.com/self-hosting) the platform

## Installation

Install the required packages:

```bash
pip install langfuse "google-adk>=2" openinference-instrumentation-google-adk
```

`google-adk` 2.x requires Python 3.10 or later. Pinning `"google-adk>=2"` ensures
pip installs the current ADK 2.x release.

## Setup

Sign up at [cloud.langfuse.com](https://cloud.langfuse.com) or
[self-host](https://langfuse.com/self-hosting) the platform, then set your API
keys. Get keys from your project settings page. Also set a
[Gemini API key](https://aistudio.google.com/app/apikey):

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_BASE_URL="https://cloud.langfuse.com"  # EU region
# Other regions: https://us.cloud.langfuse.com (US),
# https://jp.cloud.langfuse.com (Japan), https://hipaa.cloud.langfuse.com (HIPAA)
export GOOGLE_API_KEY="your-gemini-api-key"
```

Initialize the Langfuse client and instrument ADK:

```python
from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langfuse = get_client()

# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

GoogleADKInstrumentor().instrument()
```

That's it. All ADK agent activity will now be traced and sent to your Langfuse
project automatically.

## Observe

With tracing initialized, run your ADK agent as usual and all interactions will
appear in Langfuse:

```python
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

get_client()
GoogleADKInstrumentor().instrument()

# Define a tool
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }

# Create an agent with tools
agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    description="Agent to answer questions about the weather.",
    instruction="You must use the available tools to find an answer.",
    tools=[get_weather],
)

app_name = "weather_app"
user_id = "test_user"
session_id = "test_session"
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id,
)

# Run the agent. All interactions will be traced.
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(
        role="user",
        parts=[types.Part(text="What is the weather in New York?")],
    ),
):
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## Named and filterable traces

By default, traces are named after the ADK app. Use
[`propagate_attributes`](https://langfuse.com/docs/observability/sdk/instrumentation)
to set a descriptive trace name, tags, and metadata so you can filter traces in
Langfuse.

Use the async `runner.run_async()` API when setting attributes this way. The
synchronous `runner.run()` executes the agent on a background worker thread, so
OpenTelemetry context (and attributes from `propagate_attributes`) does not
reach the ADK spans:

```python
from langfuse import propagate_attributes

with propagate_attributes(
    trace_name="weather-agent-request",
    tags=["google-adk", "demo"],
    metadata={"example": "named-trace"},
):
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What is the weather in New York?")],
        ),
    ):
        if event.is_final_response():
            print(event.content.parts[0].text.strip())
```

## View traces in Langfuse

Open your **Langfuse dashboard → Traces** to inspect agent loops, tool calls,
and model generations. Traces are filterable by the users, sessions, and tags
set above.

![ADK example trace in Langfuse](https://langfuse.com/images/cookbook/integration-google-adk/google-adk-trace.png)

For multi-agent pipelines, scoring traces with user feedback, and more examples,
see the [Langfuse ADK integration
guide](https://langfuse.com/integrations/frameworks/google-adk).

## Support and Resources

- [Langfuse Documentation](https://langfuse.com/docs)
- [ADK Integration Guide](https://langfuse.com/integrations/frameworks/google-adk)
- [Langfuse Repository on GitHub](https://github.com/langfuse/langfuse)
- [Community Discord](https://discord.gg/7NXgeHuTZu)
