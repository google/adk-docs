# Quickstart: Consuming a remote agent via A2A

Supported in ADKPythonExperimental

This quickstart covers the most common starting point for any developer: **"There is a remote agent, how do I let my ADK agent use it via A2A?"**. This is crucial for building complex multi-agent systems where different agents need to collaborate and interact.

## Overview

This sample demonstrates the **Agent2Agent (A2A)** architecture in the Agent Development Kit (ADK), showcasing how multiple agents can work together to handle complex tasks. The sample implements an agent that can roll dice and check if numbers are prime.

```text
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   Root Agent    │───▶│   Roll Agent     │    │   Remote Prime     │
│  (Local)        │    │   (Local)        │    │   Agent            │
│                 │    │                  │    │  (localhost:8001)  │
│                 │───▶│                  │◀───│                    │
└─────────────────┘    └──────────────────┘    └────────────────────┘
```

The A2A Basic sample consists of:

- **Root Agent** (`root_agent`): The main orchestrator that delegates tasks to specialized sub-agents
- **Roll Agent** (`roll_agent`): A local sub-agent that handles dice rolling operations
- **Prime Agent** (`prime_agent`): A remote A2A agent that checks if numbers are prime, this agent is running on a separate A2A server

## Exposing Your Agent with the ADK Server

The ADK comes with a built-in CLI command, `adk api_server --a2a` to expose your agent using the A2A protocol.

In the `a2a_basic` example, you will first need to expose the `check_prime_agent` via an A2A server, so that the local root agent can use it.

### 1. Getting the Sample Code

First, make sure you have the necessary dependencies installed:

```bash
pip install google-adk[a2a]
```

