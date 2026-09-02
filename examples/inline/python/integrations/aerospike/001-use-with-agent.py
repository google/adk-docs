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