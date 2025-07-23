# Connecting to a Remote Agent

In the previous guide, you learned how to expose an agent as an A2A service.
Now, we'll learn how to use that remote agent from a local agent.

## The `RemoteA2AAgent` Class

The key to connecting to a remote agent is the `RemoteA2AAgent` class. This
class acts as a smart, local proxy for the remote service. It fetches the
remote agent's OpenAPI specification upon initialization to understand its
capabilities, and then uses this specification to validate requests and handle
responses.

## Building the Root Agent

Here is the code for our `root_agent`. It defines a local `roll_die` tool and a
`RemoteA2AAgent` tool that points to our running `prime_checker` service.

```python title="root_agent/agent.py"
from google.adk import Agent
from google.adk.agents import RemoteA2AAgent
import random

def roll_die(sides: int = 6) -> str:
    return f"You rolled a {random.randint(1, sides)}."

# This is the client-side tool that connects to our remote service.
prime_agent_tool = RemoteA2AAgent(
    name="prime_checker",
    description="An agent that can check if a number is prime.",
    agent_card="http://localhost:8001/.well-known/agent.json",
)

# The root_agent orchestrates the local and remote tools.
root_agent = Agent(
    model='gemini-2.0-flash',
    name='math_agent',
    instruction='''
        You can roll dice and check for prime numbers.
        To roll a die, use the roll_die tool.
        To check a prime, use the prime_checker tool.
    ''',
    tools=[roll_die, prime_agent_tool],
)
```

> **How is the `agent_card` URL constructed?**
>
> The URL for a remote agent's card follows a standard format:
> `http://{host}:{port}/.well-known/agent.json`
>
> - `{host}` and `{port}` are the host and port you specified when running
>   `adk api_server`.
> - `/.well-known/agent.json` is the standard path for the agent card.
>
> For example, if you run the `prime_checker` agent on your local machine on
> port 8001, the URL would be:
> `http://localhost:8001/.well-known/agent.json`

## Running the Root Agent

With your remote `prime_checker` agent still running, you can now run your
`root_agent` and interact with it. The best way to do this is with the
`adk web` command, which provides an interactive UI for development.

Open a new terminal and run:

```bash
adk web root_agent/
```

This will launch the ADK Dev UI in your browser. You can now chat with your
`math_agent`. Try asking it:

> "Is 13 a prime number?"

The `root_agent` will correctly delegate this request to the remote
`prime_checker` agent and return the result to you.

## Next Steps

Now that you understand the basics of connecting agents, you can learn how to
add a layer of security.

- **Continue to the next guide:** [Authentication with A2A](./authentication.md)
