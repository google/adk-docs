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

from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
# Import SequentialAgent to orchestrate the parallel and merge steps
from google.adk.agents.sequential_agent import SequentialAgent
# Use InMemoryRunner for local testing/prototyping
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

# --- Configuration ---
APP_NAME = "parallel_research_app"
USER_ID = "research_user_01"
SESSION_ID = "parallel_research_session_with_merge"
GEMINI_MODEL = "gemini-2.0-flash"


# --8<-- [start:init]
# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup
# --- 1. Define Researcher Sub-Agents (to run in parallel) ---

# Researcher 1: Renewable Energy
researcher_agent_1 = LlmAgent(
    name="RenewableEnergyResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI Research Assistant specializing in energy.
Research the latest advancements in 'renewable energy sources'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output *only* the summary.
""",
    description="Researches renewable energy sources.",
    tools=[google_search],
    # Store result in state for the merger agent
    output_key="renewable_energy_result"
)

# Researcher 2: Electric Vehicles
researcher_agent_2 = LlmAgent(
    name="EVResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI Research Assistant specializing in transportation.
Research the latest developments in 'electric vehicle technology'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output *only* the summary.
""",
    description="Researches electric vehicle technology.",
    tools=[google_search],
    # Store result in state for the merger agent
    output_key="ev_technology_result"
)

# Researcher 3: Carbon Capture
researcher_agent_3 = LlmAgent(
    name="CarbonCaptureResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI Research Assistant specializing in climate solutions.
Research the current state of 'carbon capture methods'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output *only* the summary.
""",
    description="Researches carbon capture methods.",
    tools=[google_search],
    # Store result in state for the merger agent
    output_key="carbon_capture_result"
)

# --- 2. Create the ParallelAgent (Runs researchers concurrently) ---
# This agent orchestrates the concurrent execution of the researchers.
# It finishes once all researchers have completed and stored their results in state.
parallel_research_agent = ParallelAgent(
    name="ParallelWebResearchAgent",
    sub_agents=[researcher_agent_1, researcher_agent_2, researcher_agent_3],
    description="Runs multiple research agents in parallel to gather information."
)

# --- 3. Define the Merger Agent (Runs *after* the parallel agents) ---
# This agent takes the results stored in the session state by the parallel agents
# and synthesizes them into a single, structured response with attributions.
merger_agent = LlmAgent(
    name="SynthesisAgent",
    model=GEMINI_MODEL,  # Or potentially a more powerful model if needed for synthesis
    instruction="""You are an AI Assistant responsible for combining research findings into a structured report.

Your primary task is to synthesize the following research summaries, clearly attributing findings to their source areas. Structure your response using headings for each topic. Ensure the report is coherent and integrates the key points smoothly.

**Crucially: Your entire response MUST be grounded *exclusively* on the information provided in the 'Input Summaries' below. Do NOT add any external knowledge, facts, or details not present in these specific summaries.**

**Input Summaries:**

*   **Renewable Energy:**
    {renewable_energy_result}

*   **Electric Vehicles:**
    {ev_technology_result}

*   **Carbon Capture:**
    {carbon_capture_result}

**Output Format:**

## Summary of Recent Sustainable Technology Advancements

### Renewable Energy Findings
(Based on RenewableEnergyResearcher's findings)
[Synthesize and elaborate *only* on the renewable energy input summary provided above.]

### Electric Vehicle Findings
(Based on EVResearcher's findings)
[Synthesize and elaborate *only* on the EV input summary provided above.]

### Carbon Capture Findings
(Based on CarbonCaptureResearcher's findings)
[Synthesize and elaborate *only* on the carbon capture input summary provided above.]

### Overall Conclusion
[Provide a brief (1-2 sentence) concluding statement that connects *only* the findings presented above.]

Output *only* the structured report following this format. Do not include introductory or concluding phrases outside this structure, and strictly adhere to using only the provided input summary content.
""",
    description="Combines research findings from parallel agents into a structured, cited report, strictly grounded on provided inputs.",
    # No tools needed for merging
    # No output_key needed here, as its direct response is the final output of the sequence
)


# --- 4. Create the SequentialAgent (Orchestrates the overall flow) ---
# This is the main agent that will be run. It first executes the ParallelAgent
# to populate the state, and then executes the MergerAgent to produce the final output.
sequential_pipeline_agent = SequentialAgent(
    name="ResearchAndSynthesisPipeline",
    # Run parallel research first, then merge
    sub_agents=[parallel_research_agent, merger_agent],
    description="Coordinates parallel research and synthesizes the results."
)

root_agent = sequential_pipeline_agent
# --8<-- [end:init]

# # --- 5. Running the Agent (Using InMemoryRunner for local testing) This works in Notebooks and script file ---

# # Use InMemoryRunner: Ideal for quick prototyping and local testing
# runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
# print(f"InMemoryRunner created for agent '{root_agent.name}'.")

# # We still need access to the session service (bundled in InMemoryRunner)
# # to create the session instance for the run.
# session_service = runner.session_service
# session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
# print(f"Session '{SESSION_ID}' created for direct run.")


# async def call_sequential_pipeline(query: str, user_id: str, session_id: str):
#     """
#     Helper async function to call the sequential agent pipeline.
#     Prints intermediate results from parallel agents and the final merged response.
#     """
#     print(f"\n--- Running Research & Synthesis Pipeline for query: '{query}' ---")
#     # The initial query mainly triggers the pipeline; the research topics are fixed in the agents for this example.
#     content = types.Content(role='user', parts=[types.Part(text=query)])
#     final_response_text = None
#     # Keep track of which researchers have reported
#     researcher_outputs = {}
#     researcher_names = {"RenewableEnergyResearcher", "EVResearcher", "CarbonCaptureResearcher"}
#     merger_agent_name = "SynthesisAgent" # Name of the final agent in sequence

#     print("Starting pipeline...")
#     try:
#         async for event in runner.run_async(
#             user_id=user_id, session_id=session_id, new_message=content
#         ):
#             author_name = event.author or "System"
#             is_final = event.is_final_response()
#             print(f"  [Event] From: {author_name}, Final: {is_final}") # Basic event logging

#             # Check if it's a final response from one of the researcher agents
#             if is_final and author_name in researcher_names and event.content and event.content.parts:
#                 researcher_output = event.content.parts[0].text.strip()
#                 if author_name not in researcher_outputs: # Print only once per researcher
#                     print(f"    -> Intermediate Result from {author_name}: {researcher_output}")
#                     researcher_outputs[author_name] = researcher_output

#             # Check if it's the final response from the merger agent (the last agent in the sequence)
#             elif is_final and author_name == merger_agent_name and event.content and event.content.parts:
#                  final_response_text = event.content.parts[0].text.strip()
#                  print(f"\n<<< Final Synthesized Response (from {author_name}):\n{final_response_text}")
#                  # Since this is the last agent in the sequence, we can break after its final response
#                  break

#             elif event.is_error():
#                  print(f"  -> Error from {author_name}: {event.error_message}")

#         if final_response_text is None:
#              print("<<< Pipeline finished but did not produce the expected final text response from the SynthesisAgent.")

#     except Exception as e:
#         print(f"\n❌ An error occurred during agent execution: {e}")



# initial_trigger_query = "Summarize recent sustainable tech advancements."

# # In Colab/Jupyter:
# await call_sequential_pipeline(initial_trigger_query, user_id=USER_ID, session_id=SESSION_ID)

# # In a standalone Python script or if await is not supported/failing:
# # import asyncio
# # asyncio.run(call_sequential_pipeline(initial_trigger_query, user_id=USER_ID, session_id=SESSION_ID))
