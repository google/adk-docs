# Perseus Context integration for ADK

Supported in ADKPython

The [`adk-perseus-context`](https://github.com/Perseus-Computing-LLC/adk-perseus-context) integration injects a deterministically compiled context into your ADK agent's system instruction. It is powered by [Perseus](https://github.com/Perseus-Computing-LLC/perseus), an open-source context compiler: Perseus resolves directives like `@file`, `@search`, and `@memory` into one byte-stable context string at inference time, with no retrieval index, no embeddings, and no extra LLM round-trip. Everything runs locally.

Perseus is a context compiler, not a memory or RAG backend. For persistent cross-session memory, pair it with its companion, [Perseus Vault](/integrations/perseus-vault/).

## Use cases

- **Deterministic context assembly**: The same inputs always compile to the same context, with byte-identical builds and no per-query retrieval variance
- **Workspace-aware agents**: Resolve `@file`, `@include`, `@search`, and `@memory` directives so the agent sees current project files and state
- **Index-free, local context**: No vector store, no embeddings, no cloud. The context is compiled on the machine that runs the agent
- **Full coverage at a fixed size**: Pull in exactly the context you declared, rather than a top-k slice

## Prerequisites

- Python 3.10+
- `google-adk>=1.14.0`
- `perseus-ctx>=1.0.10` (installed automatically with `adk-perseus-context`)

## Installation

```bash
pip install adk-perseus-context
```

## Use with agent

There are two ways to inject a compiled Perseus context. Use the plugin for a context shared across every agent in a `Runner`, or the callback for a single agent. `source` is a path to a `.perseus` file or an inline string starting with `@perseus`.

### Runner-wide (plugin)

```python
from adk_perseus_context import PerseusContextPlugin
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Help the user.",
)

app = App(
    name="perseus_app",
    root_agent=agent,
    plugins=[PerseusContextPlugin("context.perseus")],
)

runner = Runner(
    app=app,
    session_service=InMemorySessionService(),
)
```

### Single agent (callback)

```python
from adk_perseus_context import perseus_before_model_callback
from google.adk.agents import Agent

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Help the user.",
    before_model_callback=perseus_before_model_callback("context.perseus"),
)
```

Either way, the compiled context is appended to the request's system instruction (via ADK's `LlmRequest.append_instructions`) on every model call. If Perseus is unavailable or a compile fails, the request proceeds without injected context and a warning is logged (`fail_open=True` by default).

### Per-session context

Override the source per session through session state. This is useful when each user or task targets a different workspace or directive set. Create the session inside an async function:

```python
session = await runner.session_service.create_session(
    app_name="perseus_app",
    user_id="user",
    state={
        "_perseus_source": "@perseus\n@file AGENTS.md\n@memory deployment",
        "_perseus_workspace": "/path/to/project",
    },
)
```

## Use as an MCP server (optional)

Perseus also ships an MCP server that exposes its directives as tools, so you can consume it through ADK's `McpToolset` instead of (or alongside) the plugin:

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

perseus_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="perseus",
            args=["mcp", "serve", "--workspace", "."],
        )
    )
)

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Use Perseus tools to read workspace context.",
    tools=[perseus_tools],
)
```

## Plugin reference

| Entry point                              | Scope         | Description                                                   |
| ---------------------------------------- | ------------- | ------------------------------------------------------------- |
| `PerseusContextPlugin(source)`           | Runner-wide   | Injects the compiled context into every agent's model request |
| `perseus_before_model_callback(source)`  | Single agent  | A `before_model_callback` that injects the compiled context   |
| `_perseus_source` / `_perseus_workspace` | Session state | Per-session overrides of the source and workspace             |

## Comparison

| Approach               | Index / embeddings | Extra model call | Output stability  | Coverage                 |
| ---------------------- | ------------------ | ---------------- | ----------------- | ------------------------ |
| Naive context dump     | None               | No               | Stable            | Everything in the prompt |
| RAG / vector retrieval | Required           | Query embedding  | Varies with query | Top-k results            |
| Perseus compile        | None               | No               | Byte-identical    | Full, declared           |

## Resources

- [adk-perseus-context on GitHub](https://github.com/Perseus-Computing-LLC/adk-perseus-context)
- [adk-perseus-context on PyPI](https://pypi.org/project/adk-perseus-context/)
- [Perseus (context engine)](https://github.com/Perseus-Computing-LLC/perseus)
- [Perseus Vault Memory integration](/integrations/perseus-vault/)
