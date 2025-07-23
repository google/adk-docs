# Quickstart: Exposing Your First Agent via A2A

This guide covers the most common starting point for any developer: **"I have an agent, how do I let other agents use it?"** This is crucial for building complex multi-agent systems where different agents need to collaborate and interact.

We will take a basic ADK agent and expose it as a secure, network-accessible service using a single command.

## The Agent: A Simple "Prime Checker"

First, let's create a simple ADK agent that we'll expose. Create a new directory named `my_prime_agent` and inside it, create a file named `agent.py` with the following content:

```python title="my_prime_agent/agent.py"
from google.adk import Agent

async def check_prime(num: int) -> str:
  if num < 2:
    return f"{num} is not a prime number."
  for i in range(2, int(num**0.5) + 1):
    if num % i == 0:
      return f"{num} is not a prime number."
  return f"{num} is a prime number."

root_agent = Agent(
    model='gemini-2.0-flash',
    name='prime_checker',
    tools=[check_prime],
)
```

This `agent.py` file defines a basic ADK agent named `prime_checker` with a single tool, `check_prime`, which determines if a given number is prime.

> **Tip:** For a more integrated experience with all sample code, you can clone the `adk-python` repository and navigate to the `adk-python/contributing/samples/a2a_basic` directory. The `agent.py` file there is identical to the one above.

```bash
git clone https://github.com/google/adk-python.git
cd adk-python/contributing/samples/a2a_basic
```



## Exposing Your Agent with the ADK Server

The ADK comes with a built-in, production-ready web server designed to serve
agents. There are two primary ways to expose your agent using the A2A protocol:

### Option 1: Using the `adk api_server` Command

This method is ideal for deploying an agent as a standalone service. To expose your agent, use the `adk api_server` command with the `--a2a` flag.

> **Note:** The `adk api_server` command runs a **headless, API-only server**
> suitable for production environments. This is different from `adk web`, which
> launches the interactive Dev UI.

Open your terminal and run the following command, providing the path to the **directory** containing your agent's code:

```bash
adk api_server --a2a --port 8001 .
```

### Option 2: Programmatically Exposing an Agent with `.to_a2a()`

For more integrated scenarios, such as when you want to embed an A2A server directly within an existing application or script, you can programmatically expose your agent using the `.to_a2a()` method. This method allows you to start the A2A server directly from your Python code.

Add the following lines to your `agent.py` file:

```python title="my_prime_agent/agent.py"
# ... (previous agent definition)

if __name__ == "__main__":
    root_agent.to_a2a(root_agent, port=8001)
```

Then, you can run your `agent.py` file directly:

```bash
python my_prime_agent/agent.py
```

This will start the A2A server on port 8001, exposing your `prime_checker` agent.



This command starts a FastAPI server and creates a standard A2A endpoint for
your agent. The server will automatically handle request validation, data
serialization, and error handling according to the A2A specification.

### Verify the Server is Running

To confirm that your agent is being served correctly, you can request its OpenAPI
specification. Open a new terminal and run:

```bash
curl http://localhost:8001/openapi.json
```

You should see a JSON output describing your agent's API. This confirms your
server is running and ready to accept requests.

<details>
<summary>Click to see an example of the expected output</summary>

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "prime_checker",
    "version": "0.1.0"
  },
  "paths": {
    "/a2a/prime_checker": {
      "post": {
        "summary": "A2A Endpoint for prime_checker",
        "operationId": "a2a_prime_checker_a2a_prime_checker_post",
        "requestBody": { ... },
        "responses": { ... }
      }
    }
  },
  "components": {
    "schemas": {
      "check_prime": {
        "properties": {
          "num": {
            "title": "Num",
            "type": "integer"
          }
        },
        "type": "object",
        "required": ["num"],
        "title": "check_prime"
      },
      ...
    }
  }
}
```

</details>

## Next Steps

Now that you have created an A2A server, the next step is to learn how to
connect to it from another agent.

- **Continue to the next guide:** [Connecting to a Remote Agent](./connecting-to-remote-agents.md)
