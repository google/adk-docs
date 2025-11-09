# A2A Agent Example

This example demonstrates how to expose an ADK agent using the Agent2Agent (A2A) protocol in Go using the ADK Web Launcher.

## Files

- `main.go`: This file contains a prime number checking agent and uses the ADK web launcher to expose it as an A2A service.

## How to Run

1.  **Start the server:**

    ```bash
    go run main.go
    ```

    This will start an A2A server on port 8001, serving the agent over JSON-RPC.

2.  **Interact with the agent:**

    You can interact with the A2A agent using any A2A compliant client, for example the one in `cmd/a2a_basic`.
