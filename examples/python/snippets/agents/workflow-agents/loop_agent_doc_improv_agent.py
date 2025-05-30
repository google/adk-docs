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

# --8<-- [start:init]
# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup

import asyncio
import os
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent, SequentialAgent
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.tool_context import ToolContext
from typing import AsyncGenerator, Optional
from google.adk.events import Event, EventActions

# --- Constants ---
APP_NAME = "doc_writing_app_v3" # New App Name
USER_ID = "dev_user_01"
SESSION_ID_BASE = "loop_exit_tool_session" # New Base Session ID
GEMINI_MODEL = "gemini-2.0-flash"
STATE_INITIAL_TOPIC = "initial_topic"

# --- State Keys ---
STATE_CURRENT_DOC = "current_document"
STATE_CRITICISM = "criticism"
# Define the exact phrase the Critic should use to signal completion
COMPLETION_PHRASE = "No major issues found."

# --- Tool Definition ---
def exit_loop(tool_context: ToolContext):
  """Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end."""
  print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
  tool_context.actions.escalate = True
  # Return empty dict as tools should typically return JSON-serializable output
  return {}

# --- Agent Definitions ---

# STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
initial_writer_agent = LlmAgent(
    name="InitialWriterAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    # MODIFIED Instruction: Ask for a slightly more developed start
    instruction=f"""You are a Creative Writing Assistant tasked with starting a story.
    Write the *first draft* of a short story (aim for 2-4 sentences).
    Base the content *only* on the topic provided below. Try to introduce a specific element (like a character, a setting detail, or a starting action) to make it engaging.
    Topic: {{initial_topic}}

    Output *only* the story/document text. Do not add introductions or explanations.
""",
    description="Writes the initial document draft based on the topic, aiming for some initial substance.",
    output_key=STATE_CURRENT_DOC
)

# STEP 2a: Critic Agent (Inside the Refinement Loop)
critic_agent_in_loop = LlmAgent(
    name="CriticAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    # MODIFIED Instruction: More nuanced completion criteria, look for clear improvement paths.
    instruction=f"""You are a Constructive Critic AI reviewing a short document draft (typically 2-6 sentences). Your goal is balanced feedback.

    **Document to Review:**
    ```
    {{current_document}}
    ```

    **Task:**
    Review the document for clarity, engagement, and basic coherence according to the initial topic (if known).

    IF you identify 1-2 *clear and actionable* ways the document could be improved to better capture the topic or enhance reader engagement (e.g., "Needs a stronger opening sentence", "Clarify the character's goal"):
    Provide these specific suggestions concisely. Output *only* the critique text.

    ELSE IF the document is coherent, addresses the topic adequately for its length, and has no glaring errors or obvious omissions:
    Respond *exactly* with the phrase "{COMPLETION_PHRASE}" and nothing else. It doesn't need to be perfect, just functionally complete for this stage. Avoid suggesting purely subjective stylistic preferences if the core is sound.

    Do not add explanations. Output only the critique OR the exact completion phrase.
""",
    description="Reviews the current draft, providing critique if clear improvements are needed, otherwise signals completion.",
    output_key=STATE_CRITICISM
)


# STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
refiner_agent_in_loop = LlmAgent(
    name="RefinerAgent",
    model=GEMINI_MODEL,
    # Relies solely on state via placeholders
    include_contents='none',
    instruction=f"""You are a Creative Writing Assistant refining a document based on feedback OR exiting the process.
    **Current Document:**
    ```
    {{current_document}}
    ```
    **Critique/Suggestions:**
    {{criticism}}

    **Task:**
    Analyze the 'Critique/Suggestions'.
    IF the critique is *exactly* "{COMPLETION_PHRASE}":
    You MUST call the 'exit_loop' function. Do not output any text.
    ELSE (the critique contains actionable feedback):
    Carefully apply the suggestions to improve the 'Current Document'. Output *only* the refined document text.

    Do not add explanations. Either output the refined document OR call the exit_loop function.
""",
    description="Refines the document based on critique, or calls exit_loop if critique indicates completion.",
    tools=[exit_loop], # Provide the exit_loop tool
    output_key=STATE_CURRENT_DOC # Overwrites state['current_document'] with the refined version
)


# STEP 2: Refinement Loop Agent
refinement_loop = LoopAgent(
    name="RefinementLoop",
    # Agent order is crucial: Critique first, then Refine/Exit
    sub_agents=[
        critic_agent_in_loop,
        refiner_agent_in_loop,
    ],
    max_iterations=5 # Limit loops
)

# STEP 3: Overall Sequential Pipeline
# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = SequentialAgent(
    name="IterativeWritingPipeline",
    sub_agents=[
        initial_writer_agent, # Run first to create initial doc
        refinement_loop       # Then run the critique/refine loop
    ],
    description="Writes an initial document and then iteratively refines it with critique using an exit tool."
)
# --8<-- [end:init]


