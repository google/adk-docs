---
catalog_title: Mimir Memory
catalog_description: Persistent, local, encrypted cross-session memory for ADK agents — backed by Mimir
catalog_icon: /integrations/assets/mimir.svg
---

# Mimir Memory — Persistent Cross-Session Memory for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

Mimir provides persistent, encrypted, cross-session memory for ADK agents.
Backed by a single Rust binary with an embedded SQLite database, it requires
**zero cloud dependencies** — everything runs locally. Memory is encrypted at
rest with AES-256-GCM, and search combines FTS5 keyword matching with dense
vector retrieval.

## Use cases

- **Persistent agent memory across restarts**: Sessions survive process restarts — agents recall past conversations automatically
- **Private, air-gapped deployments**: No cloud dependency — Mimir runs entirely on your machine with optional AES-256-GCM encryption
- **Hybrid search across memories**: Combine keyword (FTS5/BM25) and semantic (dense vector) search to find relevant past interactions
- **Workspace-aware agents**: Pair with Perseus for agents that know about your project files, git state, and configuration

## Prerequisites

- Python 3.10+
- The `mimir` binary (see [Installation](#installation))
- `google-adk>=1.0.0`

## Installation

```bash
pip install adk-mimir-memory
```

Then download the `mimir` binary from the [Mimir releases page](https://github.com/Perseus-Computing-LLC/mimir/releases),
or build from source:

```bash
cargo install mimir
```

## Use with agent

```python
from google.adk.agents import Agent
from adk_mimir_memory import MimirMemoryService

agent = Agent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant with persistent memory.",
    memory_service=MimirMemoryService(
        db_path="~/.adk/mimir.db",
    ),
)
```

### Perseus Live Context (Optional)

For live workspace awareness, install the `perseus` extra:

```bash
pip install adk-mimir-memory[perseus]
```

```python
from adk_mimir_memory.perseus_context import perseus_context_agent

# The agent resolves @file, @search, @memory directives at inference time
runner.run_async(
    user_id="user",
    session_id="session",
    new_message=types.Content(role="user", parts=[types.Part.from_text(
        text="What does the README say about deployment?"
    )]),
    agent=perseus_context_agent,
)
```

Set Perseus directives via session state:

```python
session = await runner.session_service.create_session(
    app_name="my_app",
    user_id="user",
    state={
        "_perseus_directives": "@file AGENTS.md @file README.md @memory deployment",
        "_perseus_workspace": "/path/to/project",
    },
)
```

## Available memory operations

| Method | Description |
|---|---|
| `add_session_to_memory(session)` | Persist a full session's events |
| `add_events_to_memory(...)` | Append incremental event deltas |
| `add_memory(...)` | Store explicit memory entries |
| `search_memory(...)` | FTS5 keyword search across memories |

## Backend comparison

| Backend | Dependencies | Encryption | Hybrid Search | Local |
|---|---|---|---|---|
| **InMemoryMemoryService** | None | ❌ | ❌ | ✅ |
| **VertexAiMemoryBankService** | GCP + Gemini | ❌ | Gemini-driven | ❌ |
| **VertexAiRagMemoryService** | GCP + RAG | ❌ | GCP vector | ❌ |
| **MimirMemoryService** | Single binary | ✅ AES-256 | ✅ BM25+FTS5+Dense | ✅ |

## Resources

- [adk-mimir-memory on GitHub](https://github.com/Perseus-Computing-LLC/adk-mimir-memory)
- [Mimir (backing service)](https://github.com/Perseus-Computing-LLC/mimir)
- [Perseus (context engine)](https://github.com/Perseus-Computing-LLC/perseus)
