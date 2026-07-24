# DBOS plugin for ADK

Supported in ADKPython

[DBOS](https://dbos.dev) is a durable execution framework for building reliable workflows and AI agents. It integrates with ADK to make LLM calls, tool executions, and agent orchestration fault-tolerant and scalable. Agents resume exactly where they left off after crashes, deploys, or restarts — all backed by a database you own, with no separate orchestration service required.

## Use cases

The DBOS plugin adds production-grade reliability and orchestration to ADK agents:

- **Durable execution**: Persist LLM and tool outputs. Automatically recover agents from crashes, deploys, or machine failures without losing progress or duplicating side effects. No manual [session resumption](/runtime/resume/#resume-a-stopped-workflow) required.
- **Built-in retries and backoff**: Configurable retry policies with exponential backoff to handle transient failures from LLM providers and tool executions.
- **Long-running agents**: Run agents and tools for hours, days, or months.
- **Human-in-the-loop**: Pause execution and resume it later after receiving an external signal or human approval.
- **Scalable execution with rate limiting**: Compose multiple agents within a workflow, or scale agent workflows across distributed workers with durable queues and built-in rate limiting.
- **Observability and management**: Inspect, cancel, resume, and fork agent workflows from the [DBOS Console](https://docs.dbos.dev/production/workflow-management).

## Prerequisites

- Python 3.10+
- A [Gemini API key](https://aistudio.google.com/app/api-keys) (or any [supported model](/agents/models/))

## Installation

```bash
pip install dbos-google-adk
```

## Use with agent

The integration wraps your ADK agent so each LLM call runs as a durable DBOS workflow step. Tool functions decorated with `@DBOS.step()` are checkpointed individually with configurable retries.

### Basic setup

Define your agent and workflow by adding `DBOSPlugin` to your `Runner`, and driving the agent from a `@DBOS.workflow()`:

```python
import asyncio
import logging

from dbos import DBOS, DBOSConfig
from dbos_google_adk import DBOSPlugin
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Decorate tool calls with @DBOS.step() for durable execution
@DBOS.step()
async def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"Sunny in {city}"

agent = LlmAgent(name="weather", model="gemini-flash-latest", tools=[get_weather])
runner = Runner(
    app_name="my-agent",
    agent=agent,
    plugins=[DBOSPlugin()],
    session_service=InMemorySessionService(),
)

# Drive the agent from a DBOS workflow for durable execution
@DBOS.workflow()
async def run_agent(user_id: str, session_id: str, message: str) -> str:
    new_message = types.Content(role="user", parts=[types.Part.from_text(text=message)])
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=new_message
    ):
        if event.is_final_response():
            return event.content.parts[0].text
    return ""


async def main():
    # DBOS checkpoints to SQLite by default. Postgres is recommended for production.
    config: DBOSConfig = {"name": "my-agent", "system_database_url": "sqlite:///dbostest.sqlite"}
    DBOS(config=config)
    DBOS.launch()

    await runner.session_service.create_session(
        app_name="my-agent", user_id="u", session_id="s"
    )
    print(await run_agent("u", "s", "How is the weather in San Francisco?"))


if __name__ == "__main__":
    asyncio.run(main())
```

### Durable event compaction

For durable event compaction, wrap your summarizer with `DBOSEventSummarizer` so compaction LLM calls are also checkpointed:

```python
from dbos_google_adk import DBOSEventSummarizer
from google.adk.models.google_llm import Gemini

summarizer = DBOSEventSummarizer.from_llm(Gemini(model="gemini-flash-latest"))
```

## How it works

`DBOSPlugin` and `DBOSEventSummarizer` run your ADK agent inside a durable DBOS workflow:

- **LLM calls** are intercepted by `DBOSPlugin` and executed as DBOS steps. If a call fails or the worker crashes, DBOS resumes from the last successful step, reducing wasted token spend.
- **Tool functions** decorated with `@DBOS.step()` are checkpointed individually. Their outputs are stored in the database, so replays skip already-completed tool executions entirely.
- **Workflow execution** is serialized and stored in your database (SQLite or Postgres) after every step. Any worker process with access to the same database can take over execution, enabling distributed failover and horizontal scaling.

## Capabilities

| Capability                            | Description                                                                                                                                                                                                                          |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Durable tool execution                | In addition to LLM calls, tool functions decorated with `@DBOS.step()` are checkpointed in the database with configurable retries on failure                                                                                         |
| Failure recovery                      | DBOS resumes in-flight workflows from the last successful step on process restart, or automatic fail-over in a distributed setting with [DBOS Conductor](https://docs.dbos.dev/production/conductor)                                 |
| Parallel tool calls                   | Multiple tool calls from a single LLM response are dispatched concurrently with replay safety, and joined before the next LLM step                                                                                                   |
| Debugging                             | Replay any past workflow execution step-by-step. Fork and restart a workflow from a specific step for bug fixes                                                                                                                      |
| Long-running agents                   | Workflows can run for hours, days, or months; state stays in the database until completion                                                                                                                                           |
| Observability                         | Every LLM call and tool execution is a recorded step, visible in the [DBOS Console](https://docs.dbos.dev/production/workflow-management) dashboard or via OpenTelemetry                                                             |
| Human-in-the-loop                     | Pause execution and resume it later after receiving an external signal or human approval via DBOS [workflow notifications](https://docs.dbos.dev/python/tutorials/workflow-communication#workflow-messaging-and-notifications)       |
| Scalable execution with rate limiting | Compose multiple agents within a workflow, or execute agent workflows across distributed workers using [durable queues](https://docs.dbos.dev/python/tutorials/queue-tutorial). Built-in rate limiting for handling API backpressure |
| Safe versioning                       | Upgrade and deploy new agent versions using [DBOS patching or versioning](https://docs.dbos.dev/python/tutorials/upgrading-workflows) without disrupting in-flight executions                                                        |

## Additional resources

- [DBOS Python documentation](https://docs.dbos.dev/python/programming-guide) - Full reference for DBOS workflows, steps, and queues
- [dbos-google-adk on PyPI](https://pypi.org/project/dbos-google-adk/) - Python package
- [DBOS GitHub repository](https://github.com/dbos-inc/dbos-transact-py) - Source code and examples
- [DBOS Discord](https://discord.gg/eMUHrvbu67) - Questions and community discussion
