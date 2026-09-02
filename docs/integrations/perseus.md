---
catalog_title: Perseus Context
catalog_description: Compile deterministic, workspace-aware context for ADK agents
catalog_icon: /integrations/assets/perseus.svg
catalog_tags: ["data", "mcp"]
---

# Perseus Context integration for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [`adk-perseus-context`](https://github.com/Perseus-Computing-LLC/adk-perseus-context)
integration injects a deterministically compiled context into your ADK agent's
system instruction. It is powered by
[Perseus](https://github.com/Perseus-Computing-LLC/perseus), an open-source
context compiler: Perseus resolves directives like `@file`, `@search`, and
`@memory` into one byte-stable context string at inference time, with no
retrieval index, no embeddings, and no extra LLM round-trip. Everything runs
locally.

Perseus is a context compiler, not a memory or RAG backend. For persistent
cross-session memory, pair it with its companion, [Perseus Vault](/integrations/perseus-vault/).

## Use cases

- **Deterministic context assembly**: The same inputs always compile to the same
  context, with byte-identical builds and no per-query retrieval variance
- **Workspace-aware agents**: Resolve `@file`, `@include`, `@search`, and
  `@memory` directives so the agent sees current project files and state
- **Index-free, local context**: No vector store, no embeddings, no cloud. The
  context is compiled on the machine that runs the agent
- **Full coverage at a fixed size**: Pull in exactly the context you declared,
  rather than a top-k slice

## Prerequisites

- Python 3.10+
- `google-adk>=1.14.0`
- `perseus-ctx>=1.0.10` (installed automatically with `adk-perseus-context`)

## Installation

```bash
pip install adk-perseus-context
```

## Use with agent

There are two ways to inject a compiled Perseus context. Use the plugin for a
context shared across every agent in a `Runner`, or the callback for a single
agent. `source` is a path to a `.perseus` file or an inline string starting with
`@perseus`.

### Runner-wide (plugin)

```python
--8<-- "examples/inline/python/integrations/perseus/001-runner-wide-plugin.py"
```

### Single agent (callback)

```python
--8<-- "examples/inline/python/integrations/perseus/002-single-agent-callback.py"
```

Either way, the compiled context is appended to the request's system instruction
(via ADK's `LlmRequest.append_instructions`) on every model call. If Perseus is
unavailable or a compile fails, the request proceeds without injected context
and a warning is logged (`fail_open=True` by default).

### Per-session context

Override the source per session through session state. This is useful when each
user or task targets a different workspace or directive set. Create the session
inside an async function:

```python
--8<-- "examples/inline/python/integrations/perseus/003-per-session-context.py"
```

## Use as an MCP server (optional)

Perseus also ships an MCP server that exposes its directives as tools, so you
can consume it through ADK's `McpToolset` instead of (or alongside) the plugin:

```python
--8<-- "examples/inline/python/integrations/perseus/004-use-as-an-mcp-server-optional.py"
```

## Plugin reference

| Entry point | Scope | Description |
|---|---|---|
| `PerseusContextPlugin(source)` | Runner-wide | Injects the compiled context into every agent's model request |
| `perseus_before_model_callback(source)` | Single agent | A `before_model_callback` that injects the compiled context |
| `_perseus_source` / `_perseus_workspace` | Session state | Per-session overrides of the source and workspace |

## Comparison

| Approach | Index / embeddings | Extra model call | Output stability | Coverage |
|---|---|---|---|---|
| Naive context dump | None | No | Stable | Everything in the prompt |
| RAG / vector retrieval | Required | Query embedding | Varies with query | Top-k results |
| Perseus compile | None | No | Byte-identical | Full, declared |

## Resources

- [adk-perseus-context on GitHub](https://github.com/Perseus-Computing-LLC/adk-perseus-context)
- [adk-perseus-context on PyPI](https://pypi.org/project/adk-perseus-context/)
- [Perseus (context engine)](https://github.com/Perseus-Computing-LLC/perseus)
- [Perseus Vault Memory integration](/integrations/perseus-vault/)
