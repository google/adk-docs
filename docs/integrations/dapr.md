---
catalog_title: Dapr
catalog_description: Durable, long-running and self-recovering agents with human approvals and safe versioning
catalog_icon: /integrations/assets/dapr.png
catalog_tags: ["resilience"]
---

# Dapr plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Dapr](https://dapr.io) is a distributed workflow orchestration engine that
makes ADK agents resilient to failures. LLM calls and tool executions run as
Dapr
[Workflow](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/)
activities with automatic retries and recovery. If anything fails, your agent
automatically picks up exactly where it left off.

## Use cases

The Dapr plugin gives your agents:

- **Durable execution**: Never lose progress. If your agent crashes or stalls,
  Dapr automatically recovers from the last successful activity with no need to
  [manually resume](/runtime/resume/#resume-a-stopped-workflow).
- **Built-in retries and backoff**: Configurable [retry
  policies](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#retry-policies)
  with exponential backoff to handle transient failures from LLM providers and
  tool APIs.
- **Long-running and ambient agents**: Support for agents and tools that run for
  hours, days, or indefinitely, backed by Dapr's persistent state stores.
- **Portable infrastructure**: Swap 15+ databases (Redis, GCP Firestore,
  PostgreSQL, DynamoDB, Cosmos DB, and [many
  more](https://docs.dapr.io/reference/components-reference/supported-state-stores/))
  without changing agent code. Dapr's pluggable component model lets you move
  from local dev to any cloud.
- **Observability and debugging**: Inspect every step of your agent's execution
  using Dapr's workflow APIs, and emit traces and metrics through Dapr's
  built-in [OpenTelemetry
  integration](https://docs.dapr.io/operations/observability/tracing/tracing-overview/).

## Prerequisites

- Python 3.11+
- A [Gemini API key](https://aistudio.google.com/app/api-keys) (or any
  [supported model](/agents/models/))
- Dapr CLI and runtime installed ([install
  guide](https://docs.dapr.io/getting-started/install-dapr-cli/))
- A configured Dapr [state store
  component](https://docs.dapr.io/reference/components-reference/supported-state-stores/)
  for workflow persistence

## Installation

Install the [Diagrid Agent package](https://pypi.org/project/diagrid/) for Dapr,
which includes the ADK extension:

```bash
pip install diagrid
```

Initialize Dapr:

```bash
dapr init
```

## Use with agent

### Basic setup

The integration wraps your ADK agent so each LLM call and each tool execution
runs as a durable Dapr Workflow activity. The runner handles workflow
registration, starts the Dapr workflow runtime, and exposes an async interface
for invoking the agent.

**Define your agent and runner**

Create an ADK agent as usual and pass it to `DaprWorkflowAgentRunner`.

```python
import asyncio
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from diagrid.agent.adk import DaprWorkflowAgentRunner


def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The name of the city to get weather for.

    Returns:
        A string describing the weather.
    """
    # Your weather API call here
    return f"72°F and sunny in {city}"


# Define the ADK agent
agent = LlmAgent(
    name="weather_agent",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant that can check the weather.",
    tools=[FunctionTool(get_weather)],
)


async def main():
    # Wrap the agent so each tool call runs as a durable Dapr activity
    runner = DaprWorkflowAgentRunner(
        agent=agent,
        name="weather-agent",
        max_iterations=10,
    )

    # Start the Dapr Workflow runtime
    runner.start()

    try:
        async for event in runner.run_async(
            user_message="What's the weather in San Francisco?",
            session_id="session-001",
        ):
            if event["type"] == "workflow_completed":
                print(event["final_response"])
    finally:
        runner.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
```

**Run the agent with Dapr**

Dapr Workflow uses a lightweight sidecar and a configured state store. Use this
command to run Dapr locally and your agent alongside it:

```bash
dapr run --app-id weather-agent -- python3 agent.py
```

!!! note

    By default Dapr uses the Redis component installed with Dapr, located at
    `~/.dapr/components/statestore.yaml`. See [supported state
    stores](https://docs.dapr.io/reference/components-reference/supported-state-stores/)
    to change the state store used.

### Crash recovery

If the process hosting your agent crashes mid-execution, Dapr automatically
resumes the workflow from the last successful activity when the app restarts -
no custom replay logic required.

```python
# First run: process crashes after tool 1 completes.
# Second run: Dapr automatically resumes and executes tools 2 and 3.
runner = DaprWorkflowAgentRunner(agent=agent, name="sequential-agent")
runner.start()

async for event in runner.run_async(
    user_message="Run the three-step pipeline.",
    session_id="pipeline-001",
):
    if event["type"] == "workflow_completed":
        print(event["final_response"])
```

Because the `session_id` and workflow instance ID are stable, relaunching the
same app with Dapr causes the sidecar to pick up in-flight workflows and drive
them to completion, without needing to manually resume.

## How it works

The plugin turns an ADK agent loop into a Dapr Workflow so that each step is
checkpointed, retried, and automatically replayable:

- **LLM calls** are executed as Dapr Workflow
  [activities](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#workflow-activities).
  If a call fails or the worker crashes, Dapr retries according to the
  configured retry policy or replays the workflow from the last successful
  activity, adding resilience and reducing token spend.
- **Tool executions** are run as independent activities, one per tool call. The
  workflow fans out parallel tool calls via Dapr's `when_all` primitive and
  waits for them to complete before re-invoking the LLM.
- **Workflow state** (messages, tool calls, tool results) is serialized and
  stored in the configured Dapr state store after every activity, so any replica
  with access to the state store can take over execution.
- **Deterministic orchestration**: the `agent_workflow` function contains only
  deterministic control flow; all side effects (LLM calls, tool invocations)
  happen inside activities, which is the model Dapr Workflow requires for replay
  safety.

## Capabilities

| Capability | Description |
| --- | --- |
| Durable tool execution | Each ADK tool runs as a Dapr Workflow activity, with automatic retries, backoff, and replay on failure |
| Parallel tool calls | Multiple tool calls from a single LLM response are dispatched concurrently as activities and joined before the next LLM step |
| Portable state stores | Swap between Redis, GCP Firestore, PostgreSQL, Cosmos DB, and many others via Dapr components without code changes |
| Long-running agents | Workflows can run for hours, days, or indefinitely; state stays in the Dapr state store until completion |
| Observability | Every LLM call and tool execution is a workflow activity, traceable via Dapr's OpenTelemetry integration and inspectable through the workflow API |
| Kubernetes-native | Deploy the same agent to Kubernetes without code changes using Dapr's sidecar injection |

## Additional resources

- [Dapr Workflow documentation](https://docs.dapr.io/developing-applications/building-blocks/workflow/) - Full reference for Dapr's workflow building block
- [Diagrid Agent SDK on GitHub](https://github.com/diagridio/python-ai) - Source code for the Dapr ADK integration
- [Dapr Community Discord](https://bit.ly/dapr-discord) - Questions, bug reports, and community discussion
- [Supported state stores](https://docs.dapr.io/reference/components-reference/supported-state-stores/) - List of state store components compatible with Dapr Workflow
