import asyncio

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from stackone_adk import StackOnePlugin


async def main():
    plugin = StackOnePlugin()
    # Or scope to a specific account:
    # plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")

    tools = plugin.get_tools()
    print(f"Discovered {len(tools)} tools")

    agent = Agent(
        model="gemini-flash-latest",
        name="scheduling_agent",
        description="Manages scheduling, HR, and CRM through StackOne.",
        instruction=(
            "You are a helpful assistant powered by StackOne. "
            "You help users manage their scheduling, HR, and CRM tasks "
            "by using the available tools.\n\n"
            "Always be helpful and provide clear, organized responses."
        ),
        tools=tools,
    )

    async with InMemoryRunner(
        app_name="scheduling_app", agent=agent
    ) as runner:
        events = await runner.run_debug(
            "Get my most recent scheduled meeting from Calendly.",
            quiet=True,
        )
        # Extract the agent's final text response
        for event in reversed(events):
            if event.content and event.content.parts:
                text_parts = [p.text for p in event.content.parts if p.text]
                if text_parts:
                    print("".join(text_parts))
                    break


asyncio.run(main())