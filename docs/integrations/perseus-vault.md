---
catalog_title: Perseus Vault Memory
catalog_description: Add persistent, local, encrypted cross-session memory to ADK agents
catalog_icon: /integrations/assets/perseus-vault.svg
catalog_tags: ["data"]
---

# Perseus Vault Memory integration for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [`adk-perseus-vault-memory`](https://github.com/Perseus-Computing-LLC/adk-mimir-memory)
integration connects your ADK agent to
[Perseus Vault](https://github.com/Perseus-Computing-LLC/perseus-vault), a
persistent, cross-session memory backend (formerly "Mimir"/"Mneme"). Backed by a
single Rust binary with an embedded SQLite database, everything runs locally.
Memory is encrypted at rest with AES-256-GCM, and search combines FTS5 keyword
matching with dense vector retrieval.

## Prerequisites

- Python 3.10+
- The `perseus-vault` binary on your `PATH`
- `google-adk>=1.0.0`

## Installation

```bash
pip install adk-perseus-vault-memory
```

Install the `perseus-vault` binary from the
[releases page](https://github.com/Perseus-Computing-LLC/perseus-vault/releases)
(or `cargo install perseus-vault`) and place it on your `PATH`, or pass
`vault_binary="/path/to/perseus-vault"` to `PerseusVaultMemoryService`.

## Use with agent

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

After a session completes, call `await memory_service.add_session_to_memory(session)`
to persist it; the agent recalls memories in later sessions through the
`load_memory` tool. See [ADK memory](/sessions/memory/) for the full
ingest-and-recall flow.

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
| **VertexAiMemoryBankService** | Google Cloud | Google-managed | Semantic (Gemini) | Google Cloud |
| **VertexAiRagMemoryService** | Google Cloud | Google-managed | Vector similarity | Google Cloud |
| **PerseusVaultMemoryService** | `perseus-vault` binary | Local AES-256-GCM | Hybrid (FTS5 + dense) | Local |

## Resources

- [adk-perseus-vault-memory on GitHub](https://github.com/Perseus-Computing-LLC/adk-mimir-memory)
- [adk-perseus-vault-memory on PyPI](https://pypi.org/project/adk-perseus-vault-memory/)
- [Perseus Vault (backing service)](https://github.com/Perseus-Computing-LLC/perseus-vault)
- [Perseus Context integration](/integrations/perseus/)