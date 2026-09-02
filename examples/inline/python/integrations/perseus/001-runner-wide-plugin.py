from adk_perseus_context import PerseusContextPlugin
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Help the user.",
)

app = App(
    name="perseus_app",
    root_agent=agent,
    plugins=[PerseusContextPlugin("context.perseus")],
)

runner = Runner(
    app=app,
    session_service=InMemorySessionService(),
)