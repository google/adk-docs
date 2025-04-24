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

import asyncio
import os
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
from google.genai import types
# Use InMemoryRunner - no need for explicit SessionService
from google.adk.runners import InMemoryRunner
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator, Optional
from google.adk.events import Event, EventActions

# --- Constants ---
APP_NAME = "doc_writing_app"
USER_ID = "dev_user_01"
SESSION_ID = "loop_session_01"
GEMINI_MODEL = "gemini-2.0-flash"

# --- State Keys ---
# Using constants makes prompts and logic less error-prone
STATE_INITIAL_TOPIC = "initial_topic"
STATE_CURRENT_DOC = "current_document"
STATE_CRITICISM = "criticism"
STOP_WORD = "completed" # The exact word the CriticAgent should output to stop


# --8<-- [start:init]
# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup

# --- Agent Definitions ---

# Writer Agent
writer_agent = LlmAgent(
    name="WriterAgent",
    model=GEMINI_MODEL,
    # Improved Instruction: Use state key injection `{...}` and clear logic
    instruction=f"""You are a Creative Writing Assistant. Your goal is to iteratively write and refine a short document based on feedback.

IF the state key '{STATE_CURRENT_DOC}' does NOT exist or is empty:
Write a very short (1-2 sentence) story or document based on the topic provided in the state key '{STATE_INITIAL_TOPIC}'.

ELSE IF the state key '{STATE_CRITICISM}' exists and contains feedback (and is not '{STOP_WORD}'):
Refine the document currently in the state key '{STATE_CURRENT_DOC}' by thoughtfully applying the suggestions found in '{STATE_CRITICISM}'. Aim to improve the document based on the feedback.

Output *only* the new or refined document text. Do not add any introductory or concluding remarks.
""",
    description="Writes the initial document draft or refines it based on critique.",
    output_key=STATE_CURRENT_DOC # Saves output to state['current_document']
)

# Critic Agent
critic_agent = LlmAgent(
    name="CriticAgent",
    model=GEMINI_MODEL,
    # Improved Instruction: Specific output requirements for critique and stopping
    instruction=f"""You are a Constructive Critic AI. Your task is to review a document and provide feedback, or indicate completion.

Review the document provided in the session state key '{STATE_CURRENT_DOC}'.

IF the document can be improved:
Provide 1-2 brief, actionable suggestions for improvement (e.g., "Expand on the character's motivation.", "Add more sensory details."). Output *only* the critique text.

ELSE IF the document requires no further changes or is satisfactory:
Respond *exactly* with the word '{STOP_WORD}' and nothing else. This signals that the writing process is complete.

Do not add any explanations before or after your critique or the stop word.
""",
    description="Reviews the current document draft and provides critique or signals completion.",
    output_key=STATE_CRITICISM # Saves critique to state['criticism']
)

# Custom Agent to Check the Stop Condition
class CheckCondition(BaseAgent):
    """Checks the state for the critic's stop word and escalates if found."""
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Retrieve the latest criticism from the state, default to "pending" if not set
        status = ctx.session.state.get(STATE_CRITICISM, "pending")
        # Normalize the status (lowercase, remove whitespace) for reliable comparison
        is_done = (status.lower().strip() == STOP_WORD)

        # Add print statement to show the condition check
        print(f"  [CheckCondition] Checking state '{STATE_CRITICISM}': Value='{status}', Stop condition met? {is_done}")

        # Escalate (stop the loop) if the condition is met
        yield Event(author=self.name, actions=EventActions(escalate=is_done))

# Create the LoopAgent
# It runs the sub_agents sequentially in each iteration until CheckCondition escalates or max_iterations is hit.
loop_agent = LoopAgent(
    name="IterativeWritingLoop",
    sub_agents=[
        writer_agent,    # Step 1: Write or refine
        critic_agent,    # Step 2: Critique or signal stop
        CheckCondition(name="CompletionChecker") # Step 3: Check if stopped
    ],
    max_iterations=5 # Limit loops to prevent infinite runs
)