You can clone and navigate to the [**`a2a_basic`** sample](https://github.com/google/adk-python/tree/main/contributing/samples/a2a_basic) here:

```bash
git clone https://github.com/google/adk-python.git
```

As you'll see, the folder structure is as follows:

```text
a2a_basic/
├── remote_a2a/
│   └── check_prime_agent/
│       ├── __init__.py
│       ├── agent.json
│       └── agent.py
├── README.md
├── __init__.py
└── agent.py # local root agent
```

#### Main Agent (`a2a_basic/agent.py`)

- **`roll_die(sides: int)`**: Function tool for rolling dice
- **`roll_agent`**: Local agent specialized in dice rolling
- **`prime_agent`**: Remote A2A agent configuration
- **`root_agent`**: Main orchestrator with delegation logic

#### Remote Prime Agent (`a2a_basic/remote_a2a/check_prime_agent/`)

- **`agent.py`**: Implementation of the prime checking service
- **`agent.json`**: Agent card of the A2A agent
- **`check_prime(nums: list[int])`**: Prime number checking algorithm

### 2. Start the Remote Prime Agent server

To show how your ADK agent can consume a remote agent via A2A, you'll first need to start a remote agent server, which will host the prime agent (under `check_prime_agent`).

```bash
# Start the remote a2a server that serves the check_prime_agent on port 8001
adk api_server --a2a --port 8001 contributing/samples/a2a_basic/remote_a2a
```

Adding logging for debugging with `--log_level debug`

To enable debug-level logging, you can add `--log_level debug` to your `adk api_server`, as in:

```bash
adk api_server --a2a --port 8001 contributing/samples/a2a_basic/remote_a2a --log_level debug
```

This will give richer logs for you to inspect when testing your agents.

Why use port 8001?

In this quickstart, when testing locally, your agents will be using localhost, so the `port` for the A2A server for the exposed agent (the remote, prime agent) must be different from the consuming agent's port. The default port for `adk web` where you will interact with the consuming agent is `8000`, which is why the A2A server is created using a separate port, `8001`.

Once executed, you should see something like:

```shell
INFO:     Started server process [56558]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

### 3. Look out for the required agent card (`agent-card.json`) of the remote agent

A2A Protocol requires that each agent must have an agent card that describes what it does.

If someone else has already built the remote A2A agent that you are looking to consume in your agent, then you should confirm that they have an agent card (`agent-card.json`).

In the sample, the `check_prime_agent` already has an agent card provided:

a2a_basic/remote_a2a/check_prime_agent/agent-card.json

```json
{
  "capabilities": {},
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["application/json"],
  "description": "An agent specialized in checking whether numbers are prime. It can efficiently determine the primality of individual numbers or lists of numbers.",
  "name": "check_prime_agent",
  "skills": [
    {
      "id": "prime_checking",
      "name": "Prime Number Checking",
      "description": "Check if numbers in a list are prime using efficient mathematical algorithms",
      "tags": ["mathematical", "computation", "prime", "numbers"]
    }
  ],
  "url": "http://localhost:8001/a2a/check_prime_agent",
  "version": "1.0.0"
}
```

More info on agent cards in ADK

In ADK, you can use a `to_a2a(root_agent)` wrapper which automatically generates an agent card for you. If you're interested in learning more about how to expose your existing agent so others can use it, then please look at the [A2A Quickstart (Exposing)](https://adk.dev/a2a/quickstart-exposing/index.md) tutorial.

### 4. Run the Main (Consuming) Agent

```bash
# In a separate terminal, run the adk web server
adk web contributing/samples/
```

#### How it works

The main agent uses the `RemoteA2aAgent()` function to consume the remote agent (`prime_agent` in our example). As you can see below, `RemoteA2aAgent()` requires the `name`, `description`, and the URL of the `agent_card`.

a2a_basic/agent.py

```python
<...code truncated...>

from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

prime_agent = RemoteA2aAgent(
    name="prime_agent",
    description="Agent that handles checking if numbers are prime.",
    agent_card=(
        f"http://localhost:8001/a2a/check_prime_agent{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
    use_legacy=False,
)

<...code truncated>
```

Using the new A2A integration

By setting `use_legacy=False`, the agent will use the new ADK-A2A integration, as it will send the [A2A extension](https://adk.dev/a2a/a2a-extension/index.md) to the remote agent.

Then, you can simply use the `RemoteA2aAgent` in your agent. In this case, `prime_agent` is used as one of the sub-agents in the `root_agent` below:

a2a_basic/agent.py

```python
from google.adk.agents.llm_agent import Agent
from google.genai import types

root_agent = Agent(
    model="gemini-flash-latest",
    name="root_agent",
    instruction="""
      <You are a helpful assistant that can roll dice and check if numbers are prime.
      You delegate rolling dice tasks to the roll_agent and prime checking tasks to the prime_agent.
      Follow these steps:
      1. If the user asks to roll a die, delegate to the roll_agent.
      2. If the user asks to check primes, delegate to the prime_agent.
      3. If the user asks to roll a die and then check if the result is prime, call roll_agent first, then pass the result to prime_agent.
      Always clarify the results before proceeding.>
    """,
    global_instruction=(
        "You are DicePrimeBot, ready to roll dice and check prime numbers."
    ),
    sub_agents=[roll_agent, prime_agent],
    tools=[example_tool],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # avoid false alarm about rolling dice.
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
```

### Advanced Configuration: Custom Converters and Interceptors

Internally, the `RemoteA2aAgent` translates between the A2A protocol format and the ADK's native `Event` system. You can customize this behaviour by passing an [`A2aRemoteAgentConfig`](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/agent/config.py) object via the `config` parameter to `RemoteA2aAgent`.

This allows you to define custom type mappings, inject request parameters, and intercept requests or responses.

#### Converters

Converters handle the translation of incoming A2A responses into native ADK objects. You can provide your own mapping functions for the following hooks:

- **`a2a_message_converter`**: Converts standard A2A Messages into ADK `Event` objects.
- **`a2a_task_converter`**: Converts an A2A Task into an ADK `Event`.
- **`a2a_status_update_converter`**: Converts A2A `TaskStatusUpdateEvent`s into ADK `Event` objects.
- **`a2a_artifact_update_converter`**: Converts A2A `TaskArtifactUpdateEvent`s into ADK `Event` objects.
- **`a2a_part_converter`**: A foundational low-level hook utilized internally by other converters to convert individual A2A Message Parts into GenAI `Part` objects.

Note

These custom client converters are used only when the response is coming from the new implementation of the [agent executor](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/executor/a2a_agent_executor_impl.py). For more details, see the [A2A extension](https://adk.dev/a2a/a2a-extension/index.md).

#### Request Interceptors

You can inject a list of `request_interceptors` to add middleware logic to A2A requests:

- **`before_request`**: Executed before the agent starts processing. You can modify the `A2AMessage`, or return an ADK `Event` to immediately abort the request and return that event to the caller.
- **`after_request`**: Executed after the agent has processed the request. You can modify the resulting ADK `Event`, or return `None` to filter out and drop the event entirely.

#### Request Parameters Configuration

Through interceptors, you can also modify the `ParametersConfig` for the A2A request to inject:

- **`request_metadata`**: Pass custom metadata dictionaries into the request headers.
- **`client_call_context`**: Inject specific client call contexts for the underlying transport.

```python
<...code truncated...>

from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

prime_agent = RemoteA2aAgent(
    name="prime_agent",
    description="Agent that handles checking if numbers are prime.",
    agent_card=(
        f"http://localhost:8001/a2a/check_prime_agent{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
    use_legacy=False,
    config=A2aRemoteAgentConfig(
        a2a_message_converter=my_a2a_message_converter,
        request_interceptors=[my_request_interceptor],
    ),
)

<...code truncated>
```

## Example Interactions

Once both your main and remote agents are running, you can interact with the root agent to see how it calls the remote agent via A2A:

**Simple Dice Rolling:** This interaction uses a local agent, the Roll Agent:

```text
User: Roll a 6-sided die
Bot: I rolled a 4 for you.
```

**Prime Number Checking:**

This interaction uses a remote agent via A2A, the Prime Agent:

```text
User: Is 7 a prime number?
Bot: Yes, 7 is a prime number.
```

**Combined Operations:**

This interaction uses both the local Roll Agent and the remote Prime Agent:

```text
User: Roll a 10-sided die and check if it's prime
Bot: I rolled an 8 for you.
Bot: 8 is not a prime number.
```

## Next Steps

Now that you have created an agent that's using a remote agent via an A2A server, the next step is to learn how to connect to it from another agent.

- [**A2A Quickstart (Exposing)**](https://adk.dev/a2a/quickstart-exposing/index.md): Learn how to expose your existing agent so that other agents can use it via the A2A Protocol.
