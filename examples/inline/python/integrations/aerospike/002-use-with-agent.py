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