# Assign the main loop agent as the root agent for the runner
root_agent = loop_agent

# --8<-- [end:init]

# Use InMemoryRunner
runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
print(f"InMemoryRunner created for agent '{root_agent.name}'.")


# # Define an async interaction function with enhanced printing
async def call_loop_agent_async(initial_topic: str, user_id: str, session_id: str):
    """Runs the loop agent and prints intermediate outputs."""
    print(f"\n--- Starting Iterative Writing Process for topic: '{initial_topic}' ---")

    # Access the session service bundled within InMemoryRunner
    session_service = runner.session_service
    initial_state = {STATE_INITIAL_TOPIC: initial_topic}

    # Try to get the session first. If it doesn't exist, create it with the initial state.
    session = session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    if not session:
        print(f"  Session '{session_id}' not found, creating with initial state...")
        session = session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state=initial_state
        )
        print(f"  Session '{session_id}' created.")
    else:
        print(f"  Session '{session_id}' exists. Ensuring initial topic is set.")
        try:
             stored_session = session_service.sessions[APP_NAME][user_id][session_id]
             stored_session.state[STATE_INITIAL_TOPIC] = initial_topic
        except KeyError:
             print(f"  Warning: Could not directly update stored session state for {session_id}. Relying on agent logic.")

    initial_message = types.Content(role='user', parts=[types.Part(text="Start writing process.")])
    iteration_count = 0
    loop_terminated_normally = False

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=initial_message,
        ):
            author_name = event.author or "System"
            is_final = event.is_final_response()
            print(f"  [Event] From: {author_name}, Final: {is_final}") # Basic event logging

            # Check if it's a final response from one of the main agents
            if is_final and event.content and event.content.parts:
                output_text = event.content.parts[0].text.strip()

                if author_name == writer_agent.name:
                    iteration_count += 1
                    print(f"\n[Iteration {iteration_count}] WriterAgent Output ({STATE_CURRENT_DOC}):")
                    print(output_text)

                elif author_name == critic_agent.name:
                    print(f"[Iteration {iteration_count}] CriticAgent Output ({STATE_CRITICISM}):")
                    print(output_text)
                    print(f"  (Saving to state key '{STATE_CRITICISM}')")

            # Check if the loop was terminated by the CheckCondition agent's escalation
            if event.actions and event.actions.escalate and author_name == "CompletionChecker":
                 print(f"\n--- Loop terminated by CompletionChecker (Condition Met: '{STOP_WORD}') ---")
                 loop_terminated_normally = True
                 # Runner handles escalation, loop continues until exhausted or next natural break

            # --- Corrected Error Check ---
            # Check if the event contains an error message instead of using is_error()
            elif event.error_message:
                 print(f"  -> Error from {author_name}: {event.error_message}")

    except Exception as e:
        print(f"\n❌ An error occurred during agent execution: {e}")

    if not loop_terminated_normally:
         print(f"\n--- Loop finished (Max iterations {loop_agent.max_iterations} reached or other termination) ---")

    # Optional: Inspect final state
    final_state = runner.session_service.get_session(app_name=APP_NAME,user_id=user_id, session_id=session_id)
    print("\n--- Final Session State ---")
    print(final_state if final_state else "State not found or empty.")
    print("-" * 30)

# # Define main async function to run the interaction
# async def main():
#     """Main function to execute the agent interaction."""
topic = "a journey to a newly discovered planet"
# topic = "the first day of training for a clumsy dragon rider"
# topic = "the challenges of communicating with a plant-based alien species"
# topic = "life inside a giant library where books are portals"
await call_loop_agent_async(topic, user_id=USER_ID, session_id=SESSION_ID)
# asyncio.run(call_loop_agent_async(topic, user_id=USER_ID, session_id=SESSION_ID))
