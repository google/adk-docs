---
catalog_title: LangSmith
catalog_description: Trace, monitor, and evaluate agent runs, tool calls, and model requests
catalog_icon: /integrations/assets/langsmith.png
catalog_tags: ["observability", "evaluation"]
---

# LangSmith observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[LangSmith](https://www.langchain.com/langsmith) is the framework-agnostic platform from [LangChain](https://www.langchain.com/) for testing, deploying, monitoring, and improving agents. The LangSmith Python SDK includes a native ADK integration that traces your agents with a single function call, with no OpenTelemetry setup required. To get started, sign up for a [free account](https://smith.langchain.com).

## Overview

LangSmith instruments the ADK runner, agents, model calls, and tools, so you can:

- **Trace agent runs**: Capture each run as a tree of agent invocations, model requests, and tool calls, with inputs, outputs, latency, and token usage
- **Debug multi-agent workflows**: Follow control flow through `SequentialAgent`, `ParallelAgent`, and other sub-agent compositions in one trace
- **Monitor in production**: Track cost, latency, and error rates with dashboards and alerts
- **Evaluate agents**: Turn traces into datasets, then score agent behavior with LLM-as-a-judge, code, or human review

## Installation

Install the LangSmith SDK with the ADK extra:

```bash
pip install "langsmith[google-adk]"
```

## Setup

### 1. Configure environment variables { #configure-environment-variables }

Create a [LangSmith API key](https://docs.langchain.com/langsmith/create-account-api-key) from **Settings** in LangSmith, and a [Gemini API key](https://aistudio.google.com/app/apikey) in Google AI Studio:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="your-langsmith-api-key"
export LANGSMITH_PROJECT="adk-agents"  # Optional: defaults to "default"
# For EU accounts: export LANGSMITH_ENDPOINT="https://eu.api.smith.langchain.com"

export GOOGLE_API_KEY="your-gemini-api-key"
```

### 2. Enable tracing { #enable-tracing }

Call `configure_google_adk()` once at application startup:

```python
from langsmith.integrations.google_adk import configure_google_adk

configure_google_adk()
```

The function accepts these optional arguments:

- **`project_name`**: LangSmith project to send traces to. Defaults to the `LANGSMITH_PROJECT` environment variable.
- **`name`**: Name of the root trace. Defaults to `google_adk.session`.
- **`metadata`**: Key-value pairs attached to every trace.
- **`tags`**: Tags attached to every trace, for filtering in LangSmith.

## Observe

With tracing enabled, run your ADK agent as usual. Every run is sent to your LangSmith project:

```python
import asyncio

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from langsmith.integrations.google_adk import configure_google_adk

configure_google_adk(
    project_name="adk-agents",
    metadata={"environment": "development"},
    tags=["weather"],
)


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
    return {
        "status": "error",
        "error_message": f"Weather information for '{city}' is not available.",
    }


root_agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    description="Agent to answer questions using weather tools.",
    instruction="You must use the available tools to find an answer.",
    tools=[get_weather],
)

app_name = "weather_app"
user_id = "test_user"
runner = InMemoryRunner(agent=root_agent, app_name=app_name)


async def main():
    session = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id
    )

    # Run the agent (all interactions will be traced)
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text="What is the weather in New York?")]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)


asyncio.run(main())
```

Open your project in [LangSmith](https://smith.langchain.com) to see the trace. Each run appears as a `google_adk.session` root with the agent, model calls, and tool calls nested beneath it.

![LangSmith trace of an ADK weather agent, with the agent run, two Gemini model calls, and the get_weather tool call nested under the session](assets/langsmith-trace-light.png#only-light)
![LangSmith trace of an ADK weather agent, with the agent run, two Gemini model calls, and the get_weather tool call nested under the session](assets/langsmith-trace-dark.png#only-dark)

## Support and Resources

- [Trace ADK applications with LangSmith](https://docs.langchain.com/langsmith/trace-with-google-adk)
- [LangSmith Documentation](https://docs.langchain.com/langsmith/home)
- [LangSmith SDK on GitHub](https://github.com/langchain-ai/langsmith-sdk)
- [LangChain Forum](https://forum.langchain.com/)
