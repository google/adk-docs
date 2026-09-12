# Zespan observability for ADK

Supported in ADKPythonTypeScript

[Zespan](https://zespan.com) is an agent reliability platform for AI applications. The Zespan SDK instruments ADK agents natively by capturing every agent invocation, model call, tool execution, and multi-agent delegation as linked spans, then shipping them to the [Zespan dashboard](https://app.zespan.com) for inspection, cost attribution, and evaluation.

## Overview

Once your ADK agents are instrumented, the Zespan platform provides:

- **Tracing:** Capture every agent, model, tool, and delegation span with latency, tokens, and cost.
- **Cost attribution:** Break down spend by model, agent, and time period.
- **Evaluations:** Score agent behavior with custom metrics, datasets, and simulations.
- **Guardrails:** Block, redact, or flag unsafe inputs and outputs at runtime.
- **Prompt management:** Fetch and version prompts with caching and variable substitution.

## Prerequisites

Before you begin, set up a Zespan account and credentials:

1. Sign up at [app.zespan.com](https://app.zespan.com).
1. Create a project and copy the **API key** from **Onboarding → API Key**.
1. Set the environment variables:

```bash
export ZESPAN_API_KEY=<your-zespan-api-key>
export GOOGLE_API_KEY=<your-google-api-key>
```

## Installation

Install the Zespan SDK alongside ADK:

```bash
pip install zespan google-adk
```

```bash
npm install @zespan/sdk @google/adk
```

## Send traces

Instrument an ADK agent with the Zespan SDK to start capturing traces:

Initialize Zespan once at startup, then create a `ZespanADKCallbackHandler` and spread its `.callbacks` into your `LlmAgent`.

```python
import asyncio
import os

import zespan
from zespan import ZespanADKCallbackHandler
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

zespan.init(api_key=os.environ["ZESPAN_API_KEY"])

handler = ZespanADKCallbackHandler()


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


agent = LlmAgent(
    name="weather_agent",
    model="gemini-flash-latest",
    description="Agent to answer weather questions.",
    instruction="Use the available tools to find an answer.",
    tools=[get_weather],
    **handler.callbacks,
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

Two approaches are available.

**`instrumentADK`** wraps coordinator and runner in one call and intercepts the full event stream, including delegations.

```typescript
import { zespan, instrumentADK } from "@zespan/sdk";
import { LlmAgent, InMemoryRunner } from "@google/adk";

zespan.init({ apiKey: process.env.ZESPAN_API_KEY! });

function getWeather(city: string): object {
  if (city.toLowerCase() === "new york") {
    return {
      status: "success",
      report: "The weather in New York is sunny with a temperature of 25°C.",
    };
  }
  return {
    status: "error",
    error_message: `Weather information for '${city}' is not available.`,
  };
}

const coordinator = new LlmAgent({
  name: "weather_agent",
  model: "gemini-flash-latest",
  description: "Agent to answer weather questions.",
  instruction: "Use the available tools to find an answer.",
  tools: [getWeather],
});

const runner = new InMemoryRunner({
  agent: coordinator,
  appName: "weather_app",
});

const { runner: tracedRunner } = instrumentADK({ coordinator, runner });

for await (const event of tracedRunner.runEphemeral({
  userId: "user",
  newMessage: { parts: [{ text: "What is the weather in New York?" }] },
})) {
  if (event.isFinalResponse()) {
    console.log(event.content.parts[0].text);
  }
}
```

**`ZespanADKCallbackHandler`** uses ADK's native callback system; spread `.callbacks` into your agent config.

```typescript
import { zespan, ZespanADKCallbackHandler } from "@zespan/sdk";
import { LlmAgent, InMemoryRunner } from "@google/adk";

zespan.init({ apiKey: process.env.ZESPAN_API_KEY! });

const handler = new ZespanADKCallbackHandler();

const agent = new LlmAgent({
  name: "weather_agent",
  model: "gemini-flash-latest",
  description: "Agent to answer weather questions.",
  instruction: "Use the available tools to find an answer.",
  tools: [getWeather],
  ...handler.callbacks,
});

const runner = new InMemoryRunner({ agent, appName: "weather_app" });

for await (const event of runner.runEphemeral({
  userId: "user",
  newMessage: { parts: [{ text: "What is the weather in New York?" }] },
})) {
  if (event.isFinalResponse()) {
    console.log(event.content.parts[0].text);
  }
}
```

## Multi-agent systems

Zespan links coordinator and sub-agent spans into a single trace:

Use the **same handler instance** across the coordinator and all sub-agents. Spans are linked under a single trace via the shared ADK invocation ID.

```python
handler = ZespanADKCallbackHandler()

specialist = LlmAgent(
    name="lookup_agent",
    model="gemini-flash-latest",
    tools=[lookup_tool],
    **handler.callbacks,
)

coordinator = LlmAgent(
    name="coordinator",
    model="gemini-flash-latest",
    sub_agents=[specialist],
    **handler.callbacks,
)
```

With `instrumentADK`, all `subAgents` are wrapped recursively and automatically.

```typescript
const specialist = new LlmAgent({
  name: "lookup_agent",
  model: "gemini-flash-latest",
  tools: [lookupTool],
});

const coordinator = new LlmAgent({
  name: "coordinator",
  model: "gemini-flash-latest",
  subAgents: [specialist],
});

const { runner: tracedRunner } = instrumentADK({
  coordinator,
  runner: new InMemoryRunner({ agent: coordinator, appName: "my_app" }),
});
```

With `ZespanADKCallbackHandler`, spread the same instance into every agent.

```typescript
const handler = new ZespanADKCallbackHandler();

const specialist = new LlmAgent({
  name: "lookup_agent",
  model: "gemini-flash-latest",
  tools: [lookupTool],
  ...handler.callbacks,
});

const coordinator = new LlmAgent({
  name: "coordinator",
  model: "gemini-flash-latest",
  subAgents: [specialist],
  ...handler.callbacks,
});
```

## View traces in the dashboard

Run the agent, then open your project at [app.zespan.com](https://app.zespan.com). Each ADK run produces a hierarchical trace showing:

- Agent spans with latency and delegation links between coordinator and sub-agents
- LLM spans with token counts, cost, finish reason, and optional prompt/completion text
- Tool spans with input arguments and return values

## Resources

- [Zespan](https://zespan.com)
- [`zespan` on PyPI](https://pypi.org/project/zespan/)
- [`@zespan/sdk` on npm](https://www.npmjs.com/package/@zespan/sdk)
- [Zespan documentation](https://docs.zespan.com)
