# Database Memory Service for ADK

Supported in ADKPython

[`adk-database-memory`](https://github.com/anmolg1997/adk-database-memory) is a drop-in persistent `BaseMemoryService` for ADK Python, backed by async SQLAlchemy. This integration provides persistent cross-session memory for ADK agents using your own database: use SQLite for development, or Postgres / MySQL for production.

## Use cases

- **Personalized assistants**: Accumulate long-term user preferences, facts, and past decisions across sessions so the agent can recall them on demand.
- **Support and task agents**: Persist conversation history across tickets and devices, so context is available whenever the user returns.
- **Self-hosted deployments**: When Vertex AI Memory Bank is not an option (on-prem, air-gapped, non-GCP cloud), keep memory on the database you already use.
- **Local development**: Drop in SQLite for zero-config persistent memory that survives restarts, then flip the connection string to Postgres in production.

## Prerequisites

- Python 3.10 or later
- A supported database: SQLite, PostgreSQL, or MySQL / MariaDB

## Installation

Install the package together with the driver for your database:

```bash
pip install "adk-database-memory[sqlite]"    # SQLite (via aiosqlite)
pip install "adk-database-memory[postgres]"  # PostgreSQL (via asyncpg)
pip install "adk-database-memory[mysql]"     # MySQL / MariaDB (via aiomysql)
```

The core package does not include any database drivers. Choose the extra that matches your backend, or install your own async driver separately.

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
    model="gemini-flash-latest",
    instruction="You are a helpful assistant.",
)

async def main():
    async with memory:
        # Run the agent, then persist the session to memory
        runner = InMemoryRunner(agent=agent, app_name="my_app")
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

| Backend                      | Connection URL example                   | Extra          |
| ---------------------------- | ---------------------------------------- | -------------- |
| SQLite                       | `sqlite+aiosqlite:///memory.db`          | `[sqlite]`     |
| SQLite (in-memory)           | `sqlite+aiosqlite:///:memory:`           | `[sqlite]`     |
| PostgreSQL                   | `postgresql+asyncpg://user:pass@host/db` | `[postgres]`   |
| MySQL / MariaDB              | `mysql+aiomysql://user:pass@host/db`     | `[mysql]`      |
| Any async SQLAlchemy dialect | depends on driver                        | bring your own |

## API

| Method                                                 | Description                                                                                                   |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| `add_session_to_memory(session)`                       | Index every event in a completed session.                                                                     |
| `add_events_to_memory(app_name, user_id, events, ...)` | Index an explicit slice of events (useful for streaming ingestion).                                           |
| `search_memory(app_name, user_id, query)`              | Return `MemoryEntry` objects whose indexed keywords overlap with the query, scoped to the given app and user. |

On first write, the service creates a single table (`adk_memory_entries`) with an index on `(app_name, user_id)`. JSON content is stored as `JSONB` on PostgreSQL, `LONGTEXT` on MySQL, and `TEXT` on SQLite.

Retrieval uses the same keyword-extraction and matching approach as the in-memory and Firestore memory services in ADK. For embedding-based recall, pair this package with Vertex AI Memory Bank or a vector store.

## Resources

- [GitHub repository](https://github.com/anmolg1997/adk-database-memory): source code, issues, and examples.
- [PyPI package](https://pypi.org/project/adk-database-memory/): releases and install instructions.
- [ADK Memory overview](/sessions/memory/): background on how ADK uses memory services.
