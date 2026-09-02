import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.integrations.slack import SlackRunner
from slack_bolt.app.async_app import AsyncApp

# Define the core agent
root_agent = Agent(
    model="gemini-flash-latest",
    name="slack_agent",
    instruction="You are a helpful team assistant running on Slack.",
)

# Wire it up to Slack over Socket Mode
runner = Runner(
    app_name="slack_agent",
    agent=root_agent,
    session_service=InMemorySessionService(),
    auto_create_session=True,
)
slack_app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])
slack_runner = SlackRunner(runner, slack_app)

asyncio.run(slack_runner.start(os.environ["SLACK_APP_TOKEN"]))