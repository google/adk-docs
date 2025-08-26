# Agent Observability with LangWatch

[LangWatch](https://langwatch.ai) is a comprehensive observability platform for monitoring, debugging, and improving LLM applications and AI Agents. It provides automatic tracing, evaluation, and monitoring capabilities for your Google ADK applications through seamless OpenTelemetry integration. To get started, sign up for a [free account](https://app.langwatch.ai).

## Overview

LangWatch can automatically collect traces from Google ADK using [OpenInference instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk), allowing you to:

- **Trace agent interactions** - Automatically capture every agent run, tool call, model request, and response with context and metadata
- **Evaluate performance** - Assess agent behavior using custom or pre-built evaluators and run experiments to test agent configurations
- **Monitor in production** - Set up real-time dashboards and alerts to track performance
- **Debug issues** - Analyze detailed traces to quickly identify bottlenecks, failed tool calls, and any unexpected agent behavior

## Installation

Install the required packages:

```bash
pip install langwatch google-adk openinference-instrumentation-google-adk
```

## Setup

### 1. Configure Environment Variables { #configure-environment-variables }

Set your LangWatch API key and Google API key:

```bash
export LANGWATCH_API_KEY=[your_langwatch_api_key_here]
export GOOGLE_API_KEY=[your_google_api_key_here]
```

### 2. Connect your application to LangWatch { #connect-your-application-to-langwatch }

```python
import langwatch
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

# Initialize LangWatch with the Google ADK instrumentor
langwatch.setup(
    instrumentors=[GoogleADKInstrumentor()]
)
```

That's it! All Google ADK agent activity will now be traced and sent to your LangWatch dashboard automatically.

## Observe

Now that you have tracing setup, all Google ADK SDK requests will be streamed to LangWatch for observability and evaluation.

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

## Advanced Configuration

### Using Decorators for Additional Context

If you want to add additional context or metadata to your traces, you can optionally use the `@langwatch.trace()` decorator:

```python
import langwatch
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langwatch.setup(
    instrumentors=[GoogleADKInstrumentor()]
)

@langwatch.trace(name="Google ADK Agent Run")
def run_agent_interaction(user_message: str):
    # Update the current trace with additional metadata
    current_trace = langwatch.get_current_trace()
    if current_trace:
        current_trace.update(
            metadata={
                "user_id": "user_123",
                "session_id": "session_abc",
                "agent_name": "weather_agent",
                "model": "gemini-2.0-flash-exp"
            }
        )

    # Your agent execution code here
    # ... agent execution code ...

    return "Agent response"
```

## View Results in LangWatch

Once your application is running with the instrumentation, you can view all traces, metrics, and evaluations in your LangWatch dashboard:

- **Traces**: See detailed execution flows of your agents
- **Metrics**: Monitor performance and usage patterns
- **Evaluations**: Assess agent behavior and run experiments
- **Alerts**: Set up monitoring and get notified of issues

## Notes

- You do **not** need to set any OpenTelemetry environment variables or configure exporters manually—`langwatch.setup()` handles everything.
- The `@langwatch.trace()` decorator is **optional** - the OpenInference instrumentor will capture all ADK activity automatically.
- For advanced configuration (custom attributes, endpoint, etc.), see the [LangWatch Python integration guide](https://docs.langwatch.ai/integration/python).

## Troubleshooting

- Make sure your `LANGWATCH_API_KEY` is set in the environment.
- If you see no traces in LangWatch, check that the instrumentor is included in `langwatch.setup()` and that your agent code is being executed.
- Ensure you have the correct Google API key set for Gemini access.
- Check that the `openinference-instrumentation-google-adk` package is properly installed.

## Support and Resources

- [LangWatch Documentation](https://docs.langwatch.ai)
- [LangWatch Google ADK Integration Guide](https://docs.langwatch.ai/integration/python/integrations/google-ai)
- [OpenInference Package](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
