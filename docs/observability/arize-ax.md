# Agent Observability with Arize AX

[Arize AX](https://arize.com/docs/ax) is a production-grade observability platform for monitoring, debugging, and improving LLM applications and AI Agents at scale. It provides comprehensive tracing, evaluation, and monitoring capabilities for your Google ADK applications. To get started, sign up for a [free account](https://app.arize.com/auth/join).

For an open-source, self-hosted alternative, check out [Phoenix](https://arize.com/docs/phoenix).

## Overview

Arize AX can automatically collect traces from Google ADK using [OpenInference instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk), allowing you to:

- **Trace agent interactions** - Automatically capture every agent run, tool call, model request, and response with context and metadata
- **Evaluate performance** - Assess agent behavior using custom or pre-built evaluators and run experiments to test agent configurations
- **Monitor in production** - Set up real-time dashboards and alerts to track performance
- **Debug issues** - Analyze detailed traces to quickly identify bottlenecks, failed tool calls, and any unexpected agent behavior

![Agent Traces](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-traces.png)

## Installation

Install the required packages:

```bash
pip install openinference-instrumentation-google-adk google-adk arize-otel
```

## Setup

### 1. Configure Environment Variables { #configure-environment-variables }

Set your Google API key:

```bash
export GOOGLE_API_KEY=[your_key_here]
```

### 2. Connect your application to Arize AX { #connect-your-application-to-arize-ax }

```python
from arize.otel import register

# Register with Arize AX
tracer_provider = register(
    space_id="your-space-id",      # Found in app space settings page
    api_key="your-api-key",        # Found in app space settings page
    project_name="your-project-name"  # Name this whatever you prefer
)

# Import and configure the automatic instrumentor from OpenInference
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

# Finish automatic instrumentation
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)
```

## Observe

Now that you have tracing setup, all Google ADK SDK requests will be streamed to Arize AX for observability and evaluation.

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
## View Results in Arize AX
![Traces in Arize AX](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-dashboard.png)
![Agent Visualization](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-agent.png)
![Agent Experiments](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-experiments.png)

## Support and Resources
- [Arize AX Documentation](https://arize.com/docs/ax/integrations/frameworks-and-platforms/google-adk)
- [Arize Community Slack](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
- [OpenInference Package](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
