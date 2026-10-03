# LangWatch observability for ADK

Supported in ADKPython

[LangWatch](https://langwatch.ai) is an open-source LLMOps platform for observability, evaluation, and prompt optimization. It provides comprehensive tracing for ADK agents using [OpenInference instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk), allowing you to monitor, debug, and improve your agents in development and production.

## Overview

LangWatch captures traces from ADK using its built-in OpenTelemetry support, giving you:

- **Automatic tracing** - Capture every agent run, tool call, and model request with full context
- **Online evaluation** - Continuously score production traffic for quality and safety
- **Guardrails** - Block or modify harmful responses in real-time
- **Prompt management** - Version, test, and optimize prompts with built-in A/B testing
- **Datasets and experiments** - Build evaluation sets from real traces and run batch experiments

## Installation

Install the required packages:

```bash
pip install langwatch openinference-instrumentation-google-adk google-adk
```

## Setup

Sign up at [langwatch.ai](https://langwatch.ai) or [self-host](https://langwatch.ai/docs/self-hosting/overview) the platform, then set your API key:

```bash
export LANGWATCH_API_KEY="your-langwatch-api-key"
export GOOGLE_API_KEY="your-gemini-api-key"
```

Initialize tracing:

```python
import langwatch
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langwatch.setup(
    instrumentors=[GoogleADKInstrumentor()]
)
```

That's it. All ADK agent activity will now be traced and sent to your LangWatch dashboard automatically.

## Observe

With tracing initialized, run your ADK agent as usual and all interactions will appear in LangWatch:

```python
import langwatch
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langwatch.setup(
    instrumentors=[GoogleADKInstrumentor()]
)

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

# Run the agent — all interactions will be traced
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

## Adding Custom Metadata

Use the `@langwatch.trace()` decorator to attach additional context to your traces:

```python
@langwatch.trace(name="ADK Weather Agent")
def run_agent(user_message: str):
    current_trace = langwatch.get_current_trace()
    if current_trace:
        current_trace.update(
            metadata={
                "user_id": "user_123",
                "agent_name": "weather_agent",
                "environment": "production",
            }
        )

    user_msg = types.Content(
        role="user", parts=[types.Part(text=user_message)]
    )
    for event in runner.run(
        user_id="demo-user",
        session_id="demo-session",
        new_message=user_msg,
    ):
        if event.is_final_response():
            return event.content.parts[0].text

    return "No response generated"
```

## Support and Resources

- [LangWatch Documentation](https://langwatch.ai/docs)
- [ADK Integration Guide](https://langwatch.ai/docs/integration/python/integrations/google-ai)
- [LangWatch Repository on GitHub](https://github.com/langwatch/langwatch)
- [Community Discord](https://discord.gg/langwatch)
