# ADK Tutorial - Progressive Weather Bot (ADK Tools Version)

This repository contains the code for the "Build Your First Intelligent Agent Team: A Progressive Weather Bot" tutorial, specifically structured for use with the Agent Development Kit (ADK) built-in command-line tools: `adk web`, `adk run`, and `adk api_server`.

This version allows you to run each step of the tutorial without manually setting up runners and session services, as those are handled by the ADK tools.

**Note:** If you prefer a notebook environment (like Colab or Jupyter) with manual control over runners and sessions, please refer to the [original notebook tutorial version](Your_Link_To_Notebook_Version_Here).

## Prerequisites

*   **Python:** Version 3.9 - 3.12 (Check ADK documentation for the latest compatibility).
*   **Git:** To clone this repository.
*   **LLM API Keys:** You will need API keys for the services used in the tutorial steps (Google Gemini, potentially OpenAI and Anthropic).
    *   Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
    *   OpenAI Platform: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
    *   Anthropic Console: [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/google/adk-docs.git
    cd adk-docs/examples/python/tutorial/agent_team/adk-tutorial/ # Navigate into the cloned directory
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    This isolates project dependencies.

    *   **Create:**
        ```bash
        python -m venv .venv
        ```
    *   **Activate (execute in each new terminal session):**
        *   macOS / Linux:
            ```bash
            source .venv/bin/activate
            ```
        *   Windows (Command Prompt):
            ```bash
            .venv\Scripts\activate.bat
            ```
        *   Windows (PowerShell):
            ```ps1
            .venv\Scripts\Activate.ps1
            ```
        *(You should see `(.venv)` preceding your terminal prompt)*

3.  **Install Dependencies:**
    Install ADK and LiteLLM (for multi-model support).
    ```bash
    pip install google-adk
    pip install litellm
    ```

## Configuration: API Keys

Before running any agent step, you **must** configure your API keys.

1.  Navigate into the directory for the specific step you want to run (e.g., `step_1`, `step_2_anthropic`, `step_3`, etc.).
2.  Each step directory contains a `.env` file. Open this file in a text editor.
3.  Replace the placeholder values with your actual API keys.

    **Example `.env` content:**
    ```dotenv
    # Set to False to use API keys directly (required for multi-model)
    GOOGLE_GENAI_USE_VERTEXAI=FALSE

    # --- Replace with your actual keys ---
    GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_GOOGLE_API_KEY_HERE
    ANTHROPIC_API_KEY=PASTE_YOUR_ACTUAL_ANTHROPIC_API_KEY_HERE
    OPENAI_API_KEY=PASTE_YOUR_ACTUAL_OPENAI_API_KEY_HERE
    # --- End of keys ---
    ```
4.  **Save the `.env` file.**
5.  **Repeat this process** for the `.env` file in *every* step directory you intend to run. The keys needed might vary slightly depending on the models used in that specific step.

## Running the Examples

Ensure your virtual environment is activated before running these commands. Each `agent.py` file (e.g., in `step_1`) contains example queries you can use to test the agents. 

### Using `adk web` (Recommended for Interactive UI)

1.  **Navigate to the parent `adk-tutorial` directory** (the one containing the `step_1`, `step_2_...` folders).
    ```bash
    # Make sure you are in the main 'adk-tutorial' folder
    cd /path/to/your/adk-tutorial
    ```
2.  **Run the command:**
    ```bash
    adk web
    ```
3.  This will start a local web server and likely open a new tab in your browser.
4.  In the web UI, you'll find a dropdown menu (usually on the left). Use this dropdown to **select the agent step** you want to interact with (e.g., `step_1`, `step_2_gpt4`, `step_6`).
5.  Once selected, you can type messages in the chat interface to interact with the agent for that specific step.

### Using `adk run` (Command-Line Interaction)

The `adk run` command allows you to interact with an agent directly from your terminal. You typically specify the path to the agent file.

*   **Example (running Step 1):**
    ```bash
    # Make sure you are in the main 'adk-tutorial' folder
    adk run step_1
    ```
*   For detailed usage and options for `adk run`, please refer to the [Official ADK Documentation - Run Your Agent](https://google.github.io/adk-docs/get-started/quickstart/#terminal-adk-run).

### Using `adk api_server` (Exposing as API)

The `adk api_server` command starts a FastAPI server, exposing your agent via an API endpoint.

*   **Example (serving Step 1):**
    ```bash
    # Make sure you are in the main 'adk-tutorial' folder
    adk api_server
    ```
*   For detailed usage, API endpoint structure, and options for `adk api_server`, please consult the [Official ADK Documentation - Testing your Agents](https://google.github.io/adk-docs/get-started/testing/).

## Directory Structure

```
adk-tutorial/
├── step_1/
│   ├── __init__.py
│   ├── agent.py      # Agent definition for Step 1
│   └── .env          # API Key configuration for Step 1
├── step_2_anthropic/
│   ├── __init__.py
│   ├── agent.py      # Agent definition for Step 2 (Anthropic)
│   └── .env          # API Key configuration for Step 2 (Anthropic)
├── step_2_gpt4/
│   ├── __init__.py
│   ├── agent.py      # Agent definition for Step 2 (GPT-4)
│   └── .env          # API Key configuration for Step 2 (GPT-4)
├── step_3/
│   ├── __init__.py
│   ├── agent.py      # Agent definition for Step 3
│   └── .env          # API Key configuration for Step 3
├── step_5/
│   # ...
└── step_6/
    # ...
└── README.md         # This file
```

Each `step_X` directory is self-contained regarding its agent logic (`agent.py`) and required API keys (`.env`).

## A Note on Step 4 (Session State & Personalization)

You might notice that "Step 4: Adding Memory and Personalization with Session State" is not included in this version of the tutorial (designed for use with `adk web`, `adk api_server`, or `adk run`).

The demonstration of session state concepts in Step 4, particularly the direct manipulation of `InMemorySessionService` for illustrative purposes, is best experienced in an interactive notebook environment (like Google Colab). This allows for immediate code execution and inspection of state changes that are less direct when using the ADK's built-in server tools.

## To experience the full tutorial including Step 4, please refer to the [interactive notebook version here](https://google.github.io/adk-docs/tutorials/agent-team/#step-4-adding-memory-and-personalization-with-session-state)

The subsequent steps in this folder-based tutorial (Step 5 onwards) build upon the concepts from Steps 1-3 and are designed to run correctly here, focusing on features like callbacks that are fully demonstrable with `adk web`/`run`.
