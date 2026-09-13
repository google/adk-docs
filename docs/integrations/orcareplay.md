---
catalog_title: OrcaReplay
catalog_description: Record an agent run at the model-provider boundary and replay it offline with no provider call
catalog_icon: /integrations/assets/orcareplay.png
---

# OrcaReplay for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[OrcaReplay](https://github.com/Continuum-AI-Corp/OrcaReplay) records an agent run from **outside
the process** — at the HTTP boundary between your agent and its model provider — and can serve that
recording back so the same run happens again with no provider called and no API key needed.

Nothing is installed into your agent. `orca record` launches your ADK script as a child process with
the provider origin redirected for that process only, so the code that runs is the code you wrote,
not an instrumented variant of it.

## Use cases

- **Reproduce a run someone else had.** A recording is a file. A colleague, or a maintainer on an
  issue, can re-run the session that misbehaved without your key and without spending tokens.
- **Regression-test an agent in CI.** Replay costs nothing and needs no network, so a recorded run
  can guard instruction, tool-schema or orchestration changes on every commit.
- **Answer "why did it do that" from evidence.** The trace holds the verbatim requests and
  responses, every tool call with its arguments, shell exit codes, and the files the run changed —
  including the ones nobody mentioned.
- **Compare models on one fixed prefix.** `orca compare` forks a recorded run from a checkpoint onto
  several models with the same files and conversation prefix, so the model is the only variable.

## Prerequisites

- Python 3.10+
- Node.js 20+ (OrcaReplay is an npm CLI)
- An API key for whichever model your agent uses, for the recording pass only. The replay pass needs
  no key.

## Installation

```bash
npm install -g orcareplay
```

The installed command is `orca`.

## Use with agent

Wire the model through `LiteLlm` with a model id only — no `base_url` in code — so the origin comes
from the environment, which is what `orca record` sets for the child process.

```python
# agent.py
import asyncio
import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.genai import types

agent = Agent(
    name="orca_demo",
    model=LiteLlm(model=f"openai/{os.environ.get('MODEL', 'gpt-4o-mini')}"),
    instruction="You are terse. Answer in the fewest possible words.",
)


async def main() -> None:
    runner = InMemoryRunner(agent=agent, app_name="orca_demo")
    session = await runner.session_service.create_session(
        app_name="orca_demo", user_id="u1"
    )
    async for event in runner.run_async(
        user_id="u1",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text="Say hello in three words.")]
        ),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    print(part.text, end="")


asyncio.run(main())
```

Record it:

```bash
orca record generic-openai -- python agent.py
```

```text
info recording run=run_135c37894350 adapter=generic-openai proxy=http://127.0.0.1:52685
info recorded run=run_135c37894350 events=6 exit=0
```

Then replay it, with no provider reachable:

```bash
orca replay last
```

```text
info replaying run=run_135c37894350 exchanges=1 egress=blocked
info replay.done reused=1/1 exact=1 divergences=0 unmatched=0 exit=0
```

`exact=1` means the replayed request matched the recording byte for byte — instruction, message
assembly and parameters all reproduced. Your agent's own runner, event loop and tool dispatch
execute for real; only the model's answer comes from the trace.

To read the run rather than re-run it:

```bash
orca show last      # the timeline: model turns, tool calls, exit codes, files changed
orca graph last     # which event caused which
```

## Limits

Three, stated up front rather than discovered later.

- **`egress=blocked` means model-provider egress, not network isolation.** Replay serves the model's
  answers from the trace and calls no provider, but it still *executes the recorded tool calls for
  real*. An ADK tool that fetches a URL or writes to a database does it again. Replay is not a
  sandbox; run it inside one if that matters.
- **A matching replay is not a determinism result.** The model is not being re-asked — its recorded
  answers are served back. Whether a *fresh* run would behave the same way is a different question
  that replay cannot answer.
- **A trace is a full transcript.** It holds whatever the run held. `orca scrub` is best-effort — it
  matches known key shapes and high-entropy strings, and cannot know that a particular hostname or
  customer name is confidential — so review a trace before sharing it.

## Resources

- [OrcaReplay repository](https://github.com/Continuum-AI-Corp/OrcaReplay) — Apache-2.0
- [Framework integration notes](https://github.com/Continuum-AI-Corp/OrcaReplay/blob/main/docs/integrations.md) — what is captured for each framework, and what is not
- [Integration checks](https://github.com/Continuum-AI-Corp/OrcaReplay/tree/main/test/integrations) — each framework is recorded against a stub origin, the origin is killed, the run is replayed, and the numbers are asserted
