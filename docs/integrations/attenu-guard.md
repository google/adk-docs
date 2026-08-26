---
catalog_title: Attenu Guard
catalog_description: Per-agent permissions on every tool call and agent transfer; a sub-agent never holds more than its parent, with an offline-verifiable audit log
catalog_icon: /integrations/assets/attenu-guard.png
---

# Attenu Guard plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Attenu Guard](https://github.com/attenu-io/attenu-guard) is an open-source
(Apache-2.0) Python library that enforces per-agent permissions on every tool
call and every agent-to-agent handoff. The ADK plugin
(`attenu_guard.adapters.google_adk`) is one `BasePlugin`: register it once on
your `App` and every agent in the tree is covered. When control reaches a
sub-agent — by `transfer_to_agent`, `AgentTool`, or a task-mode sub-agent — the
plugin computes that agent's permission set as the *meet* of what the parent
holds and what you declared for the child, so a sub-agent never holds more than
its parent. Each tool call is checked before the tool body runs, and every
decision is written to a hash-chained audit log that verifies offline.

## Use cases

- **Narrow permissions at every transfer**: ADK decides *who* may transfer;
  the plugin decides *what the receiving agent may do*. An agent reached by a
  peer transfer inherits from the peer, so a narrow sibling cannot hand off
  into a wider one.
- **Deny before the tool body runs**: `before_tool_callback` checks the
  calling agent's permissions, including typed ceilings (row limits, spend
  caps, egress rank); a denial is returned to the model as the tool result, or
  raised as a hard stop with `raise_on_deny=True`.
- **Cascade revocation and an auditable record**: revoke any agent's guard and
  every descendant is denied immediately; `attenu-guard verify` checks the
  audit log's integrity and the parent ⊆ child relation from the exported
  bundle alone, with no service in the path.

## Prerequisites

- Python >= 3.10
- [ADK](https://adk.dev) >= 2.7
- No account, API key, or network access is required

## Installation

```bash
pip install 'attenu-guard[google-adk]'
```

## Use with agent

### Register the plugin on the App

Issue a root `Guard` for the orchestrator, declare what each sub-agent may
hold and how each tool maps onto a permission, and register the plugin once:

```python
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from attenu_guard import Authority, Guard, RowLimit, EgressRank
from attenu_guard.adapters.google_adk import DelegationGuardPlugin, ToolAuthority

summarizer = LlmAgent(
    model="gemini-flash-latest",
    name="summarizer",
    instruction="Summarize the CRM pipeline you are given.",
    tools=[crm_query],
)
orchestrator = LlmAgent(
    model="gemini-flash-latest",
    name="orchestrator",
    instruction="Answer questions about the sales pipeline; delegate summaries.",
    tools=[crm_query, crm_export],
    sub_agents=[summarizer],
)

# What the root holds.
root = Guard.issue("orchestrator", Authority(
    scopes={"crm.*", "mail.send"},
    ceilings=[RowLimit(100_000), EgressRank("any")], ttl=3600))

plugin = DelegationGuardPlugin(
    root,
    root_agent_name="orchestrator",
    # What each sub-agent may hold: the plugin grants the meet of this and the parent's set.
    delegations={"summarizer": Authority(
        scopes={"crm.read"},
        ceilings=[RowLimit(5_000), EgressRank("none")], ttl=900)},
    # How each tool maps onto a permission check (scope + the context the ceilings read).
    tools={
        "crm_query":  ToolAuthority("crm.read",   lambda a: {"rows": a.get("rows", 0)}),
        "crm_export": ToolAuthority("crm.export", lambda a: {"egress": "any"}),
    },
)

app = App(name="pipeline_app", root_agent=orchestrator, plugins=[plugin])
runner = Runner(app=app, session_service=InMemorySessionService())
```

With this configuration the summarizer can call `crm_query` for up to 5,000
rows and is denied `crm_export` before the tool body runs, whichever agent
transferred to it. An agent with no entry in `delegations`, and a tool with no
entry in `tools`, both fail closed.

### Revoke a subtree

```python
root.revoke(plugin.guard_for("summarizer").node_id)  # every descendant denies immediately
```

### Verify the record offline

```bash
attenu-guard view audit.jsonl          # render the delegation tree and verify the hash chain
attenu-guard verify bundle.json        # integrity, child ⊆ parent, containment — from the file alone
```

## Runnable example

The repository ships an ADK example with a scripted model (no API key) that
shows a peer transfer going through, the transferred-to agent being denied a
tool outside the transferring agent's permissions, and the audit bundle
verifying offline, plus a live variant:

```bash
pip install 'attenu-guard[google-adk]'
python examples/integrations/google_adk/peer_transfer/demo.py
# RUN_LIVE=1 GOOGLE_API_KEY=... python examples/integrations/google_adk/peer_transfer/live_smoke.py
```

See the [example README](https://github.com/attenu-io/attenu-guard/tree/main/examples/integrations/google_adk/peer_transfer)
and the [ADK page on attenu.io](https://attenu.io/docs/example-google-adk/).

## What the plugin does not do

It does not inspect prompts or model output, and it does not decide what a
task *should* be allowed to do — you declare each sub-agent's `Authority` and
each tool's `ToolAuthority` (the companion
[attenu-derive](https://github.com/attenu-io/attenu-derive) engine can compute
them from the app). Hook points and the trust boundary are documented in the
[adapter source](https://github.com/attenu-io/attenu-guard/blob/main/src/attenu_guard/adapters/google_adk.py).

## Resources

- [attenu-guard on GitHub](https://github.com/attenu-io/attenu-guard) · [PyPI](https://pypi.org/project/attenu-guard/)
- [Integrations matrix](https://attenu.io/docs/integrations/) · [Denial contract](https://attenu.io/docs/denial-contract/)
- [Draft specification](https://attenu.io/docs/internet-draft/) for the delegation-token wire format