# --- Running the Agent on Notebooks/Scripts ---
# runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
# print(f"InMemoryRunner created for agent '{root_agent.name}'.")


# # Interaction function (Modified to show agent names and flow)
# async def call_pipeline_async(initial_topic: str, user_id: str, session_id: str):
#     print(f"\n--- Starting Iterative Writing Pipeline (Exit Tool) for topic: '{initial_topic}' ---")
#     session_service = runner.session_service
#     initial_state = {STATE_INITIAL_TOPIC: initial_topic}
#     # Explicitly create/check session BEFORE run_async
#     session = session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
#     if not session:
#         print(f"  Session '{session_id}' not found, creating with initial state...")
#         session = session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id, state=initial_state)
#         print(f"  Session '{session_id}' created.")
#     else:
#         print(f"  Session '{session_id}' exists. Resetting state for new run.")
#         try:
#             # Clear iterative state if reusing session ID
#             stored_session = session_service.sessions[APP_NAME][user_id][session_id]
#             stored_session.state = {STATE_INITIAL_TOPIC: initial_topic} # Reset state
#         except KeyError: pass # Should not happen if get_session succeeded

#     initial_message = types.Content(role='user', parts=[types.Part(text="Start the writing pipeline.")])
#     loop_iteration = 0
#     pipeline_finished_via_exit = False
#     last_known_doc = "No document generated." # Store the last document output

#     try:
#         async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=initial_message):
#             author_name = event.author or "System"
#             is_final = event.is_final_response()
#             print(f"  [Event] From: {author_name}, Final: {is_final}")

#             # Display output from each main agent when it finishes
#             if is_final and event.content and event.content.parts:
#                 output_text = event.content.parts[0].text.strip()

#                 if author_name == initial_writer_agent.name:
#                     print(f"\n[Initial Draft] By {author_name} ({STATE_CURRENT_DOC}):")
#                     print(output_text)
#                     last_known_doc = output_text
#                 elif author_name == critic_agent_in_loop.name:
#                     loop_iteration += 1
#                     print(f"\n[Loop Iteration {loop_iteration}] Critique by {author_name} ({STATE_CRITICISM}):")
#                     print(output_text)
#                     print(f"  (Saving to state key '{STATE_CRITICISM}')")
#                 elif author_name == refiner_agent_in_loop.name:
#                     # Only print if it actually refined (didn't call exit_loop)
#                     if not event.actions.escalate: # Check if exit wasn't triggered in *this* event's actions
#                         print(f"[Loop Iteration {loop_iteration}] Refinement by {author_name} ({STATE_CURRENT_DOC}):")
#                         print(output_text)
#                         last_known_doc = output_text
#                         print(f"  (Overwriting state key '{STATE_CURRENT_DOC}')")

#             # Check if the loop was terminated by the exit_loop tool's escalation
#             # Note: The escalation action might be attached to the *tool response* event,
#             # or the *subsequent model response* if summarization happens.
#             # We detect loop termination by seeing if the RefinerAgent calls the tool
#             # (indicated by the tool's print statement) or if max iterations hit.
#             if event.actions and event.actions.escalate:
#                  # We don't know the author for sure here if it's the internal escalation propagation
#                  print(f"\n--- Refinement Loop terminated (Escalation detected) ---")
#                  pipeline_finished_via_exit = True
#                  # Exit the event processing loop once escalation is detected
#                  # as the LoopAgent should stop yielding further internal events.
#                  break

#             elif event.error_message:
#                  print(f"  -> Error from {author_name}: {event.error_message}")
#                  break # Stop on error

#     except Exception as e: print(f"\n❌ An error occurred during agent execution: {e}")

#     # Determine final status based on whether exit_loop was (presumably) called
#     if pipeline_finished_via_exit:
#         print(f"\n--- Pipeline Finished (Terminated by exit_loop) ---")
#     else:
#         print(f"\n--- Pipeline Finished (Max iterations {refinement_loop.max_iterations} reached or error) ---")

#     print(f"Final Document Output:\n{last_known_doc}")

#     # Final state retrieval
#     final_session_object = runner.session_service.get_session(app_name=APP_NAME,user_id=user_id, session_id=session_id)
#     print("\n--- Final Session State ---")
#     if final_session_object: print(final_session_object.state)
#     else: print("State not found (Final session object could not be retrieved).")
#     print("-" * 30)


# topic = "a robot developing unexpected emotions"
# # topic = "the challenges of communicating with a plant-based alien species"


# session_id = f"{SESSION_ID_BASE}_{hash(topic) % 1000}" # Unique session ID

# # In Colab/Jupyter:
# await call_pipeline_async(topic, user_id=USER_ID, session_id=session_id)

# # In a standalone Python script or if await is not supported/failing:
# # asyncio.run(call_pipeline_async(topic, user_id=USER_ID, session_id=session_id))
