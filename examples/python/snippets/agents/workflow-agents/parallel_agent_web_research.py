# --- Setup Instructions ---
# 1. Install the ADK package:
# !pip install google-adk
# # Make sure to restart kernel if using colab/jupyter notebooks

# 2. Set up your Gemini API Key:
#    - Get a key from Google AI Studio: https://aistudio.google.com/app/apikey
#    - Set it as an environment variable:
import os
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE" # <--- REPLACE with your actual key
# # Or learn about other authentication methods (like Vertex AI, Anthropic API, etc.):
# # https://google.github.io/adk-docs/agents/models/

# Check if API key is set before proceeding (optional but recommended)
# if not os.getenv("GOOGLE_API_KEY"):
#     print("Warning: GOOGLE_API_KEY environment variable not set. Google Search tool may fail.")

# import asyncio # Required for async execution


from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
# Use InMemoryRunner for local testing/prototyping
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

# --- Configuration ---
APP_NAME = "parallel_research_app"
USER_ID = "research_user_01"
SESSION_ID = "parallel_research_session"
# Ensure this specific model is available or change to a suitable alternative.
GEMINI_MODEL = "gemini-2.0-flash" #

# --8<-- [start:init] 
# --- Define Researcher Sub-Agents ---

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
    tools=[google_search], # Provide the search tool
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
    tools=[google_search], # Provide the search tool
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
    tools=[google_search], # Provide the search tool
    output_key="carbon_capture_result"
)

# --- Create the ParallelAgent ---
# This agent orchestrates the concurrent execution of the researchers.
# For running with ADK CLI tools (adk web, adk run, adk api_server),
# this variable MUST be named `root_agent`.
parallel_research_agent = ParallelAgent(
    name="ParallelWebResearchAgent",
    sub_agents=[researcher_agent_1, researcher_agent_2, researcher_agent_3],
    description="Runs multiple research agents in parallel to gather information." # Added description
)

# --8<-- [end:init]

# --- Running the Agent (Choose ONE method) ---

# === Method 1: Running Directly (Notebook/Script) ===
# This method is suitable for local testing in Colab, Jupyter, or a Python script.
# It requires explicitly setting up the Runner and Session.

# Use InMemoryRunner: Ideal for quick prototyping and local testing.
# Why? It runs entirely in memory, requiring no external database or service setup.
# Limitation: Sessions, state, and artifacts are NOT persisted after the script finishes.
# When to use something else? For production or multi-user scenarios, use
# VertexAiSessionService (for managed deployment) or DatabaseSessionService (for self-hosting
# with persistence), or implement your own BaseSessionService.
runner = InMemoryRunner(agent=parallel_research_agent, app_name=APP_NAME)

# We still need access to the session service (bundled in InMemoryRunner)
# to create the session instance for the run.
session_service = runner.session_service
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
print(f"Session '{SESSION_ID}' created for direct run.")

# Agent Interaction using run_async
async def call_agent_directly(query):
    '''
    Helper async function to call the agent with a query using run_async.
    '''
    print(f"\n--- Calling Parallel Agent Directly with query: '{query}' ---")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    # Use runner.run_async for asynchronous execution
    print("Starting parallel research...")
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    ):
        # ParallelAgent itself doesn't usually produce a final text response directly.
        # Its purpose is to run sub-agents. The results are often in the state.
        # We print events for demonstration.
        print(f"  Event from {event.author}: Partial={event.partial}, Content Role={event.content.role if event.content else 'N/A'}")
        if event.is_final_response() and event.content:
             print(f"  -> Final Response Fragment from {event.author}: {event.content.parts[0].text.strip()}")
        elif event.is_error():
             print(f"  -> Error from {event.author}: {event.error_details}")

    # After the run, check the session state for results saved by output_key
    final_session = session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    print("\n--- Final Session State ---")
    # Use as_dict() for a cleaner dictionary representation of the state
    print(final_session.state)
    print("-" * 30)

async def run_direct_method():
     # Check API key again before running
     if not os.getenv("GOOGLE_API_KEY"):
         print("Error: GOOGLE_API_KEY needed for google_search tool. Set the environment variable.")
         return
     await call_agent_directly("research latest trends in sustainable tech")


