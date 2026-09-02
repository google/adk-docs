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