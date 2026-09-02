---
catalog_title: Synap
catalog_description: Add persistent, cross-session long-term memory to ADK agents
catalog_icon: /integrations/assets/synap.png
catalog_tags: ["data"]
---

# Synap integration for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [`maximem-synap-google-adk`](https://pypi.org/project/maximem-synap-google-adk/)
plugin connects your ADK agent to [Synap](https://www.maximem.ai/synap), a managed
long-term memory layer for AI agents. Synap automatically extracts and
structures knowledge from conversations (facts, preferences, episodes,
emotions, and temporal events) and retrieves only what is semantically relevant
to the current query.

## Use cases

- **Persistent cross-session memory**: Give your ADK agents long-term memory
  that survives across sessions and deployments, with no manual bookkeeping.
- **Multi-tenant isolation**: Memory is scoped to `user_id` and `customer_id`,
  ensuring strict isolation in multi-user deployments.
- **Semantic recall**: Server-side extraction surfaces only what is relevant to
  the current query, keeping prompts short and tokens efficient.

## Prerequisites

- A [Synap](https://synap.maximem.ai) account and API key
- [Gemini API key](https://aistudio.google.com/app/api-keys) (or any other model
  provider configured with ADK)

## Installation

```bash
pip install maximem-synap-google-adk maximem-synap
```

Set the following environment variable:

```bash
export SYNAP_API_KEY="your-synap-api-key"
```

## Use with agent

`create_synap_tools(...)` returns two `FunctionTool` instances, `search_memory`
and `store_memory`, that the agent can call to recall and persist memories on
demand.

```python
--8<-- "examples/inline/python/integrations/synap/001-use-with-agent.py"
```

Run with:

```bash
adk run path/to/your_agent
```

Teach the agent something on the first turn (e.g. *"I'm allergic to peanuts"*),
then ask about it on a later turn. Synap retrieves the relevant memory
automatically, even across separate `adk run` invocations.

## Available tools

| Tool | Description |
|------|-------------|
| `search_memory` | Semantic search over the user's stored memories. Takes a natural-language query and returns the most relevant facts, preferences, and episodes. |
| `store_memory` | Persist an explicit fact in the user's long-term memory. The agent calls this when the user shares something worth remembering. |

## Resources

- [Synap documentation](https://docs.maximem.ai)
- [ADK integration guide](https://docs.maximem.ai/integrations/google-adk)
- [`maximem-synap-google-adk` on PyPI](https://pypi.org/project/maximem-synap-google-adk/)
- [Open source integration package](https://github.com/maximem-ai/maximem_synap_sdk/tree/main/packages/integrations/synap-google-adk)
- [Synap Dashboard](https://synap.maximem.ai)
