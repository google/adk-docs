# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# # --- Setup Instructions ---
# # 1. Install the ADK package:
# !pip install google-adk
# # Make sure to restart kernel if using colab/jupyter notebooks

# # 2. Set up your Gemini API Key:
# #    - Get a key from Google AI Studio: https://aistudio.google.com/app/apikey
# #    - Set it as an environment variable:
# import os
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE" # <--- REPLACE with your actual key
# # Or learn about other authentication methods (like Agent Platform):
# # https://adk.dev/agents/models/


# ADK Imports
import asyncio

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import InMemoryRunner  # Use InMemoryRunner
from google.genai import types  # For types.Content
from typing import Optional

# Define the model - Use the specific model name requested
GEMINI_2_FLASH = "gemini-2.0-flash"


# --- 1. Define the Callback Function ---
def modify_output_after_agent(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    Logs exit from an agent and checks 'add_concluding_note' in session state.
    If True, returns new Content, which ADK emits as an *additional* event after
    the agent's own output. The agent's original output is still produced.
    If False or not present, returns None, so no extra event is emitted.
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    print(f"\n[Callback] Exiting agent: {agent_name} (Inv: {invocation_id})")
    print(f"[Callback] Current State: {current_state}")

    # Example: Check state to decide whether to modify the final output
    if current_state.get("add_concluding_note", False):
        print(
            f"[Callback] State condition 'add_concluding_note=True' met: Appending a note after agent {agent_name}'s output."
        )
        # Returned Content is emitted as an extra event after the agent's own
        # output; it does not overwrite what the agent already produced.
        return types.Content(
            parts=[
                types.Part(
                    text=f"Concluding note added by after_agent_callback, after the original output."
                )
            ],
            role="model",  # Assign model role to the appended response
        )
    else:
        print(
            f"[Callback] State condition not met: Only agent {agent_name}'s original output is emitted."
        )
        # Return None - no extra event is emitted after the agent's output.
        return None


# --- 2. Setup Agent with Callback ---
llm_agent_with_after_cb = LlmAgent(
    name="MySimpleAgentWithAfter",
    model=GEMINI_2_FLASH,
    instruction="You are a simple agent. Just say 'Processing complete!'",
    description="An LLM agent demonstrating after_agent_callback appending an extra event",
    after_agent_callback=modify_output_after_agent,  # Assign the callback here
)


# --- 3. Setup Runner and Sessions using InMemoryRunner ---
async def main():
    app_name = "after_agent_demo"
    user_id = "test_user_after"
    session_id_normal = "session_run_normally"
    session_id_modify = "session_modify_output"

    # Use InMemoryRunner - it includes InMemorySessionService
    runner = InMemoryRunner(agent=llm_agent_with_after_cb, app_name=app_name)
    # Get the bundled session service to create sessions
    session_service = runner.session_service

    # Create session 1: Agent output will be used as is (default empty state)
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_normal,
        # No initial state means 'add_concluding_note' will be False in the callback check
    )
    # print(f"Session '{session_id_normal}' created with default state.")

    # Create session 2: The callback appends an extra event after the agent output
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_modify,
        state={"add_concluding_note": True},  # Set the state flag here
    )
    # print(f"Session '{session_id_modify}' created with state={{'add_concluding_note': True}}.")

    # --- Scenario 1: Run where the callback adds nothing ---
    print(
        "\n"
        + "=" * 20
        + f" SCENARIO 1: Running Agent on Session '{session_id_normal}' (Only Original Output) "
        + "=" * 20
    )
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_normal,
        new_message=types.Content(
            role="user", parts=[types.Part(text="Process this please.")]
        ),
    ):
        # Print final output, from the LLM or from the callback's extra event
        if event.is_final_response() and event.content and event.content.parts:
            print(
                f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}"
            )
        elif event.error_code:
            print(f"Error Event: {event.error_code} - {event.error_message}")

    # --- Scenario 2: Run where the callback appends an extra event ---
    print(
        "\n"
        + "=" * 20
        + f" SCENARIO 2: Running Agent on Session '{session_id_modify}' (Original Output + Appended Note) "
        + "=" * 20
    )
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_modify,
        new_message=types.Content(
            role="user", parts=[types.Part(text="Process this and add note.")]
        ),
    ):
        # Print final output, from the LLM or from the callback's extra event
        if event.is_final_response() and event.content and event.content.parts:
            print(
                f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}"
            )
        elif event.error_code:
            print(f"Error Event: {event.error_code} - {event.error_message}")


# --- 4. Execute ---
# In a Jupyter Notebook or similar environment you can `await main()` directly.
# As a script:
if __name__ == "__main__":
    # Make sure GOOGLE_API_KEY environment variable is set if not using Agent Platform auth
    # Or ensure Application Default Credentials (ADC) are configured for Agent Platform
    asyncio.run(main())
