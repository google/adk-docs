---
catalog_title: Loom
catalog_description: Store user memories and recall them across agent sessions
catalog_icon: /integrations/assets/loom.svg
catalog_tags: ["data"]
---

# Loom memory service for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Loom](https://github.com/ClickHouse/loom) provides a native ADK
`BaseMemoryService` backed by your Loom deployment. Connect it to a `Runner`
to use ADK's memory tools with stored user memories and application documents.

## Use cases

- **User preferences**: Store preferences through the memory service and recall
  them in later sessions.
- **Application knowledge**: Include documents from the application's Loom
  namespace in memory search results.

## Prerequisites

- Python 3.11 or later.
- A [Loom deployment](https://github.com/ClickHouse/loom/blob/v1.3.0-rc.1/docs/getting-started/quickstart.md)
  with memory search configured.
- A Loom token with read and write access to a dedicated application namespace.
- A [Gemini API key](https://aistudio.google.com/app/api-keys) for the agent model.

## Installation

This example uses the published Loom SDK prerelease and ADK 2.14.0:

```bash
pip install --upgrade 'clickhouse-loom[google-adk]==1.3.0rc1' 'google-adk==2.14.0'
```

## Configuration

Set the following environment variables before running the example:

| Variable | Value |
| --- | --- |
| `LOOM_BASE_URL` | Your Loom deployment URL |
| `LOOM_ORG` | Your Loom organization |
| `LOOM_NAMESPACE` | A namespace dedicated to this ADK application |
| `LOOM_API_KEY` | The token for that namespace |
| `GOOGLE_API_KEY` | Your Gemini API key |
| `GOOGLE_GENAI_USE_VERTEXAI` | `FALSE` to use the Gemini API |

Model inference and your Loom deployment's configured providers can incur
charges.

## Use with agent

Save this as `loom_memory_agent.py` and run `python loom_memory_agent.py`.
The application stores one explicit user preference through the native memory
service. The `preload_memory` tool searches for relevant context before the
agent's model call.

```python
import asyncio
import os

from google.adk.agents import Agent
from google.adk.memory.memory_entry import MemoryEntry
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import preload_memory
from google.genai import types
from loom import Agent as LoomAgent
from loom.integrations.google_adk import LoomMemoryService

APP_NAME = "loom_memory_example"
USER_ID = "alice"


def build_runner(loom_agent, sessions, model="gemini-flash-latest"):
    memory = LoomMemoryService(loom_agent, app_name=APP_NAME)
    root_agent = Agent(
        name="travel_assistant",
        model=model,
        instruction="Use the user's remembered preferences when answering.",
        tools=[preload_memory],
    )
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=sessions,
        memory_service=memory,
    )
    return runner, memory


async def main():
    async with LoomAgent(
        org=os.environ["LOOM_ORG"],
        namespace=os.environ["LOOM_NAMESPACE"],
        base_url=os.environ["LOOM_BASE_URL"],
        api_key=os.environ["LOOM_API_KEY"],
    ) as loom_agent:
        sessions = InMemorySessionService()
        runner, memory = build_runner(loom_agent, sessions)
        await memory.add_memory(
            app_name=APP_NAME,
            user_id=USER_ID,
            memories=[
                MemoryEntry(
                    content=types.Content(
                        role="user",
                        parts=[types.Part(text="I prefer an aisle seat when flying.")],
                    )
                )
            ],
        )
        session = await sessions.create_session(app_name=APP_NAME, user_id=USER_ID)
        message = types.Content(
            role="user", parts=[types.Part(text="Which airplane seat do I prefer?")]
        )
        async for event in runner.run_async(
            user_id=USER_ID, session_id=session.id, new_message=message
        ):
            if event.is_final_response() and event.content:
                print("".join(part.text or "" for part in event.content.parts or []))


if __name__ == "__main__":
    asyncio.run(main())
```

Use a separate Loom namespace and service for each ADK application. ADK user
IDs scope memory operations within that namespace; Loom token permissions
control access to it. Namespace documents are shared application knowledge.
The example's chat sessions stay in process, while memories are stored in Loom.

The example writes an explicit preference. To extract memories from a completed
conversation, call `add_session_to_memory` with its ADK session. This does not
happen automatically when attaching the service to a runner.

## Memory operations

| ADK interface | Loom behavior |
| --- | --- |
| `add_memory` | Store explicit memory entries for an ADK user |
| `search_memory` | Search that user's memories, then fill remaining result slots from namespace documents |
| `add_session_to_memory` | Submit a session's active events for memory extraction |
| `add_events_to_memory` | Submit an event delta with its ADK session ID |
| `preload_memory` | Search before each model call and add matches to its context |

## Additional resources

- [Loom adapter guide](https://github.com/ClickHouse/loom/blob/v1.3.0-rc.1/docs/features/integrations/frameworks.md#google-adk)
- [Published SDK](https://pypi.org/project/clickhouse-loom/1.3.0rc1/)
- [Memory service source](https://github.com/ClickHouse/loom/blob/v1.3.0-rc.1/sdk/python/loom/integrations/google_adk.py)
- [ADK memory documentation](/sessions/memory/)
