from google.adk import Agent
from google.adk.environment import LocalEnvironment
from google.adk.tools.environment import EnvironmentToolset

root_agent = Agent(
    model="gemini-flash-latest",
    name="my_agent",
    instruction="""
    You are a helpful AI assistant that can use the local environment
    to execute commands and file I/O. Follow the rules of the
    environment and the user's instructions.
    """,
    tools=[
        EnvironmentToolset(
            environment=LocalEnvironment(),
        ),
    ],
)