# Agent Observability with Phoenix

[Phoenix](https://arize.com/docs/phoenix) is an open-source, self-hosted observability platform for monitoring, debugging, and improving LLM applications and AI Agents at scale. It provides comprehensive tracing and evaluation capabilities for your Google ADK applications. To get started, sign up for a [free account](https://phoenix.arize.com/). 


## Overview

Phoenix can automatically collect traces from Google ADK using [OpenInference instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk), allowing you to:

- **Trace agent interactions** - Automatically capture every agent run, tool call, model request, and response with full context and metadata
- **Evaluate performance** - Assess agent behavior using custom or pre-built evaluators and run experiments to test agent configurations
- **Debug issues** - Analyze detailed traces to quickly identify bottlenecks, failed tool calls, and unexpected agent behavior
- **Self-hosted control** - Keep your data on your own infrastructure

## Installation

### 1. Install Required Packages { #install-required-packages }

```bash
pip install openinference-instrumentation-google-adk google-adk arize-phoenix-otel
```

## Setup

### 1. Launch Phoenix { #launch-phoenix }

These instructions show you how to use Phoenix Cloud. You can also [launch Phoenix](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing) in a notebook, from your terminal, or self-host it using a container. 

1. Sign up for a [free Phoenix account](https://phoenix.arize.com/). 
2. From the Settings page of your new Phoenix Space, create your API key
3. Copy your endpoint which should look like: https://app.phoenix.arize.com/s/[your-space-name]

**Set your Phoenix endpoint and API Key:**

```python
import os

os.environ["PHOENIX_API_KEY"] = "ADD YOUR PHOENIX API KEY"
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "ADD YOUR PHOENIX COLLECTOR ENDPOINT"

# If you created your Phoenix Cloud instance before June 24th, 2025, set the API key as a header:
# os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={os.getenv('PHOENIX_API_KEY')}"
```

### 2.  Connect your application to Phoenix { #connect-your-application-to-phoenix }

```python
from phoenix.otel import register

# Configure the Phoenix tracer
tracer_provider = register(
    project_name="my-llm-app",  # Default is 'default'
    auto_instrument=True        # Auto-instrument your app based on installed OI dependencies
)
```

## Observe

Now that you have tracing setup, all Google ADK SDK requests will be streamed to Phoenix for observability and evaluation.

```python
import nest_asyncio
nest_asyncio.apply()

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Define a tool function
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

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
    model="gemini-2.0-flash-exp",
    description="Agent to answer questions using weather tools.",
    instruction="You must use the available tools to find an answer.",
    tools=[get_weather]
)

app_name = "weather_app"
user_id = "test_user"
session_id = "test_session"
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id
)

# Run the agent (all interactions will be traced)
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[
        types.Part(text="What is the weather in New York?")]
    )
):
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## Support and Resources
- [Phoenix Documentation](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)
- [Community Slack](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
- [OpenInference Package](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
