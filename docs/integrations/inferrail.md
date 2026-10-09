---
catalog_title: Inferrail
catalog_description: Give each agent run a dollar budget, enforced before the model provider
catalog_icon: /integrations/assets/inferrail.png
catalog_tags: ["connectors"]
---

# Inferrail per-run budgets for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Inferrail](https://github.com/domondi1/inferrail) is an open-source,
OpenAI-compatible gateway that gives one agent run a dollar budget. Every
model call in the run carries the run's id and budget as headers. Calls
are admitted while the run's budget has room, and a call that would go
over it is refused with HTTP 402 before it reaches the model provider.
Afterwards you can read what the run cost. Prompts and responses aren't
stored.

Because Inferrail exposes an OpenAI-compatible endpoint, ADK agents use
it through the [LiteLLM](/agents/models/litellm/) model connector. No
ADK-specific package is needed.

## Use cases

- **Cap one run**: a looping agent, a failing tool, or parallel sub-agent
  calls can't spend more than the run's budget.
- **Parallel calls share one budget safely**: each call reserves its
  estimated cost atomically before it's sent.
- **Per-run cost record**: see what each run cost, without storing
  prompts or responses.

## Prerequisites

- Python 3.11+
- An OpenAI API key

## Setup

```bash
pip install google-adk litellm inferrail
export OPENAI_API_KEY=sk-...
```

## Give each run a budget

`inferrail.start()` runs Inferrail inside your process, on a background
thread on a free local port, with no config file. Build each run's model
with the run's id and budget as headers. This example runs two agent
runs at the same time, one with room to finish and one whose budget is
smaller than a single call:

```python
import asyncio

import inferrail
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.genai import types

base_url = inferrail.start()


def lookup(topic: str) -> str:
    """Return a fact about the topic."""
    return "Refunds are processed within 5 business days."


def agent_for_run(run_id: str, budget_usd: str) -> LlmAgent:
    model = LiteLlm(
        model="openai/gpt-4o-mini",
        api_base=base_url,
        api_key="unused",  # the provider key stays with Inferrail
        max_tokens=200,
        extra_headers={
            "X-Inferrail-Attribute-Work-Id": run_id,
            "X-Inferrail-Budget-Usd": budget_usd,
        },
    )
    return LlmAgent(
        name="support",
        model=model,
        instruction="Call lookup once, then answer in one sentence.",
        tools=[lookup],
    )


async def run(run_id: str, budget_usd: str) -> str:
    runner = InMemoryRunner(agent=agent_for_run(run_id, budget_usd), app_name="support")
    session = await runner.session_service.create_session(app_name="support", user_id="u1")
    message = types.Content(role="user", parts=[types.Part(text="How long do refunds take?")])
    async for event in runner.run_async(user_id="u1", session_id=session.id, new_message=message):
        if event.error_code:  # a refused call arrives as an error event
            return f"{run_id}: stopped ({event.error_code})"
    return f"{run_id}: finished"


async def main() -> None:
    print(await asyncio.gather(run("ticket-4812", "0.05"), run("ticket-4813", "0.0001")))


asyncio.run(main())
```

The first call of a run creates its budget; there's nothing to set up
beforehand. Each call reserves its estimated cost (prompt plus
`max_tokens`) before it's sent, so `ticket-4813`'s first call doesn't fit
and is refused with HTTP 402 without reaching OpenAI. In ADK 2.x the
refusal arrives as an event with `error_code` set; stop reading events
there, because the runner raises if you keep iterating. ADK also logs the
error with a traceback.

Read a run's cost afterwards:

```bash
inferrail work ticket-4812
```

## Limitations

- Covers models called through `LiteLlm` (Chat Completions). Native
  Gemini calls don't go through Inferrail.
- Each call reserves an estimate (prompt size plus `max_tokens` at list
  price), so set `max_tokens`.
- Only calls that go through Inferrail are counted.

## Resources

- [Give one AI agent run a dollar budget](https://github.com/domondi1/inferrail/blob/main/docs/recipes/agent-run-budget.md?ref=adk-integrations#google-adk) (also covers running Inferrail as a separate gateway)
- [Inferrail on GitHub](https://github.com/domondi1/inferrail)
- [Inferrail on PyPI](https://pypi.org/project/inferrail/)
