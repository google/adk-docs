import asyncio

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from stackone_adk import StackOnePlugin


async def main():
    plugin = StackOnePlugin(
        mode="search_and_execute",
        account_ids=["YOUR_ACCOUNT_ID"],
        search={"method": "auto", "top_k": 10},
    )

    agent = Agent(
        model="gemini-flash-latest",
        name="stackone_agent",
        description="Connects to multiple SaaS providers through StackOne.",
        instruction=(
            "You are an assistant powered by StackOne. To answer the "
            "user's request, first call tool_search with a short query "
            "to find the right action, then call tool_execute with the "
            "chosen tool name and parameters that match the schema "
            "returned by tool_search."
        ),
        tools=plugin.get_tools(),
    )

    app = App(
        name="stackone_app",
        root_agent=agent,
        plugins=[plugin],
    )

    async with InMemoryRunner(app=app) as runner:
        events = await runner.run_debug(
            "List the first 3 workers.",
            quiet=True,
        )
        for event in reversed(events):
            if event.content and event.content.parts:
                text_parts = [p.text for p in event.content.parts if p.text]
                if text_parts:
                    print("".join(text_parts))
                    break


asyncio.run(main())