---
catalog_title: Mimir Memory
catalog_description: Add persistent, local, encrypted cross-session memory to ADK agents
catalog_icon: /integrations/assets/mimir.svg
catalog_tags: ["data"]
---

# Mimir Memory integration for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [`adk-mimir-memory`](https://github.com/Perseus-Computing-LLC/adk-mimir-memory)
integration connects your ADK agent to
[Mimir](https://github.com/Perseus-Computing-LLC/mimir), a persistent,
cross-session memory backend. Backed by a single Rust binary with an embedded
SQLite database, it requires **zero cloud dependencies**, and everything runs
locally. Memory is encrypted at rest with AES-256-GCM, and search combines FTS5
keyword matching with dense vector retrieval.

## Use cases

- **Persistent agent memory across restarts**: Sessions survive process
  restarts, and agents recall past conversations automatically
- **Private, air-gapped deployments**: No cloud dependency, and Mimir runs
  entirely on your machine with optional AES-256-GCM encryption
- **Hybrid search across memories**: Combine keyword (FTS5/BM25) and semantic
  (dense vector) search to find relevant past interactions
- **Workspace-aware agents**: Pair with Perseus for agents that know about your
  project files, git state, and configuration

## Prerequisites

- Python 3.10+
- The `mimir` binary (see [Installation](#installation))
- `google-adk>=1.0.0`

## Installation

Install the Python package:

```bash
pip install adk-mimir-memory
```

Then install the `mimir` binary: download the build for your platform from the
[Mimir releases page](https://github.com/Perseus-Computing-LLC/mimir/releases)
and place it on your `PATH`. The service looks for `mimir` by default, or pass
`mimir_binary="/absolute/path/to/mimir"` to `MimirMemoryService`.

## Use with agent

Create the `MimirMemoryService`, pass it to your `Runner`, and give the agent
the `load_memory` tool so it can recall past sessions:

```python
from adk_mimir_memory import MimirMemoryService
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import load_memory

agent = Agent(
    name="memory_assistant",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant with long-term memory.",
    tools=[load_memory],
)

runner = Runner(
    agent=agent,
    app_name="mimir_app",
    session_service=InMemorySessionService(),
    memory_service=MimirMemoryService(db_path="~/.adk/mimir.db"),
)
```

After a session completes, call
`await memory_service.add_session_to_memory(session)` to persist it. The agent
recalls relevant memories in later sessions through the `load_memory` tool. See
[ADK memory](/sessions/memory/) for the full ingest-and-recall flow.

### Perseus live context (optional)

For live workspace awareness, install the `perseus` extra:

```bash
pip install adk-mimir-memory[perseus]
```

Then use the prebuilt `perseus_context_agent`, which resolves `@file`,
`@search`, and `@memory` directives at inference time:

```python
from adk_mimir_memory.perseus_context import perseus_context_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# The pre-built agent ships without a model; set one before use.
perseus_context_agent.model = "gemini-flash-latest"

runner = Runner(
    agent=perseus_context_agent,
    app_name="perseus_app",
    session_service=InMemorySessionService(),
    memory_service=MimirMemoryService(db_path="~/.adk/mimir.db"),
)
```

Set Perseus directives via session state when creating the session (inside an
async function):

```python
session = await runner.session_service.create_session(
    app_name="perseus_app",
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

| Backend | Dependencies | At-rest encryption | Search | Hosting |
|---|---|---|---|---|
| **InMemoryMemoryService** | None | Not persisted | Keyword | Local (ephemeral) |
| **VertexAiMemoryBankService** | Google Cloud | Google-managed (CMEK optional) | Semantic (Gemini) | Google Cloud |
| **VertexAiRagMemoryService** | Google Cloud | Google-managed (CMEK optional) | Vector similarity | Google Cloud |
| **MimirMemoryService** | `mimir` binary | Local AES-256-GCM (optional) | Hybrid (FTS5 + dense) | Local |

## Resources

- [adk-mimir-memory on GitHub](https://github.com/Perseus-Computing-LLC/adk-mimir-memory)
- [Mimir (backing service)](https://github.com/Perseus-Computing-LLC/mimir)
- [Perseus (context engine)](https://github.com/Perseus-Computing-LLC/perseus)
