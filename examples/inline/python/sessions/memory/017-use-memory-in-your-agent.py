from google.adk.agents import Agent
from google.adk.tools import preload_memory

async def auto_save_session_to_memory_callback(callback_context):
    await callback_context.add_session_to_memory()

agent = Agent(
    model=MODEL,
    name="Generic_QA_Agent",
    instruction="Answer the user's questions",
    tools=[preload_memory],
    after_agent_callback=auto_save_session_to_memory_callback,
)