from adk_perseus_vault_memory.perseus_context import perseus_context_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# The pre-built agent ships without a model; set one before use.
perseus_context_agent.model = "gemini-flash-latest"

runner = Runner(
    agent=perseus_context_agent,
    app_name="perseus_app",
    session_service=InMemorySessionService(),
    memory_service=PerseusVaultMemoryService(db_path="~/.adk/vault.db"),
)