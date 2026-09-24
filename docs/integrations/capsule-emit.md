---
catalog_title: Agent Action Capsule (capsule-emit)
catalog_description: Sealed, content-addressed evidence records for ADK tool calls — audit evidence whose integrity a third party can check
catalog_icon: /integrations/assets/capsule-emit.svg
catalog_tags: ["observability"]
---

# Agent Action Capsule (capsule-emit) for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[capsule-emit](https://github.com/action-state-group/capsule-emit) records each completed tool call in an ADK agent as an **Agent Action Capsule**: a sealed, signed, content-addressed evidence record. Capsules are audit and compliance evidence for what an agent actually did — complementary to tracing.

## Why capsules for ADK?

ADK ships its own OpenTelemetry-based tracing, which answers *"what happened, for the operator."* Capsules answer a different question: *"give a stranger a record they can check"* — an auditor, a counterparty, a compliance team reviewing an evidence bundle after the fact. A capsule ledger is the operator's account of what the agent did, kept in a form an outside party can check against an accepted external checkpoint once one covers it — not independent proof that the recorded events occurred.

- **Sealed, content-addressed records**: every capsule's identity is a digest over its own contents, so a record cannot be quietly edited in place — tamper-*evidence* against a reference the other party already holds (an accepted witness checkpoint, a previously shared digest), not tamper-*proofing* on its own.
- **Digest-only commitment**: tool inputs/outputs are committed as SHA-256 digests; raw content stays in your environment. (A digest of low-entropy content can still be confirmed by guessing — treat digests as commitments, not encryption.)
- **Offline checks**: anyone holding the ledger can re-verify structure, content addressing, chain links, and each record's producer signature with no service and no credentials. A signature proves the key named in the record signed it, not who holds that key: the signature and key id sit outside the digest, so a ledger re-signed under a fresh key still passes.
- **Checkpointed tamper-evidence (on by default)**: the emitter posts checkpoints (log size, root hash, timestamp; never record content) to a witness; the cadence and endpoint are in the table below. Each checkpoint the witness accepts gives an outside party a reference to check the ledger against, to the extent that party trusts the witness to be independent of you. Records sealed after the last accepted checkpoint are not yet committed outside your environment; a run that seals fewer than 100 records, all within 900 seconds, exits without posting one. `CAPSULE_WITNESS=off` stops all egress; offline verification never consults a checkpoint either way. The older per-seal SCITT anchor is a legacy channel, off by default.
- **Observation mode stamped on every capsule**: records state *how* they were observed (`in_path` for the callback path, `event_stream` for the event tap) — provenance the consumer can weigh, not a hidden default.

## Setup

Install the ADK extra:

```shell
pip install "capsule-emit[adk]"
```

### Path 1 — tool callbacks

Pass the emitter's bound callbacks to your agent. One sealed `executed` capsule is appended to the ledger file per completed tool call; consequential tools declare their world-effect once, at construction (`effects=`), and read-only calls assert none:

```python
from capsule_emit.adapters.adk import ADKCapsuleEmitter

emitter = ADKCapsuleEmitter(
    operator="acme-co",
    developer="po-agent@v1",
    model={"provider": "google", "model_id": "gemini-2.0-flash"},
    ledger="ledger.jsonl",  # the default; capsules append here as JSON lines
    effects={"write_order": {"type": "write_order", "status": "dispatched"}},
)
```

```python
from google.adk.agents import LlmAgent


def lookup_order(order_id: str) -> dict:
    """Example tool."""
    return {"order_id": order_id, "status": "shipped"}


agent = LlmAgent(
    name="writer",
    model="gemini-2.0-flash",
    tools=[lookup_order],
    before_tool_callback=emitter.before_tool_callback,
    after_tool_callback=emitter.after_tool_callback,
)
```

### Path 2 — event-stream tap

For apps that consume the `Runner` event stream instead of registering tool callbacks:

```python
async def run_with_evidence(runner, session, message, emitter):
    async for event in runner.run_async(
        user_id=session.user_id, session_id=session.id, new_message=message
    ):
        emitter.tap_event(event)  # seals a capsule per completed tool call
        # ... your own event handling continues
```

Capsules sealed on this path are stamped `observation_mode="event_stream"` — the emitter observed the runtime's narration rather than sitting in the call path.

### Check the evidence

```python
import json

from capsule_emit.signing import verify_store_signed

capsules = [json.loads(line) for line in open("ledger.jsonl") if line.strip()]
if not capsules:
    raise SystemExit("empty ledger — nothing to verify")
# checks each signature against the key named in the record, not against a key you trust
results = verify_store_signed(capsules, require_signature=True)
ok = all(r.ok for r in results)
print(f"{len(capsules)} capsules, verify: {'ALL OK' if ok else 'FAILURES'}")
```

## What gets recorded

| Field | Content |
|---|---|
| `action_id` / tool name | which tool call this capsule records |
| input / output digests | SHA-256 commitments — raw content never leaves your environment |
| `effect` | declared per consequential tool via `effects={...}`; read-only calls assert no world-effect |
| `observation_mode` | `in_path` (callback path) or `event_stream` (event tap) — how the record was observed |
| `signature` / `key_id` | a COSE_Sign1 producer signature over the capsule id, and the key that made it — outside the digest, so they prove which key signed, not who holds it |
| network egress | by default, a checkpoint (log size, root hash, timestamp; never record content) after every 100 records, or at the next seal once 900 seconds have passed (no background timer), posted to the project's public witness at `witness.agentactioncapsule.org`; `CAPSULE_WITNESS_URL` sends it to a witness you choose, `CAPSULE_WITNESS=off` disables it. The legacy per-seal anchor is off unless `CAPSULE_ANCHOR=legacy-on` |

## Honest limits (by design)

- **Errors are opt-in on the callback path**: ADK's `after_tool_callback` fires only after a tool *returns*; a tool that raises produces no capsule there. Call `emitter.emit_errored(...)` from your own `except` block to seal the failed attempt. (The event tap seals error-shaped responses like any other output.)
- **Refusals stay a policy act**: `blocked` / `denied` verdicts are never inferred. When your gate blocks a tool, call `emit_blocked` / `emit_denied`, or wrap a predicate with `emitter.guard(...)` to get a `before_tool_callback` that seals the block and short-circuits the tool.
- **Integrity is not completeness**: offline verification proves the presented ledger is *internally consistent* — every digest recomputes and every chain link holds. It does not prove the ledger is the one originally written (an accepted witness checkpoint is the outside reference for that, as of the last one), and it never proves the operator recorded everything.

The capsule format is an open spec ([`draft-mih-scitt-agent-action-capsule`](https://datatracker.ietf.org/doc/draft-mih-scitt-agent-action-capsule/), an individual Internet-Draft, work in progress — as is [SCITT](https://datatracker.ietf.org/wg/scitt/about/) itself) with an Apache-2.0 reference implementation.