# === Method 2: Preparing for ADK CLI (adk web, adk run, adk api_server) ===
# Instructions for deploying this agent using ADK command-line tools.
# Based on the Quickstart guide: https://google.github.io/adk-docs/get-started/quickstart/

# 1. Project Structure:
#    Organize your code into a standard Python package structure as shown in the quickstart.
#    Example:
#    parent_folder/
#    └── my_parallel_agent/     <-- Your agent package folder
#        ├── __init__.py
#        ├── agent.py           # <-- Put your agent definitions here
#        └── .env               # <-- Store GOOGLE_API_KEY here

# 2. Define `root_agent`:
#    In your `agent.py` file inside the package folder (e.g., `my_parallel_agent/agent.py`),
#    ensure the main agent you want the ADK tools to run (`parallel_research_agent` in this case)
#    is assigned to a variable named exactly `root_agent`.
#    ```python
#    # In my_parallel_agent/agent.py
#    # ... (define researcher_agent_1, _2, _3 as above)
#
#    root_agent = ParallelAgent( # <<< MUST be named root_agent for ADK CLI
#        name="ParallelWebResearchAgent",
#        sub_agents=[researcher_agent_1, researcher_agent_2, researcher_agent_3],
#        description="Runs multiple research agents in parallel."
#    )
#    ```
#    Also make sure your `__init__.py` imports this file (e.g., `from . import agent`).

# 3. Environment Variables (`.env`):
#    Create a file named `.env` inside your agent package folder (e.g., `my_parallel_agent/.env`)
#    and add your API key as shown in the quickstart (Section 3). Example:
#    ```env
#    GOOGLE_API_KEY=YOUR_API_KEY_HERE
#    # Or configure for Vertex AI as per quickstart if needed
#    # GOOGLE_GENAI_USE_VERTEXAI=TRUE
#    # GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
#    # GOOGLE_CLOUD_LOCATION=LOCATION
#    ```
#    The ADK tools will automatically load environment variables from this file.

# 4. Run with ADK CLI:
#    Navigate your terminal to the **parent folder** containing your agent package (e.g., `parent_folder/`).
#    Then run one of the ADK commands (see Quickstart Section 4):
#    ```bash
#    # For the interactive Dev UI:
#    adk web 
#
#    # For a single run in the terminal:
#    adk run my_parallel_agent --query "research latest trends"
#
#    # To start an API server:
#    adk api_server my_parallel_agent
#    ```
#    (Replace `my_parallel_agent` with the actual name of your agent package folder).

# 5. IMPORTANT - Code Differences for ADK CLI:
#    When preparing your `agent.py` for Method 2 (ADK CLI), you **DO NOT** include:
#      - The `InMemoryRunner` setup.
#      - The `session_service.create_session(...)` call.
#      - The `call_agent_directly` or `run_direct_method` helper functions.
#      - The final execution block (`if __name__ == "__main__":` or `await ...`).
#    The ADK tools handle the Runner, Session management, and execution loop automatically.
#    Your `agent.py` for Method 2 should essentially contain only the imports,
#    agent definitions, and the final `root_agent = ...` assignment.

# 6. Refer to Quickstart:
#    For complete details on project setup, authentication, and running with ADK tools,
#    please follow the official Quickstart guide:
#    https://google.github.io/adk-docs/get-started/quickstart/

# --8<-- [end:init]

# --- Execution Block (Only for Method 1 - Direct Run) ---
# Choose ONE method to execute. Comment out or remove the other.

# To run Method 1 (Directly in notebook/script):
print("Running Method 1: Direct Execution with InMemoryRunner")

# In a notebook environment:
await run_direct_method()

# In a standard Python script:
# if __name__ == "__main__":
#     asyncio.run(run_direct_method())

print("\nReminder: To run with ADK CLI tools (adk web/run/api_server), comment out the notebook/script execution block above, ensure your agent code is in the correct project structure (see Method 2 instructions), and run the appropriate 'adk' command from the parent directory.")