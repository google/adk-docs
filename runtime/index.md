# Agent Runtime

Supported in ADKPython v0.1.0TypeScript v0.2.0Go v0.1.0Java v0.1.0

ADK provides several ways to run and test your agents during development. Choose the method that best fits your development workflow.

## Ways to run agents

- **Dev UI**

  ______________________________________________________________________

  Use `adk web` to launch a browser-based interface for interacting with your agents.

  [Use the Web Interface](https://adk.dev/runtime/web-interface/index.md)

- **Command Line**

  ______________________________________________________________________

  Use `adk run` to interact with your agents directly in the terminal.

  [Use the Command Line](https://adk.dev/runtime/command-line/index.md)

- **API Server**

  ______________________________________________________________________

  Use `adk api_server` to expose your agents through a RESTful API.

  [Use the API Server](https://adk.dev/runtime/api-server/index.md)

## Technical reference

For more in-depth information on runtime configuration and behavior, see these pages:

- **[Event Loop](https://adk.dev/runtime/event-loop/index.md)**: Understand the core event loop that powers ADK, including the yield/pause/resume cycle.
- **[Resume Agents](https://adk.dev/runtime/resume/index.md)**: Learn how to resume agent execution from a previous state.
- **[Runtime Config](https://adk.dev/runtime/runconfig/index.md)**: Configure runtime behavior with RunConfig.
