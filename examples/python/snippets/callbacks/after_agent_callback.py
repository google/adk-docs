from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import Runner
from typing import Optional
from google.genai import types 
from google.adk.sessions import InMemorySessionService

GEMINI_2_FLASH="gemini-2.0-flash"

# --- Define the Callback Function ---
def simple_after_agent_logger(callback_context: CallbackContext) -> Optional[types.Content]:
    """Logs exit from an agent and optionally appends a message."""
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    print(f"[Callback] Exiting agent: {agent_name} (Invocation: {invocation_id})")

    # Example: Check state potentially modified during the agent's run
    final_status = callback_context.state.get("agent_run_status", "Completed Normally")
    print(f"[Callback] Agent run status from state: {final_status}")

    # Example: Optionally return Content to append a message
    if callback_context.state.get("add_concluding_note", False):
        print(f"[Callback] Adding concluding note for agent {agent_name}.")
        # Return Content to append after the agent's own output
        return types.Content(parts=[types.Part(text=f"Concluding note added by after_agent_callback.")])
    else:
        print(f"[Callback] No concluding note added for agent {agent_name}.")
        # Return None - no additional message appended
        return None

my_llm_agent = LlmAgent(
        name="SimpleLlmAgentWithAfter",
        model=GEMINI_2_FLASH,
        instruction="You are a simple agent. Just say 'Processing complete!'",
        description="An LLM agent demonstrating after_agent_callback",
        after_agent_callback=simple_after_agent_logger # Assign the function here
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