from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import Runner
from typing import Optional
from google.genai import types 
from google.adk.sessions import InMemorySessionService

GEMINI_2_FLASH="gemini-2.0-flash"

# --- Define the Callback Function ---
def simple_before_agent_logger(callback_context: CallbackContext) -> Optional[types.Content]:
    """Logs entry into an agent and checks a condition."""
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    print(f"[Callback] Entering agent: {agent_name} (Invocation: {invocation_id})")

    # Example: Check a condition in state
    if callback_context.state.get("skip_agent", False):
        print(f"[Callback] Condition met: Skipping agent {agent_name}.")
        # Return Content to skip the agent's run
        return types.Content(parts=[types.Part(text=f"Agent {agent_name} was skipped by callback.")])
    else:
        print(f"[Callback] Condition not met: Proceeding with agent {agent_name}.")
        # Return None to allow the agent's run to execute
        return None

# Create LlmAgent and Assign Callback
my_llm_agent = LlmAgent(
        name="SimpleLlmAgent",
        model=GEMINI_2_FLASH,
        instruction="You are a simple agent. Just say 'Hello!'",
        description="An LLM agent demonstrating before_agent_callback",
        before_agent_callback=simple_before_agent_logger
    )

APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)


# Agent Interaction
def call_agent(query):
  content = types.Content(role='user', parts=[types.Part(text=query)])
  events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

  for event in events:
      if event.is_final_response():
          final_response = event.content.parts[0].text
          print("Agent Response: ", final_response)

call_agent("callback example")