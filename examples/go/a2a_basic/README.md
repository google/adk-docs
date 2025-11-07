# A2A Consuming Agent Example

This example demonstrates how an ADK agent can consume a remote A2A agent in Go.
It sets up a "Root Agent" that delegates tasks to a local "Roll Agent" and a remote "Prime Agent".

## Prerequisites

Before running this example, you need to have the A2A serving example running.
Follow the instructions in [remote_a2a/check_prime_agent/README.md](https://github.com/google/adk-docs/blob/main/examples/go/a2a_basic/remote_a2a/check_prime_agent/README.md) to start the serving agent on port 8001.

## Files

- `main.go`: This file contains the implementation of the local Roll Agent, the remote Prime Agent, and the orchestrating Root Agent.

## How to Run

1.  **Ensure the A2A serving example is running** (from `cmd/a2a_basic/remote_a2a/check_prime_agent`).

2.  **Run this consuming example:**

    ```bash
    go run main.go
    ```

## Expected Output

When you run this example, you should see output similar to this:

```
--- Example Interaction ---
User: Roll a 6-sided die and check if it's prime
Bot calls tool: roll_dice with args: map[sides:6]
Bot calls tool: prime_checking with args: map[nums:[<roll_result>]]
Bot: I can roll dice or check prime numbers. What would you like?
```

**Note:** The mock LLM in this example is very basic and will not actually execute the tools or provide a coherent response for combined operations. It's designed to demonstrate the delegation mechanism. For a real-world scenario, you would integrate with an actual LLM.
