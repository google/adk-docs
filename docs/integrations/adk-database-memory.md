---
catalog_title: Database Memory Service
catalog_description: Durable memory service for ADK agents backed by SQLite, PostgreSQL, or MySQL via SQLAlchemy
catalog_icon: /integrations/assets/adk-database-memory.png
catalog_tags: ["data"]
---

# Database Memory Service for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[`adk-database-memory`](https://github.com/anmolg1997/adk-database-memory) is a drop-in durable `BaseMemoryService` for the Python ADK, backed by any async SQLAlchemy dialect. It provides persistent cross-session memory for agents without requiring a managed service: point it at SQLite for development, or at a production Postgres / MySQL instance for deployment.

## Use cases

- **Personalized assistants**: accumulate long-term user preferences, facts, and past decisions across sessions so the agent can recall them on demand.
- **Support and task agents**: persist conversation history across tickets and devices, so context is available whenever the user returns.
- **Self-hosted deployments**: when Vertex AI Memory Bank is not an option (on-prem, air-gapped, non-GCP cloud), keep memory on the database you already run.
- **Local development**: drop in SQLite for zero-config durable memory that survives restarts, then flip the connection string to Postgres in production.

## Prerequisites

- Python 3.10 or later.
- A database reachable over an async SQLAlchemy URL: SQLite file (zero setup), PostgreSQL, or MySQL / MariaDB. Any async SQLAlchemy dialect works.

## Installation

Install the package together with the driver for your database:

```bash
pip install "adk-database-memory[sqlite]"       # SQLite (via aiosqlite)
pip install "adk-database-memory[postgres]"     # PostgreSQL (via asyncpg)
pip install "adk-database-memory[mysql]"        # MySQL / MariaDB (via aiomysql)
```

The base install does not pull any database driver. Pick the extra that matches your backend, or install your own async driver separately.

## Use with agent

The service implements `google.adk.memory.base_memory_service.BaseMemoryService`, so it slots into any ADK `Runner` that accepts a `memory_service`:

```python
import asyncio

from adk_database_memory import DatabaseMemoryService
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

memory = DatabaseMemoryService("sqlite+aiosqlite:///memory.db")

agent = Agent(
    name="assistant",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant. Use your memory tool to recall facts about the user.",
)

async def main():
    async with memory:
        runner = InMemoryRunner(agent=agent, app_name="my_app")
        # ... run the agent, then persist the session to memory
        session = await runner.session_service.create_session(app_name="my_app", user_id="u1")
        # After the session completes:
        await memory.add_session_to_memory(session)

        # Later, recall relevant memories for a new query:
        result = await memory.search_memory(
            app_name="my_app",
            user_id="u1",
            query="what did we decide about the pricing model?",
        )
        for entry in result.memories:
            print(entry.author, entry.timestamp, entry.content)

asyncio.run(main())
```

## Supported backends

| Backend | Connection URL example | Extra |
| ---- | ---- | ---- |
| SQLite | `sqlite+aiosqlite:///memory.db` | `[sqlite]` |
| SQLite (in-memory) | `sqlite+aiosqlite:///:memory:` | `[sqlite]` |
| PostgreSQL | `postgresql+asyncpg://user:pass@host/db` | `[postgres]` |
| MySQL / MariaDB | `mysql+aiomysql://user:pass@host/db` | `[mysql]` |
| Any async SQLAlchemy dialect | depends on driver | bring your own |

## API

| Method | Description |
| ---- | ---- |
| `add_session_to_memory(session)` | Index every event in a completed session. |
| `add_events_to_memory(app_name, user_id, events, ...)` | Index an explicit slice of events (useful for streaming ingestion). |
| `search_memory(app_name, user_id, query)` | Return `MemoryEntry` objects whose indexed keywords overlap with the query, scoped to the given app and user. |

On first write the service creates a single table (`adk_memory_entries`) with an index on `(app_name, user_id)`. JSON content is stored as `JSONB` on PostgreSQL, `LONGTEXT` on MySQL, and `TEXT` on SQLite.

Retrieval uses the same keyword-extraction and matching approach as the in-memory and Firestore memory services in ADK. It is a durable, zero-infra starting point, not a semantic retriever. For embedding-based recall, pair this package with Vertex AI Memory Bank or a vector store.

## Resources

- [GitHub repository](https://github.com/anmolg1997/adk-database-memory): source code, issues, and examples.
- [PyPI package](https://pypi.org/project/adk-database-memory/): releases and install instructions.
- [ADK Memory overview](https://google.github.io/adk-docs/sessions/memory/): background on how ADK uses memory services.
