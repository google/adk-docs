# Quickstart: Exposing a remote agent via A2A

Supported in ADKPythonExperimental

This quickstart covers the most common starting point for any developer: **"I have an agent. How do I expose it so that other agents can use my agent via A2A?"**. This is crucial for building complex multi-agent systems where different agents need to collaborate and interact.

## Overview

This sample demonstrates how you can easily expose an ADK agent so that it can be then consumed by another agent using the A2A Protocol.

There are two main ways to expose an ADK agent via A2A.

- **by using the `to_a2a(root_agent)` function**: use this function if you just want to convert an existing agent to work with A2A, and be able to expose it via a server through `uvicorn`, instead of `adk deploy api_server`. This means that you have tighter control over what you want to expose via `uvicorn` when you want to productionize your agent. Furthermore, the `to_a2a()` function auto-generates an agent card based on your agent code.
- **by creating your own agent card (`agent.json`) and hosting it using `adk api_server --a2a`**: There are two main benefits of using this approach. First, `adk api_server --a2a` works with `adk web`, making it easy to use, debug, and test your agent. Second, with `adk api_server`, you can specify a parent folder with multiple, separate agents. Those agents that have an agent card (`agent.json`), will automatically be usable via A2A by other agents through the same server. However, you will need to create your own agent cards. To create an agent card, you can follow the [A2A Python tutorial](https://a2a-protocol.org/latest/tutorials/python/1-introduction/).

This quickstart will focus on `to_a2a()`, as it is the easiest way to expose your agent and will also autogenerate the agent card behind-the-scenes. If you'd like to use the `adk api_server` approach, you can see it being used in the [A2A Quickstart (Consuming) documentation](https://google.github.io/adk-docs/a2a/quickstart-consuming/index.md).

```text
Before:
                                                ┌────────────────────┐
                                                │ Hello World Agent  │
                                                │  (Python Object)   │
                                                | without agent card │
                                                └────────────────────┘

                                                          │
                                                          │ to_a2a()
                                                          ▼

After:
┌────────────────┐                             ┌───────────────────────────────┐
│   Root Agent   │       A2A Protocol          │ A2A-Exposed Hello World Agent │
│(RemoteA2aAgent)│────────────────────────────▶│      (localhost: 8001)         │
│(localhost:8000)│                             └───────────────────────────────┘
└────────────────┘
```

The sample consists of :

- **Remote Hello World Agent** (`remote_a2a/hello_world/agent.py`): This is the agent that you want to expose so that other agents can use it via A2A. It is an agent that handles dice rolling and prime number checking. It becomes exposed using the `to_a2a()` function and is served using `uvicorn`.
- **Root Agent** (`agent.py`): A simple agent that is just calling the remote Hello World agent.

## Exposing the Remote Agent with the `to_a2a(root_agent)` function

You can take an existing agent built using ADK and make it A2A-compatible by simply wrapping it using the `to_a2a()` function. For example, if you have an agent like the following defined in `root_agent`:

```python
# Your agent code here
root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world_agent',

    <...your agent code...>
)
```

Then you can make it A2A-compatible simply by using `to_a2a(root_agent)`:

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Make your agent A2A-compatible
a2a_app = to_a2a(root_agent, port=8001)
```

The `to_a2a()` function will even auto-generate an agent card in-memory behind-the-scenes by [extracting skills, capabilities, and metadata from the ADK agent](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/utils/agent_card_builder.py), so that the well-known agent card is made available when the agent endpoint is served using `uvicorn`.

You can also provide your own agent card by using the `agent_card` parameter. The value can be an `AgentCard` object or a path to an agent card JSON file.

**Example with an `AgentCard` object:**

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard

# Define A2A agent card
my_agent_card = AgentCard(
    name="file_agent",
    url="http://example.com",
    description="Test agent from file",
    version="1.0.0",
    capabilities={},
    skills=[],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    supportsAuthenticatedExtendedCard=False,
)
a2a_app = to_a2a(root_agent, port=8001, agent_card=my_agent_card)
```

**Example with a path to a JSON file:**

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Load A2A agent card from a file
a2a_app = to_a2a(root_agent, port=8001, agent_card="/path/to/your/agent-card.json")
```

Now let's dive into the sample code.

### 1. Getting the Sample Code

First, make sure you have the necessary dependencies installed:

```bash
pip install google-adk[a2a]
```

You can clone and navigate to the [**a2a_root** sample](https://github.com/google/adk-python/tree/main/contributing/samples/a2a_root) here:

```bash
git clone https://github.com/google/adk-python.git
```

As you'll see, the folder structure is as follows:

```text
a2a_root/
├── remote_a2a/
│   └── hello_world/    
│       ├── __init__.py
│       └── agent.py    # Remote Hello World Agent
├── README.md
└── agent.py            # Root agent
```

#### Root Agent (`a2a_root/agent.py`)

- **`root_agent`**: A `RemoteA2aAgent` that connects to the remote A2A service
- **Agent Card URL**: Points to the well-known agent card endpoint on the remote server

#### Remote Hello World Agent (`a2a_root/remote_a2a/hello_world/agent.py`)

- **`roll_die(sides: int)`**: Function tool for rolling dice with state management
- **`check_prime(nums: list[int])`**: Async function for prime number checking
- **`root_agent`**: The main agent with comprehensive instructions
- **`a2a_app`**: The A2A application created using `to_a2a()` utility

### 2. Start the Remote A2A Agent server

You can now start the remote agent server, which will host the `a2a_app` within the hello_world agent:

```bash
# Ensure current working directory is adk-python/
# Start the remote agent using uvicorn
uvicorn contributing.samples.a2a_root.remote_a2a.hello_world.agent:a2a_app --host localhost --port 8001
```

Why use port 8001?

In this quickstart, when testing locally, your agents will be using localhost, so the `port` for the A2A server for the exposed agent (the remote, prime agent) must be different from the consuming agent's port. The default port for `adk web` where you will interact with the consuming agent is `8000`, which is why the A2A server is created using a separate port, `8001`.

Once executed, you should see something like:

```shell
INFO:     Started server process [10615]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8001 (Press CTRL+C to quit)
```

### 3. Check that your remote agent is running

You can check that your agent is up and running by visiting the agent card that was auto-generated earlier as part of your `to_a2a()` function in `a2a_root/remote_a2a/hello_world/agent.py`:

<http://localhost:8001/.well-known/agent-card.json>

You should see the contents of the agent card, which should look like:

```json
{"capabilities":{},"defaultInputModes":["text/plain"],"defaultOutputModes":["text/plain"],"description":"hello world agent that can roll a dice of 8 sides and check prime numbers.","name":"hello_world_agent","protocolVersion":"0.2.6","skills":[{"description":"hello world agent that can roll a dice of 8 sides and check prime numbers. \n      I roll dice and answer questions about the outcome of the dice rolls.\n      I can roll dice of different sizes.\n      I can use multiple tools in parallel by calling functions in parallel(in one request and in one round).\n      It is ok to discuss previous dice roles, and comment on the dice rolls.\n      When I are asked to roll a die, I must call the roll_die tool with the number of sides. Be sure to pass in an integer. Do not pass in a string.\n      I should never roll a die on my own.\n      When checking prime numbers, call the check_prime tool with a list of integers. Be sure to pass in a list of integers. I should never pass in a string.\n      I should not check prime numbers before calling the tool.\n      When I are asked to roll a die and check prime numbers, I should always make the following two function calls:\n      1. I should first call the roll_die tool to get a roll. Wait for the function response before calling the check_prime tool.\n      2. After I get the function response from roll_die tool, I should call the check_prime tool with the roll_die result.\n        2.1 If user asks I to check primes based on previous rolls, make sure I include the previous rolls in the list.\n      3. When I respond, I must include the roll_die result from step 1.\n      I should always perform the previous 3 steps when asking for a roll and checking prime numbers.\n      I should not rely on the previous history on prime results.\n    ","id":"hello_world_agent","name":"model","tags":["llm"]},{"description":"Roll a die and return the rolled result.\n\nArgs:\n  sides: The integer number of sides the die has.\n  tool_context: the tool context\nReturns:\n  An integer of the result of rolling the die.","id":"hello_world_agent-roll_die","name":"roll_die","tags":["llm","tools"]},{"description":"Check if a given list of numbers are prime.\n\nArgs:\n  nums: The list of numbers to check.\n\nReturns:\n  A str indicating which number is prime.","id":"hello_world_agent-check_prime","name":"check_prime","tags":["llm","tools"]}],"supportsAuthenticatedExtendedCard":false,"url":"http://localhost:8001","version":"0.0.1"}
```

### 4. Run the Main (Consuming) Agent

Now that your remote agent is running, you can launch the dev UI and select "a2a_root" as your agent.

```bash
# In a separate terminal, run the adk web server
adk web contributing/samples/
```

To open the adk web server, go to: <http://localhost:8000>.

## Example Interactions

Once both services are running, you can interact with the root agent to see how it calls the remote agent via A2A:

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

Now that you have created an agent that's exposing a remote agent via an A2A server, the next step is to learn how to consume it from another agent.

- [**A2A Quickstart (Consuming)**](https://google.github.io/adk-docs/a2a/quickstart-consuming/index.md): Learn how your agent can use other agents using the A2A Protocol.
