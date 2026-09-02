import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from respan import Respan
from respan_instrumentation_google_adk import GoogleADKInstrumentor

respan = Respan(
    instrumentations=[GoogleADKInstrumentor()],
    environment="development",
)

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="You are a concise assistant.",
)


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="respan-adk-demo",
        user_id="user_1",
    )
    runner = Runner(
        agent=agent,
        app_name="respan-adk-demo",
        session_service=session_service,
    )
    message = types.Content(
        role="user",
        parts=[types.Part(text="Say hello in one sentence.")],
    )

    async for event in runner.run_async(
        user_id="user_1",
        session_id=session.id,
        new_message=message,
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)

    respan.flush()
    respan.shutdown()


asyncio.run(main())