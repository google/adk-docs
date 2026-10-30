---
catalog_title: Tracekit
catalog_description: Check each tool call against your policy and sign it into a verifiable log
catalog_icon: /integrations/assets/tracekit.png
catalog_tags: ["observability"]
---

# Tracekit plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Tracekit](https://github.com/Cygnux-Labs/Tracekit) records what an AI agent does as evidence that people who weren't
there can check. Its [ADK plugin](https://github.com/Cygnux-Labs/Tracekit/blob/main/docs/integrations/google-adk.md) asks a
separate signer process to allow, deny or hold each tool call of every agent a Runner runs, before the tool runs,
and records the result. Each decision and result is signed into a hash-chained log, and a run exports as one bundle
that anyone can verify offline. The ADK plugin is marked experimental in Tracekit.

## Use cases

- **Policy before each tool call**: The plugin asks the signer to decide each call against your policy before the
  tool runs. A denied call never runs: the model reads the reason as the tool's result, and the run goes on.
- **A person approves risky calls**: A call your policy holds waits up to 5 minutes for a person to approve it with
  `tracekit approvals approve`. The approval is bound to the call's exact arguments.
- **Evidence anyone can check**: The signer, not the agent, signs every decision and result. Export a run as one
  bundle and verify it offline with `tracekit verify`.

## Prerequisites

- Python 3.11 or newer
- ADK 2.12, the version Tracekit 1.3 is tested with
- A Gemini API key for the example agent (`GOOGLE_API_KEY`)

Tracekit is open source (MIT) and runs on your own machine; it needs no account.

## Installation

```bash
pip install tracekit-ai "google-adk>=2.12,<2.13"
```

## Use with agent

List the plugin first in the App's `plugins`, so it records each call before any other plugin answers it. On a
laptop, the client starts a local signer the first time it needs one.

```python
import asyncio

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from tracekit.integrations.google_adk import Tracekit
from tracekit.sdk.client import Client


def get_order_status(order_id: str) -> dict:
    """Looks up the shipping status of an order."""
    return {"order_id": order_id, "status": "shipped"}


root_agent = Agent(
    model="gemini-flash-latest",
    name="support_agent",
    instruction="Answer questions about customer orders.",
    tools=[get_order_status],
)


async def main(run):
    app = App(name="support", root_agent=root_agent, plugins=[Tracekit(run)])
    runner = InMemoryRunner(app=app)
    await runner.run_debug("Where is order 1042?")


with Client().run(agent="support-agent") as run:
    asyncio.run(main(run))
```

Then export and verify the run:

```bash
tracekit last
```

This writes the run's bundle and a trust file next to it, checks the bundle and prints `Integrity: VERIFIED.`

### What the plugin covers

- **Covered**: function tools, sub-agents and their tool calls, agents run as tools (`AgentTool`), MCP toolsets, and
  long-running tools. Calls your app pauses for ADK's own tool confirmation are decided again when they resume.
- **Not covered**: handing a task to a task-mode sub-agent, code the agent's `code_executor` runs, and built-in tools
  that run on the model provider's side, such as Google Search.

The [plugin guide](https://github.com/Cygnux-Labs/Tracekit/blob/main/docs/integrations/google-adk.md) lists every case.

## Configuration

- **Policy**: the local signer starts with Tracekit's laptop policy, which knows shell, file and web tools by name. A
  tool it doesn't know, such as `get_order_status` above, is allowed and flagged. Map your own tools and write rules
  for them in a [policy file](https://github.com/Cygnux-Labs/Tracekit/blob/main/docs/policy-v2.md).
- **Production**: run the signer as its own user or service, so the agent can't reach its keys or its log. See the
  [deployment guide](https://github.com/Cygnux-Labs/Tracekit/blob/main/docs/deploy.md).

## Additional resources

- [Tracekit on GitHub](https://github.com/Cygnux-Labs/Tracekit)
- [Tracekit's ADK plugin guide](https://github.com/Cygnux-Labs/Tracekit/blob/main/docs/integrations/google-adk.md)
- [Runnable offline example (scripted model, no API key)](https://github.com/Cygnux-Labs/Tracekit/tree/main/examples/v2/google_adk)
- [tracekit-ai on PyPI](https://pypi.org/project/tracekit-ai/)
