# Restate plugin for ADK

Supported in ADKPython

[Restate](https://restate.dev) is a durable execution engine that turns ADK agents into innately resilient, robust systems. It provides persistent sessions, pause/resume for human approvals, resilient multi-agent orchestration, safe versioning, and full observability and control over every execution. All LLM calls and tool executions are journaled, so if anything fails, your agent recovers from exactly where it left off.

## Use cases

The Restate plugin gives your agents:

- **Durable execution**: Never lose progress. If your agent crashes, it picks up exactly where it left off, with automatic retries and recovery.
- **Pause/resume for human-in-the-loop**: Pause execution for days or weeks until a human approves, then resume where you left off.
- **Durable state**: Agent memory and conversation history persist across restarts with built-in session management.
- **Observability & Task control**: See exactly what your agent did and kill, pause, and resume agent executions at any time.
- **Resilient multi-agent orchestration**: Run resilient workflows across multiple agents with parallel execution.
- **Safe versioning**: Deploy new versions without breaking ongoing executions via immutable deployments.

## Prerequisites

- Python 3.12+
- A [Gemini API key](https://aistudio.google.com/app/api-keys)

To run the example below, you'll also need:

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Docker](https://docs.docker.com/get-docker/) (or [Brew/npm/binary](https://docs.restate.dev/develop/local_dev#running-restate-server--cli-locally) for the Restate server)

## Installation

Install the Restate SDK for Python:

```bash
pip install "restate-sdk[serde]"
```

## Use with agent

Follow these steps to run a durable agent and inspect its execution journal in the Restate UI:

1. **Clone the [restate-google-adk-example repository](https://github.com/restatedev/restate-google-adk-example) and navigate to the example**

   ```bash
   git clone https://github.com/restatedev/restate-google-adk-example.git
   cd restate-google-adk-example/examples/hello-world
   ```

1. **Export your Gemini API key**

   ```bash
   export GOOGLE_API_KEY=your-api-key
   ```

1. **Start the weather agent**

   ```bash
   uv run .
   ```

1. **Start Restate in another terminal**

   ```bash
   docker run --name restate --rm -p 8080:8080 -p 9070:9070 -d \
     --add-host host.docker.internal:host-gateway \
     docker.restate.dev/restatedev/restate:latest
   ```

   Other installation methods: [Brew, npm, binary downloads](https://docs.restate.dev/develop/local_dev#running-restate-server--cli-locally)

1. **Register the agent**

   Open the Restate UI at `localhost:9070` and register your agent deployment (e.g., `http://host.docker.internal:9080`):

   Safe versioning

   Restate registers each deployment as an immutable snapshot. When you deploy a new version, ongoing executions finish on the original deployment while new requests route to the latest one. Learn more about [version-aware routing](https://docs.restate.dev/services/versioning).

1. **Send a request to the agent**

   In the Restate UI, select **WeatherAgent**, open the **Playground**, and send a request:

   Durable sessions and retries

   This request goes through Restate, which persists it before forwarding to your agent. Each session (here `session-1`) is isolated, stateful, and durable. If the agent crashes mid-execution, Restate automatically retries and resumes from the last journaled step, without losing progress.

1. **Inspect the execution journal**

   Click on the **Invocations** tab and then on your invocation to see the execution journal:

   Full control over agent executions

   Every LLM call and tool execution is recorded in the journal. From the UI, you can pause, resume, restart from any intermediate step, or kill an execution. Check the **State** tab to inspect your agent's current session data.

## Capabilities

The Restate plugin provides the following capabilities for your ADK agents:

| Capability                | Description                                                                                                 |
| ------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Durable tool execution    | Wraps tool logic with `restate_object_context().run_typed()` so it retries and recovers automatically       |
| Human-in-the-loop         | Pauses execution with `restate_object_context().awakeable()` until an external signal (e.g. human approval) |
| Persistent sessions       | `RestateSessionService()` stores agent memory and conversation state durably                                |
| Durable LLM calls         | `RestatePlugin()` journals LLM calls with automatic retries                                                 |
| Multi-agent communication | Durable cross-agent HTTP calls with `restate_object_context().service_call()`                               |
| Parallel execution        | Run tools and agents concurrently with `restate.gather()` for deterministic recovery                        |

## Additional resources

- [Restate ADK example repository](https://github.com/restatedev/restate-google-adk-example) - Runnable examples including claims processing with human approval
- [Restate ADK tutorial](https://docs.restate.dev/tour/google-adk) - Walkthrough of agent development with Restate and ADK
- [Restate AI documentation](https://docs.restate.dev/ai) - Full reference for durable AI agent patterns
- [Restate SDK on PyPI](https://pypi.org/project/restate-sdk/) - Python package
