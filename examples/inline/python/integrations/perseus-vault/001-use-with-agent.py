from adk_perseus_vault_memory import PerseusVaultMemoryService
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import load_memory

agent = Agent(
    name="memory_assistant",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant with long-term memory.",
    tools=[load_memory],
)

runner = Runner(
    agent=agent,
    app_name="perseus_vault_app",
    session_service=InMemorySessionService(),
    memory_service=PerseusVaultMemoryService(db_path="~/.adk/vault.db"),
)