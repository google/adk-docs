---
catalog_title: TraceRoot
catalog_description: Trace, debug, and evaluate your ADK agent workflows
catalog_icon: /integrations/assets/traceroot.png
catalog_tags: ["observability", "evaluation"]
---

# TraceRoot observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[TraceRoot](https://traceroot.ai/?utm_source=google-adk&utm_medium=referral&utm_campaign=2026-09-google-adk)
is an [open-source](https://github.com/traceroot-ai/traceroot) observability and
self-improving layer for AI agents that helps teams detect failures, investigate
their causes, and evaluate fixes. Its ADK integration captures agent runs, model
calls, and tool executions, including inputs, outputs, token usage, and timing.

## Overview

Key features include:

- [Model and tool-call tracing](https://traceroot.ai/docs/tracing/introduction):
  Inspect inputs, outputs, timing, and token usage for each step, with cost
  tracking for supported models.
- [Detectors and alerts about your agent traces](https://traceroot.ai/docs/detectors/introduction):
  Use an LLM judge to check incoming traces for issues you define, with optional
  root cause analysis and email or Slack alerts.
- [AI-assisted debugging](https://traceroot.ai/docs/ai-agent/overview):
  Investigate failures using traces and code from your connected GitHub
  repository, then open fix PRs for review.
- [Datasets and evaluations](https://traceroot.ai/docs/evals/introduction):
  Run your agent on repeatable test cases, score its outputs, and compare
  changes to prompts, models, or code.
- [CLI access for coding agents](https://traceroot.ai/docs/cli/get-started):
  Inspect and export traces from your terminal, or let your coding agent read
  them alongside your source code.

## Installation

Use Python 3.11 or later and install the following packages in your virtual
environment:

```bash
pip install traceroot google-adk
```

## Setup

### 1. Configure your API keys

Create a project in [TraceRoot](https://app.traceroot.ai) and copy its API key.
The example also needs a [Gemini API key](https://ai.google.dev/gemini-api/docs/api-key).
Set both keys in your environment:

```bash
export TRACEROOT_API_KEY="YOUR_TRACEROOT_API_KEY"
export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
export GOOGLE_GENAI_USE_VERTEXAI="FALSE"
```

For a self-hosted TraceRoot instance, also set `TRACEROOT_HOST_URL` to your
instance's URL. Keep these keys on the server.

### 2. Enable tracing and run an agent

Call `traceroot.initialize(integrations=[Integration.GOOGLE_ADK])` before running
your agent. The SDK uses OpenInference instrumentation to capture ADK execution
and reads `TRACEROOT_API_KEY` from the environment to send traces to TraceRoot.

Save the following as `agent.py`. It uses a small set of sample orders so the
agent can answer a question by calling a tool.

```python
import asyncio

import traceroot
from traceroot import Integration

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

traceroot.initialize(
    integrations=[Integration.GOOGLE_ADK]
)


def get_order_status(order_id: str) -> dict:
    """Look up an order in the sample data.

    Args:
        order_id: The order identifier, such as ORD-123.
    """
    orders = {"ORD-123": "shipped", "ORD-456": "processing"}
    return {
        "order_id": order_id,
        "status": orders.get(order_id, "not found"),
    }


root_agent = Agent(
    name="order_assistant",
    model="gemini-flash-latest",
    instruction="Use get_order_status for order questions.",
    tools=[get_order_status],
)


async def main():
    async with InMemoryRunner(
        agent=root_agent, app_name="order_demo"
    ) as runner:
        session = await runner.session_service.create_session(
            app_name="order_demo", user_id="demo_user"
        )
        message = types.Content(
            role="user",
            parts=[types.Part(text="Has ORD-123 shipped?")],
        )
        async for event in runner.run_async(
            user_id="demo_user",
            session_id=session.id,
            new_message=message,
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts or []:
                    if part.text:
                        print(part.text)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        traceroot.flush()
```

Run the example from the same terminal where you set the environment variables:

```bash
python agent.py
```

The agent looks up `ORD-123` and responds with its shipping status.
The final `traceroot.flush()` call sends any buffered spans before the script exits.

## Observe

Open your project in [TraceRoot](https://app.traceroot.ai) and select the new
trace. Expand the trace tree to see the agent run, the model calls, and the
`get_order_status` tool call. Select the tool span to inspect the `order_id`
argument and the returned status, or select a model span to inspect its prompt,
response, and token usage.

The [trace timeline](https://traceroot.ai/docs/tracing/timeline) shows how long
each step took, helping you distinguish time spent in the model from time spent
in tools. The [token and cost views](https://traceroot.ai/docs/tracing/cost-tracking)
show usage per model call and across the trace, with costs calculated for
supported models.

## Troubleshooting

- If the model request fails, check that `GOOGLE_API_KEY` is loaded and valid.
- If the request succeeds but no trace appears, check `TRACEROOT_API_KEY` and make
  sure `traceroot.initialize(integrations=[Integration.GOOGLE_ADK])` runs before
  the agent. For a self-hosted instance, also check `TRACEROOT_HOST_URL`.
- Initialize tracing once per process and call `traceroot.flush()` before a
  short-lived script exits.

## Support and resources

- [TraceRoot ADK integration guide](https://traceroot.ai/docs/integrations/google-adk)
- [TraceRoot Python SDK reference](https://traceroot.ai/docs/tracing/python-sdk)
- [TraceRoot Python SDK on GitHub](https://github.com/traceroot-ai/traceroot-py)
