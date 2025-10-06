# Python Quickstart for ADK

This guide shows you how to get up and running with the Agent Development Kit
(ADK) for Python. Before you start, make sure you have the following installed:

*   Python 3.9 or later
*   `pip` for installing packages   

## Installation

Install ADK by running the following command:

```shell
pip install google-adk
```

??? tip "Recommended: create and activate a Python virtual environment"

    Create a Python virtual environment:

    ```shell
    python -m venv .venv
    ```

    Activate the Python virtual environment:

    === "Windows CMD"

        ```shell
        .venv\Scripts\activate.bat
        ```

    === "Windows Powershell"

        ```shell
        .venv\Scripts\Activate.ps1
        ```

    === "MacOS / Linux"

        ```shell
        source .venv/bin/activate
        ```

## Create an agent project

Run the `adk create` command to start a new agent project. 

```shell
adk create my_agent
```

??? tip "Note: API key required"
    The created project uses Gemini, which requires an API key. Create a key in
    Google AI Studio on the [API Keys](https://aistudio.google.com/app/apikey) page.
    You can also use a Google Cloud project ID with access to the Vertex AI.

### Explore the agent project

The created agent project has the following structure, with the `agent.py`
file containing the main control code for the agent.

```shell
my_agent/
    agent.py      # main agent code.
    .env          # API keys or project IDs
    __init__.py
```

The `agent.py` file contains a `root_agent` definition which is the only
required element of an ADK agent. You can also define tools for the agent to
use. The following example includes an additional `get_current_time` tool for
use by the agent:

```python
from google.adk.agents.llm_agent import Agent

# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    if city.lower() == "new york":
        return {"status": "success", "time": "10:30 AM EST"}
    return {"status": "error", "message": f"Time for {city} not available."}

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    tools=[get_current_time]
)
```

## Run your agent

Run your agent using the `adk run` command-line tool.

```shell
adk run my_agent
```

![adk-run.png](../assets/adk-run.png)

### Run agent with web interface

The ADK framework provides web interface you can use to test and interact with
your agent. You can start the web interface using the following terminal

```shell
adk web my_agent
```
This command starts a web server with a chat interface for your agent:

![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)

## Next: build your agent

Now that you have ADK installed and your first agent running, try building
your own agent with our intermediate build guides:

*  [Build your agent](/adk-docs/tutorials/)
