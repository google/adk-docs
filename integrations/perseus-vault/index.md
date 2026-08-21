# Perseus Vault Memory integration for ADK

Supported in ADKPython

The [`adk-perseus-vault-memory`](https://github.com/Perseus-Computing-LLC/adk-mimir-memory) integration connects your ADK agent to [Perseus Vault](https://github.com/Perseus-Computing-LLC/perseus-vault), a persistent, cross-session memory backend. Backed by a single Rust binary with an embedded SQLite database, it requires **zero cloud dependencies**, and everything runs locally. Memory is encrypted at rest with AES-256-GCM, and search combines FTS5 keyword matching with dense vector retrieval.

## Use cases

- **Persistent agent memory across restarts**: Sessions survive process restarts, and agents recall past conversations automatically
- **Private, air-gapped deployments**: No cloud dependency, and Perseus Vault runs entirely on your machine with optional AES-256-GCM encryption
- **Hybrid search across memories**: Combine keyword (FTS5/BM25) and semantic (dense vector) search to find relevant past interactions
- **Workspace-aware agents**: Pair with Perseus for agents that know about your project files, git state, and configuration

## Prerequisites

- Python 3.10+
- The `perseus-vault` binary (see [Installation](#installation))
- `google-adk>=1.0.0`

## Installation

Install the Python package:

```bash
pip install adk-perseus-vault-memory
```

Then install the `perseus-vault` binary: download the build for your platform from the [releases page](https://github.com/Perseus-Computing-LLC/perseus-vault/releases) and place it on your `PATH`. The service looks for `perseus-vault` by default, or pass `vault_binary="/absolute/path/to/perseus-vault"` to `PerseusVaultMemoryService`.

## Use with agent

Create the `PerseusVaultMemoryService`, pass it to your `Runner`, and give the agent the `load_memory` tool so it can recall past sessions:

```python
from adk_perseus_vault_memory import PerseusVaultMemoryService
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
    app_name="perseus_vault_app",
    session_service=InMemorySessionService(),
    memory_service=PerseusVaultMemoryService(db_path="~/.adk/vault.db"),
)
```

After a session completes, call `await memory_service.add_session_to_memory(session)` to persist it; the agent recalls memories in later sessions through the `load_memory` tool. See [ADK memory](/sessions/memory/) for the full ingest-and-recall flow.

### Perseus live context (optional)

For live workspace awareness, install the `perseus` extra:

```bash
pip install adk-perseus-vault-memory[perseus]
```

Then use the prebuilt `perseus_context_agent`, which resolves `@file`, `@search`, and `@memory` directives at inference time:

```python
from adk_perseus_vault_memory.perseus_context import perseus_context_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# The pre-built agent ships without a model; set one before use.
perseus_context_agent.model = "gemini-flash-latest"

runner = Runner(
    agent=perseus_context_agent,
    app_name="perseus_app",
    session_service=InMemorySessionService(),
    memory_service=PerseusVaultMemoryService(db_path="~/.adk/vault.db"),
)
```

Set Perseus directives via session state when creating the session (inside an async function):

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

| Method                           | Description                         |
| -------------------------------- | ----------------------------------- |
| `add_session_to_memory(session)` | Persist a full session's events     |
| `add_events_to_memory(...)`      | Append incremental event deltas     |
| `add_memory(...)`                | Store explicit memory entries       |
| `search_memory(...)`             | FTS5 keyword search across memories |

## Backend comparison

| Backend                       | Dependencies           | At-rest encryption | Search                | Hosting           |
| ----------------------------- | ---------------------- | ------------------ | --------------------- | ----------------- |
| **InMemoryMemoryService**     | None                   | Not persisted      | Keyword               | Local (ephemeral) |
| **VertexAiMemoryBankService** | Google Cloud           | Google-managed     | Semantic (Gemini)     | Google Cloud      |
| **VertexAiRagMemoryService**  | Google Cloud           | Google-managed     | Vector similarity     | Google Cloud      |
| **PerseusVaultMemoryService** | `perseus-vault` binary | Local AES-256-GCM  | Hybrid (FTS5 + dense) | Local             |

## Resources

- [adk-perseus-vault-memory on GitHub](https://github.com/Perseus-Computing-LLC/adk-mimir-memory)
- [adk-perseus-vault-memory on PyPI](https://pypi.org/project/adk-perseus-vault-memory/)
- [Perseus Vault (backing service)](https://github.com/Perseus-Computing-LLC/perseus-vault)
- [Perseus Context integration](/integrations/perseus/)
