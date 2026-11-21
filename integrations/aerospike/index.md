# Aerospike integration for ADK

Supported in ADKPython

The [`adk-aerospike`](https://github.com/aerospike-community/adk-aerospike) integration connects your ADK agent to [Aerospike](https://aerospike.com/), a distributed real-time key-value database. It implements all three ADK Python storage interfaces on a single cluster using the native Aerospike client in your application process. Register the `aerospike://` URI scheme once and the `adk` CLI can use Aerospike for sessions, artifacts, and memory.

There are several ways to use this integration:

| Approach             | Description                                                                                                                       |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Session service**  | `AerospikeSessionService`: Scoped state (`app:`, `user:`, session), event history with chunked storage, atomic `append_event`.    |
| **Memory service**   | `AerospikeMemoryService`: Lexical word-overlap search via per-token posting-list keys; same semantics as `InMemoryMemoryService`. |
| **Artifact service** | `AerospikeArtifactService`: Versioned blobs per session or `user:` namespace.                                                     |
| **Full stack**       | Wire all three services into one `Runner`, or pass matching `aerospike://` URIs to `adk web` / `adk run`.                         |

## Use cases

- **Production agent persistence**: Keep conversation state, tool outputs, and user-scoped data across restarts and replicas without operating a separate memory service.
- **High-throughput agents**: Sub-millisecond reads and writes for chat, voice, and real-time orchestration where session append latency matters.
- **Lexical long-term memory**: Tokenize text at write time; search with point reads on posting-list keys (`app:user:kw:<token>`) and hydrate memory rows, with no embedding model required.
- **Multimodal artifacts**: Store images, files, and generated outputs with version history; `user:` filenames are visible across sessions (ADK contract).
- **Self-hosted and multi-tenant**: One namespace, composite secondary indexes for tenant-scoped artifact and memory operations; Community or Enterprise on-prem or cloud.

## Prerequisites

- Python 3.11 or later
- [ADK for Python](/get-started/python/) (`google-adk`)
- Aerospike Database 7.x or 8.x (Community or Enterprise)
- A reachable cluster (local Docker example below)

Local Aerospike for development:

```bash
docker run --rm -d --name aerospike -p 3000-3003:3000-3003 aerospike/aerospike-server:latest
```

For model calls in the runnable examples, set `GOOGLE_API_KEY` (or your model provider credentials).

## Installation

```bash
pip install google-adk adk-aerospike
```

## Use with agent

Plug `AerospikeSessionService` into any ADK `Runner` for a full multi-turn agent with persisted sessions.

```python
import asyncio

from adk_aerospike import AerospikeSessionService
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.genai import types

async def main() -> None:
    session_service = AerospikeSessionService.from_uri(
        "aerospike://localhost:3000/adk"
    )
    agent = LlmAgent(
        name="assistant",
        model="gemini-flash-latest",
        instruction="Be helpful. Keep replies under 30 words.",
    )
    runner = Runner(
        agent=agent,
        app_name="myapp",
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="myapp", user_id="user-1"
    )
    async for event in runner.run_async(
        user_id="user-1",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text="Hello")]
        ),
    ):
        if event.content:
            for part in event.content.parts or []:
                if part.text:
                    print(part.text)

    session_service.close()

asyncio.run(main())
```

Use the session service directly for state, events, and listing. Scoped keys follow ADK conventions (`app:`, `user:`, `temp:`).

```python
import asyncio

from adk_aerospike import AerospikeSessionService
from google.adk.events import Event, EventActions
from google.genai import types

async def main() -> None:
    svc = AerospikeSessionService.from_uri("aerospike://localhost:3000/adk")

    session = await svc.create_session(
        app_name="support_bot",
        user_id="alice",
        state={
            "topic": "billing",
            "app:tenant": "acme-corp",
            "user:nickname": "Allie",
            "temp:scratch": "throwaway",
        },
    )

    await svc.append_event(
        session,
        Event(
            invocation_id="i1",
            author="user",
            content=types.Content(
                role="user",
                parts=[types.Part(text="Where is my invoice?")],
            ),
            actions=EventActions(state_delta={"turn": 1}),
        ),
    )

    fetched = await svc.get_session(
        app_name="support_bot",
        user_id="alice",
        session_id=session.id,
    )
    print(fetched.state)
    # topic, turn, app:tenant, user:nickname — temp: keys are not persisted

    svc.close()

asyncio.run(main())
```

Persist text-bearing session events, then search with word overlap (no vector index).

```python
import asyncio

from adk_aerospike import AerospikeMemoryService
from google.adk.events import Event, EventActions
from google.adk.sessions import Session
from google.genai import types

async def main() -> None:
    memory = AerospikeMemoryService.from_uri(
        "aerospike://localhost:3000/adk", top_k=10
    )

    session = Session(
        id="s-1",
        app_name="support_bot",
        user_id="alice",
        events=[
            Event(
                invocation_id="i",
                author="user",
                content=types.Content(
                    role="user",
                    parts=[types.Part(text="Python uses duck typing.")],
                ),
                actions=EventActions(),
            ),
        ],
    )
    await memory.add_session_to_memory(session)

    resp = await memory.search_memory(
        app_name="support_bot",
        user_id="alice",
        query="python duck typing",
    )
    for m in resp.memories:
        print(m.content.parts[0].text)

    memory.close()

asyncio.run(main())
```

Save versioned artifacts per session; use a `user:` filename prefix for cross-session visibility.

```python
import asyncio

from adk_aerospike import AerospikeArtifactService
from google.genai import types

async def main() -> None:
    svc = AerospikeArtifactService.from_uri(
        "aerospike://localhost:3000/adk"
    )

    await svc.save_artifact(
        app_name="support_bot",
        user_id="alice",
        session_id="s-1",
        filename="report.pdf",
        artifact=types.Part(
            inline_data=types.Blob(
                mime_type="application/pdf", data=b"%PDF-1.4..."
            ),
        ),
    )

    latest = await svc.load_artifact(
        app_name="support_bot",
        user_id="alice",
        session_id="s-1",
        filename="report.pdf",
    )
    print(latest.inline_data.mime_type)

    svc.close()

asyncio.run(main())
```

```python
from adk_aerospike import (
    AerospikeArtifactService,
    AerospikeMemoryService,
    AerospikeSessionService,
)
from google.adk.agents import LlmAgent
from google.adk.runners import Runner

uri = "aerospike://localhost:3000/adk"

session_service = AerospikeSessionService.from_uri(uri)
artifact_service = AerospikeArtifactService.from_uri(uri)
memory_service = AerospikeMemoryService.from_uri(uri)

agent = LlmAgent(name="assistant", model="gemini-flash-latest")
runner = Runner(
    agent=agent,
    app_name="myapp",
    session_service=session_service,
    artifact_service=artifact_service,
    memory_service=memory_service,
)
```

Register URI schemes once (for example in `services.py` next to your agent):

```python
import adk_aerospike

adk_aerospike.register()
```

Then point the CLI at the same namespace for each storage role:

```bash
adk web \
  --session_service_uri=aerospike://localhost:3000/adk \
  --artifact_service_uri=aerospike://localhost:3000/adk \
  --memory_service_uri=aerospike://localhost:3000/adk
```

Note

`register()` wires `aerospike://` into ADK's service registry so the dev UI and CLI resolve these URLs without custom factory code.

## Configuration

### Connection URI

All three services share one URI format:

```text
aerospike://[user:pass@]host[:port][,host2[:port],…]/<namespace>[?option=value]
```

Examples:

```text
aerospike://localhost:3000/adk
aerospike://user:pass@node1:3000,node2:3000/prod?set_prefix=prod_&tls=true
```

| Query parameter | Description                                                                             |
| --------------- | --------------------------------------------------------------------------------------- |
| `set_prefix`    | Prefix for Aerospike set names (default `adk_`). Multiple apps can share one namespace. |
| `tls=true`      | Enable TLS. Pass `tls_config={...}` to `from_uri` for mTLS details.                     |
| `auth_mode`     | `INTERNAL` (default), `EXTERNAL`, `EXTERNAL_INSECURE`, or `PKI`.                        |

You can also construct services with an existing `aerospike.Client` and `Schema` for shared connection pools across services.

### State scoping

Session `state` uses key prefixes (same as [`google.adk.sessions.state.State`](https://github.com/google/adk-python)):

| Prefix         | Stored in        | Visibility                |
| -------------- | ---------------- | ------------------------- |
| `app:foo`      | `adk_app_state`  | All users of the app      |
| `user:foo`     | `adk_user_state` | This user across sessions |
| `temp:foo`     | Not persisted    | Current invocation only   |
| *(unprefixed)* | Session record   | This session only         |

`get_session` merges all scopes into one dict with prefixes restored for ADK compatibility.

## Available services

### Services

| Service                    | ADK interface         | Description                                                                                                                                                                                                         |
| -------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AerospikeSessionService`  | `BaseSessionService`  | Sessions, events, scoped state. Hot event tail on the session record; sealed chunks at 256 KiB. Most appends are one atomic `operate()`; `get_session` uses `batch_read` for session + app + user state in one RTT. |
| `AerospikeArtifactService` | `BaseArtifactService` | Versioned artifacts per `(app, user, session, filename)`. Inline payload up to 8 MiB per version. `user:` filenames use the ADK user namespace sentinel.                                                            |
| `AerospikeMemoryService`   | `BaseMemoryService`   | One memory row per text-bearing event; posting-list PK per token. `search_memory` ranks by query token overlap.                                                                                                     |

### URI registration

| Function                   | Description                                                                 |
| -------------------------- | --------------------------------------------------------------------------- |
| `adk_aerospike.register()` | Registers `aerospike://` with ADK's service registry for CLI and `adk web`. |

## Storage layout

Default set prefix `adk_` in your namespace:

| Set              | Key pattern                   | Purpose                                   |
| ---------------- | ----------------------------- | ----------------------------------------- |
| `adk_sessions`   | `app:user:session`            | Session record (state + hot event tail)   |
| `adk_sessions`   | `app:user:session:c:NNNNNNNN` | Sealed event chunks                       |
| `adk_sessions`   | `app:user:sl`                 | Session list manifest for `list_sessions` |
| `adk_app_state`  | `app`                         | App-scoped state                          |
| `adk_user_state` | `app:user`                    | User-scoped state                         |
| `adk_artifacts`  | `app:user:session:fname:ver`  | Artifact versions                         |
| `adk_memory`     | `app:user:session:event_id`   | Memory row                                |
| `adk_memory`     | `app:user:kw:token`           | Posting list for lexical search           |

See the [data model](https://github.com/aerospike-community/adk-aerospike/blob/main/docs/data-model.md) in the repository for indexes, chunking invariants, and operational notes.

## Additional resources

- [adk-aerospike on GitHub](https://github.com/aerospike-community/adk-aerospike)
- [adk-aerospike on PyPI](https://pypi.org/project/adk-aerospike/)
- [Runnable examples](https://github.com/aerospike-community/adk-aerospike/tree/main/examples)
- [Aerospike documentation](https://aerospike.com/docs/)
- [ADK sessions and memory](/sessions/)
