---
catalog_title: Restate
catalog_description: Resilient agent execution and orchestration with durable sessions and human approvals
catalog_icon: /adk-docs/integrations/assets/restate.svg
---

# Restate plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Restate](https://restate.dev) is a durable execution engine that turns ADK agents into innately resilient, robust systems. 
It provides persistent sessions, pause/resume for human approvals, 
resilient multi-agent orchestration, safe versioning, and full
observability and control over every execution. All LLM calls and tool executions
are journaled, so if anything fails, your agent recovers from exactly where it
left off.

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

## Installation

```bash
pip install "restate-sdk[serde]"
```

## Use with agent

The following example creates a minimal durable agent with a weather tool:

- Add the `RestatePlugin` to your ADK app to journal LLM calls
- Use the `RestateSessionService` to get persistent sessions and concurrency management
- Make tool executions durable via Restate Context actions, such as `restate_object_context().run_typed()` for API calls
- Run the ADK runner from within a Restate handler, and call the agent at `http://localhost:8080/WeatherAgent/session-1/run`

```python
import restate
from google.adk import Runner
from google.adk.agents.llm_agent import Agent
from google.adk.apps import App
from google.genai.types import Content, Part
from restate.ext.adk import RestatePlugin, RestateSessionService, restate_object_context


async def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    async def fetch_weather() -> str:
        return f"The weather in {city} is sunny, 72°F"

    # Durable execution: automatically retries and recovers on failure
    return await restate_object_context().run_typed("Get weather", fetch_weather)


agent = Agent(
    model="gemini-2.5-flash",
    name="weather_agent",
    instruction="You are a helpful weather assistant.",
    tools=[get_weather],
)

app = App(name="agents", root_agent=agent, plugins=[RestatePlugin()])
runner = Runner(app=app, session_service=RestateSessionService())

weather_service = restate.VirtualObject("WeatherAgent")

@weather_service.handler()
async def run(ctx: restate.ObjectContext, message: str) -> str | None:
    events = runner.run_async(
        user_id=ctx.key(),
        session_id="session",
        new_message=Content(role="user", parts=[Part.from_text(text=message)]),
    )
    final_response = None
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            if event.content.parts[0].text:
                final_response = event.content.parts[0].text
    return final_response
```

View the execution journal in the Restate UI, inspect failures and pause, resume or kill executions:

[Visit the example repository for the complete, latest example.](https://github.com/restatedev/restate-google-adk-example)

## Capabilities

| Capability | Description |
| --- | --- |
| Durable tool execution | Wraps tool logic with `restate_object_context().run_typed()` so it retries and recovers automatically |
| Human-in-the-loop | Pauses execution with `restate_object_context().awakeable()` until an external signal (e.g. human approval) |
| Persistent sessions | `RestateSessionService()` stores agent memory and conversation state durably |
| Durable LLM calls | `RestatePlugin()` journals LLM calls with automatic retries |
| Multi-agent communication | Durable cross-agent HTTP calls with `restate_object_context().service_call()` |
| Parallel execution | Run tools and agents concurrently with `restate.gather()` for deterministic recovery |

## Quickstart

1. **Clone the [example repository](https://github.com/restatedev/restate-google-adk-example/tree/main/examples/hello-world)**

    ```bash
    git clone git@github.com:restatedev/restate-google-adk-example.git && cd restate-google-adk-example/examples/hello-world
    ```

2. **Export your Gemini API key**

    ```bash
    export GOOGLE_API_KEY=your-api-key
    ```

3. **Start the weather agent**

    ```bash
    uv run .
    ```

4. **Start Restate in another terminal**

    ```bash
    docker run --name restate --rm -p 8080:8080 -p 9070:9070 -d \
      --add-host host.docker.internal:host-gateway \
      docker.restate.dev/restatedev/restate:latest
    ```

    Other install methods: [Brew, npm, binary downloads](https://docs.restate.dev/develop/local_dev#running-restate-server--cli-locally)

5. **Register the agent**

    Open the Restate UI at `localhost:9070` and register your agent deployment (`http://host.docker.internal:9080`):

    ![Restate registration](./assets/restate-registration.png)

    !!! tip "Safe versioning"
        Restate registers each deployment as an immutable snapshot. When you deploy a new version, ongoing executions finish on the original deployment while new requests route to the latest one. Learn more about [version-aware routing](https://docs.restate.dev/services/versioning).

6. **Send a request to the agent**

    Click on the `run` handler of the `WeatherAgent` service in the UI to open the playground and send a request:

    ![Send request in the UI](./assets/restate-request.png)

    !!! tip "Durable sessions and retries"
        This request goes through Restate, which persists it before forwarding to your agent. Each session (here `session-1`) is isolated, stateful, and durable. If the agent crashes mid-execution, Restate automatically retries and resumes from the last journaled step, without losing progress.

7. **Inspect the execution journal**

    Click on the Invocations tab and then on your invocation to see the execution journal.

    ![Restate journal in the UI](./assets/restate-journal.png)

    !!! tip "Full control over agent executions"
        Every LLM call and tool execution is recorded in the journal. From the UI, you can pause, resume, restart from any intermediate step, or kill an execution. Check the State tab to inspect your agent's current session data.


## Additional resources

- [Example repository](https://github.com/restatedev/restate-google-adk-example) - Runnable examples including claims processing with human approval
- [Google ADK + Restate tutorial](https://docs.restate.dev/tour/google-adk) - Walkthrough of agent development with Restate and ADK
- [Restate AI documentation](https://docs.restate.dev/ai) - Full reference for durable AI agent patterns
- [Restate SDK on PyPI](https://pypi.org/project/restate-sdk/) - Python package
