from google.adk.runners import InMemoryRunner
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import asyncio

# Import the plugin.
from .count_plugin import CountInvocationPlugin

async def hello_world(tool_context: ToolContext, query: str):
    print(f'Hello world: query is [{query}]')

    root_agent = Agent(
        model='gemini-flash-latest',
        name='hello_world',
        description='Prints hello world with user query.',
        instruction="""Use hello_world tool to print hello world and user query.
        """,
        tools=[hello_world],
    )

async def main():
    """Main entry point for the agent."""
    prompt = 'hello world'
    runner = InMemoryRunner(
        agent=root_agent,
        app_name='test_app_with_plugin',

        # Add your plugin here. You can add multiple plugins.
        plugins=[CountInvocationPlugin()],
    )

    # The rest is the same as starting a regular ADK runner.
    session = await runner.session_service.create_session(
        user_id='user',
        app_name='test_app_with_plugin',
    )

    async for event in runner.run_async(
        user_id='user',
        session_id=session.id,
        new_message=types.Content(
            role='user', parts=[types.Part.from_text(text=prompt)]
        )
    ):
        print(f'** Got event from {event.author}')

if __name__ == "__main__":
    asyncio.run(main())