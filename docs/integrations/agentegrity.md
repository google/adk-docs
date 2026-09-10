---
catalog_title: Agentegrity by Cogensec
catalog_description: Evaluate agent integrity and collect tamper-evident security evidence
catalog_icon: /integrations/assets/agentegrity.png
catalog_tags: ["observability", "evaluation"]
---

# Agentegrity by Cogensec: observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Agentegrity](https://github.com/Cogensec/agentegrity) is an open-source agent
integrity evaluation framework owned and maintained by
[Cogensec](https://github.com/Cogensec). Its Python adapter attaches
callbacks to ADK agents to evaluate observed inputs and tool activity and
record security evidence without replacing the ADK runner.

## Overview

- **Integrity scoring and adversarial detection**: Evaluate observed events
  through adversarial, cortical, governance, and recovery layers. Inspect
  composite and per-property scores and detections such as prompt injection
  in user inputs and tool outputs.
- **Behavioral drift and reasoning/memory integrity**: The cortical layer
  supports behavioral baselines, reasoning-chain validation, and memory
  integrity checks. These depend on supplied context and baseline configuration;
  instrumentation alone does not capture model reasoning or ADK memory reads.
- **Decision provenance and audit chains**: Record tool-call decisions and
  evaluation results in a hash-linked, tamper-evident audit chain. Optional
  Ed25519 signing produces cryptographically signed attestations.
- **Recovery verification**: Evaluate baseline availability, integrity history,
  audit-chain consistency, and declared recovery capabilities. Checkpoint
  snapshot/restore requires a configured backend; the adapter does not
  automatically roll back ADK sessions or tool side effects.
- **Multi-agent topology evidence**: For an instrumented agent with
  `sub_agents`, record the root and its immediate children as a hierarchical
  topology in attestation evidence. This structural snapshot does not imply
  automatic instrumentation of every descendant or capture of peer messages.

The current adapter is observation-only: even with `enforce=True`, it does not
prevent tool calls. Scores describe the evidence available to the evaluator;
missing reasoning, memory, baseline, or peer context limits what can be assessed.

## Installation

Use Python 3.10 or later and install the ADK integration:

```bash
pip install "agentegrity[google-adk]"
```

## Setup

For the Gemini example below, configure credentials following the
[ADK Python quickstart](/get-started/python/). No Agentegrity account or API key
is required for local evaluation.

Agentegrity evaluates locally by default, but anonymous usage telemetry is
**enabled by default**. It includes adapter names, counts, enum values, and
rounded scores, not prompts, tool arguments, or agent content. Disable it before
starting your application:

```bash
export DO_NOT_TRACK=1
```

Alternatively, set `AGENTEGRITY_TELEMETRY_DISABLED=1` or call
`agentegrity.disable_telemetry()` before initialization.

Session exporters are separate from telemetry and can transmit full event
content, including prompts, tool arguments, and outputs. For local-only
Agentegrity evaluation, disable telemetry, do not register exporters, and leave
`AGENTEGRITY_TOKEN` and `AGENTEGRITY_EXPORTER_URL` unset. Optional LLM-backed
checks also require an external model provider when configured. The ADK agent's
own model and tool network calls are independent of these settings.

## Use with agent

Save this example as `agentegrity_example.py` and run it with
`python agentegrity_example.py` after configuring your model credentials.

```python
import asyncio
from pprint import pprint

import agentegrity
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types


def get_store_hours() -> dict:
    """Return the example store's opening hours."""
    return {"hours": "Monday through Friday, 09:00 to 17:00"}


async def main():
    runtime = agentegrity.init(frameworks=["google_adk"])
    try:
        root_agent = Agent(
            name="store_assistant",
            model="gemini-flash-latest",
            instruction="Use get_store_hours to answer questions about opening hours.",
            tools=[get_store_hours],
        )
        root_agent = runtime.instrument(root_agent)
        runner = InMemoryRunner(agent=root_agent, app_name="store_app")
        session = await runner.session_service.create_session(
            app_name="store_app", user_id="example_user"
        )
        async for event in runner.run_async(
            user_id="example_user",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text="When is the store open?")]
            ),
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts or []:
                    if part.text:
                        print(part.text)

        pprint(runtime.report()["google_adk"])
        adapter = runtime.adapters["google_adk"]
        for event in adapter.events:
            if event.evaluation_result is not None:
                pprint(event.evaluation_result.to_dict())
    finally:
        agentegrity.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
```

Instrumentation modifies and returns the same agent, attaching before/after
agent and tool callbacks. The report includes evaluation, event, attestation,
and decision counts, `chain_hash_linked`, and attached `exporters`. Individual
scores are available on adapter events; the summary is not itself an integrity
score. An empty exporter list means no session exporter is attached, not that
telemetry or model network calls are disabled.

## Signed attestations

The runtime example creates hash-linked records, but does not configure signing.
Install the optional cryptographic dependency to sign records explicitly:

```bash
pip install "agentegrity[crypto]"
```

After the run, before shutdown, the following can sign the collected attestation
and decision records using an in-memory key:

```python
from agentegrity.core.attestation import generate_signing_key

signing_key = generate_signing_key()
for record in adapter.attestation_chain.records:
    record.sign(signing_key)
    assert record.verify(signing_key.public_key())
```

For durable verification, manage and retain signing keys securely and pin the
trusted public key independently of the records. Hash-link verification alone
does not authenticate the signer or prove the agent's behavior was safe.

## Support and Resources

- [Agentegrity repository and configuration](https://github.com/Cogensec/agentegrity)
- [Agentegrity on PyPI](https://pypi.org/project/agentegrity/)
- [ADK adapter implementation](https://github.com/Cogensec/agentegrity/blob/main/src/agentegrity/adapters/google_adk.py)
- [Telemetry and opt-out](https://github.com/Cogensec/agentegrity/blob/main/docs/telemetry.md)
- [Report an issue](https://github.com/Cogensec/agentegrity/issues)
