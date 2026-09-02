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