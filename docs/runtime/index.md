# Agent Runtime

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK provides several ways to run and test your agents during development. Choose
the method that best fits your development workflow.

## Ways to run agents

<div class="grid cards" markdown>

-   :material-web:{ .lg .middle } **Dev UI**

    ---

    Use `adk web` to launch a browser-based interface for interacting with your
    agents.

    [:octicons-arrow-right-24: Use the Web Interface](web-interface.md)

-   :material-console:{ .lg .middle } **Command Line**

    ---

    Use `adk run` to interact with your agents directly in the terminal.

    [:octicons-arrow-right-24: Use the Command Line](command-line.md)

-   :material-api:{ .lg .middle } **API Server**

    ---

    Use `adk api_server` to expose your agents through a RESTful API.

    [:octicons-arrow-right-24: Use the API Server](api-server.md)

</div>

## Technical reference

For more in-depth information on runtime configuration and behavior, see these
pages:

- **[Event Loop](event-loop.md)**: Understand the core event loop that powers
  ADK, including the yield/pause/resume cycle.
- **[Resume Agents](resume.md)**: Learn how to resume agent execution from a
  previous state.
- **[Runtime Config](runconfig.md)**: Configure runtime behavior with
  RunConfig.
