---
catalog_title: Temporal
catalog_description: Resilient, scalable agents, long-running agents and tools, human approvals, safe versioning, and more using the world's leading durable execution provider.
catalog_icon: /adk-docs/integrations/assets/temporal.svg
---

# Temporal plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Temporal](https://temporal.io) is a durable execution platform that makes ADK
agents resilient, scalable, and production-ready. LLM calls and tool executions
run as Temporal [Activities](https://docs.temporal.io/activities) with automatic
retries and recovery. If anything fails, your agent picks up exactly where it
left off - no manual session management or external database required.

## Use cases

The Temporal plugin gives your agents:

- **Durable execution**: Never lose progress. If your agent crashes or stalls,
  Temporal automatically recovers from the last successful step - no manual
  [session resumption](https://google.github.io/adk-docs/runtime/resume/#resume-a-stopped-workflow)
  required.
- **Built-in retries and rate limiting**: Configurable
  [retry policies](https://docs.temporal.io/encyclopedia/retry-policies) with
  backoff, plus mechanisms for handling backpressure from LLM providers.
- **Long-running and ambient agents**: Support for agents that run for hours,
  days, or indefinitely using blocking awaits and
  [worker versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning).
- **Human-in-the-loop**: Pause execution until a human approves, then resume
  where you left off. Temporal's
  [task routing](https://docs.temporal.io/task-routing) scalably routes incoming
  signals (such as user chats or approvals) to the correct workflow.
- **Long-running tools**: Execute tools that take minutes or hours as
  [Activities](https://docs.temporal.io/activities) with heartbeating, timeouts,
  and retries - no separate microservices needed.
- **Observability and debugging**: Inspect every step of your agent's execution,
  replay workflows deterministically, and pinpoint failures using the
  [Temporal UI](https://docs.temporal.io/web-ui).
- **Safe versioning**: Deploy new agent versions without breaking in-flight
  executions via
  [worker versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning).

## Prerequisites

- Python 3.9+
- A [Gemini API key](https://aistudio.google.com/app/api-keys) (or any
  [supported model](https://google.github.io/adk-docs/agents/models/))
- A running Temporal server
  ([local dev server](https://docs.temporal.io/cli#start-dev-server),
  [self-hosted](https://docs.temporal.io/self-hosted-guide), or
  [Temporal Cloud](https://temporal.io/cloud))

## Installation

Install the Temporal Python SDK:

```bash
pip install temporalio
```

Install ADK:

```bash
pip install google-adk
```

## Use with agent

### Basic setup

The integration has two sides: the **workflow side** (where your agent runs) and
the **worker side** (which hosts the execution environment).

**1. Define your agent and workflow**

Create an ADK agent and wrap it in a Temporal Workflow. Use `TemporalModel` to
route LLM calls through Temporal Activities:

```python
from datetime import timedelta
from google.adk.agents import Agent
from temporalio import workflow
from temporalio.contrib.google_adk_agents import TemporalModel

# Create an agent with a Temporal-aware model
agent = Agent(
    name="weather_agent",
    model=TemporalModel("gemini-2.5-pro"),
    instruction="You are a helpful weather assistant.",
    tools=[get_weather],  # your tool functions
)

@workflow.defn
class WeatherAgentWorkflow:
    @workflow.run
    async def run(self, user_message: str) -> str:
        # Run the ADK agent inside a Temporal Workflow
        runner = InMemoryRunner(agent=agent)
        result = await runner.run_async(user_message)
        return result
```

**2. Configure and start the worker**

Use `TemporalAdkPlugin` to configure the worker to make ADK ready to run in a Workflow on a distributed system:

```python
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.contrib.google_adk_agents import TemporalAdkPlugin

async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="adk-task-queue",
        workflows=[WeatherAgentWorkflow],
        plugins=[TemporalAdkPlugin()],
    )
    await worker.run()

asyncio.run(main())
```

**3. Start a workflow execution**

```python
from temporalio.client import Client

async def start():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        WeatherAgentWorkflow.run,
        "What's the weather in San Francisco?",
        id="weather-agent-1",
        task_queue="adk-task-queue",
    )
    print(result)
```

### Using custom tools as Activities

Wrap Temporal Activities as ADK tools using `activity_tool`, so tool executions
get full retry and timeout guarantees:

```python
from datetime import timedelta
from temporalio import activity
from temporalio.contrib.google_adk_agents.workflow import activity_tool
from temporalio.workflow import ActivityConfig

@activity.defn
async def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Your weather API call here
    return f"72°F and sunny in {city}"

# Wrap the activity as an ADK tool
weather_tool = activity_tool(
    get_weather,
    start_to_close_timeout=timedelta(seconds=30),
    retry_policy=RetryPolicy(maximum_attempts=3),
)

# Use in your agent
agent = Agent(
    name="weather_agent",
    model=TemporalModel("gemini-2.5-pro"),
    tools=[weather_tool],
)
```

### Using MCP tools

Execute [MCP](https://google.github.io/adk-docs/mcp/) tools as Temporal
Activities:

```python
from temporalio.contrib.google_adk_agents import (
    TemporalAdkPlugin,
    TemporalMcpToolSet,
    TemporalMcpToolSetProvider,
)

# Define a factory for your MCP toolset
provider = TemporalMcpToolSetProvider("my-tools", my_toolset_factory)

# Use in your agent workflow
agent = Agent(
    name="tool_agent",
    model=TemporalModel("gemini-2.5-pro"),
    toolsets=[TemporalMcpToolSet("my-tools")],
)

# Configure the worker with the toolset provider
worker = Worker(
    client,
    task_queue="adk-task-queue",
    workflows=[ToolAgentWorkflow],
    plugins=[TemporalAdkPlugin(toolset_providers=[provider])],
)
```

## How it works

The plugin ensures your ADK agent runs deterministically inside Temporal:

- **LLM calls** are executed as Temporal Activities via `TemporalModel`. If a
  call fails or the worker crashes, Temporal retries or replays from the last
  successful step, adding resilience and reducing token spend.
- **Non-deterministic operations** When run in Workflow code (as opposed to Activity code), 
  (`time.time()`, `uuid.uuid4()`) are
  automatically replaced with Temporal's deterministic equivalents
  (`workflow.now()`, `workflow.uuid4()`).
- **ADK and Gemini modules** are configured for Temporal's
  [sandbox](https://docs.temporal.io/develop/python/sandbox-environment)
  environment with automatic passthrough.
- **Pydantic serialization** is configured automatically for ADK's data types.

## Capabilities

| Capability | Description |
| --- | --- |
| Durable LLM calls | `TemporalModel` executes model invocations as Activities with configurable timeouts and automatic retries |
| Durable tool execution | `activity_tool` wraps tool functions as Activities, supporting long-running tools, automatic retries, and heartbeating |
| MCP tool support | `TemporalMcpToolSet` executes MCP tools as Activities with full event propagation |
| Human-in-the-loop | Your Agent Workflow can wait for [Signals](https://docs.temporal.io/signals) and [Updates](https://docs.temporal.io/messages#updates) to wait for human input, and clients can send those to resume the Agent |
| Deterministic runtime | `TemporalAdkPlugin` replaces non-deterministic calls with Temporal-safe equivalents |
| Debuggability | Every LLM call and tool execution is visible as an Activity in the Temporal UI, making it trivial to debug faults. |
| Observability | Work with your favorite Observability solution using OpenTelemetry, with cross-process spans that are resilient to crashes.
| Safe versioning | Deploy new agent versions using [Temporal Worker Versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning) without disrupting in-flight executions |
| Multi-agent orchestration | Compose multiple agents within a Workflow, or scale them to more complex use cases by using [Child Workflows](https://docs.temporal.io/child-workflows) or [Nexus](https://docs.temporal.io/nexus) |

## Additional resources

- [Temporal Python SDK documentation](https://docs.temporal.io/develop/python) -
  Full reference for Temporal's Python SDK
- [Temporal Python SDK on PyPI](https://pypi.org/project/temporalio/) - Python
  package
- [Temporal Cloud](https://temporal.io/cloud) - Managed Temporal service
- [Orchestrating ambient agents with Temporal](https://temporal.io/blog/orchestrating-ambient-agents-with-temporal) -
  Blog post on long-running agent patterns
