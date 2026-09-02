---
catalog_title: Temporal
catalog_description: Resilient, scalable agents, long-running agents and tools, human approvals, and safe versioning
catalog_icon: /integrations/assets/temporal.png
catalog_tags: ["resilience"]
---

# Temporal plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Temporal](https://temporal.io) is a general-purpose durable execution platform
that makes ADK agents resilient, scalable, and production-ready. LLM calls and
tool executions run as Temporal
[Activities](https://docs.temporal.io/activities) with automatic retries and
recovery. If anything fails, your agent picks up exactly where it left off - no
manual session management or external database required.

## Use cases

The Temporal plugin gives your agents:

- **Durable execution**: Never lose progress. If your agent crashes or stalls,
  Temporal automatically recovers from the last successful step - no manual
  [session resumption](/runtime/resume/#resume-a-stopped-workflow)
  required.
- **Built-in retries and rate limiting**: Configurable
  [retry policies](https://docs.temporal.io/encyclopedia/retry-policies) with
  backoff, plus mechanisms for handling backpressure from LLM providers.
- **Long-running and ambient agents**: Support for agents and tools that run for hours,
  days, or indefinitely using blocking awaits.
- **Human-in-the-loop**: Pause execution until a human approves, then resume
  where you left off. Temporal's
  [task routing](https://docs.temporal.io/task-routing) scalably routes incoming
  signals (such as user chats or approvals) to the correct workflow.
- **Observability and debugging**: Inspect every step of your agent's execution,
  replay workflows deterministically, and pinpoint failures using the
  [Temporal UI](https://docs.temporal.io/web-ui).

## Prerequisites

- Python 3.10+
- A [Gemini API key](https://aistudio.google.com/app/api-keys) (or any
  [supported model](/agents/models/))
- A running Temporal server
  ([local dev server](https://docs.temporal.io/cli#start-dev-server),
  [self-hosted](https://docs.temporal.io/self-hosted-guide), or
  [Temporal Cloud](https://temporal.io/cloud))
- Temporal Python SDK [1.24.0](https://github.com/temporalio/sdk-python/releases/tag/1.24.0)

Note that as of Temporal Python 1.24.0, this integration is experimental and
there may be future breaking changes.

## Installation

Install the Temporal Python SDK along with the google-adk extra:

```bash
pip install "temporalio[google-adk]"
```

## Use with agent

### Basic setup

The integration has two sides: the **workflow side** (where your agent runs) and
the **worker side** (which hosts the execution environment).

**1. Define your agent and workflow**

Create an ADK agent and wrap it in a Temporal Workflow. Use `TemporalModel` to
route LLM calls through Temporal Activities.

```python
--8<-- "examples/inline/python/integrations/temporal/001-basic-setup.py"
```

**2. Configure and start the worker**

Use `GoogleAdkPlugin` to configure the worker to make ADK ready to run in a
Workflow on a distributed system:

```python
--8<-- "examples/inline/python/integrations/temporal/002-drop-your-agent-in-a-workflow-to-give-it.py"
```

**3. Start a workflow execution**

```python
--8<-- "examples/inline/python/integrations/temporal/003-drop-your-agent-in-a-workflow-to-give-it.py"
```

### Using MCP tools

Execute [MCP](/mcp/) tools as Temporal
Activities:

```python
--8<-- "examples/inline/python/integrations/temporal/004-using-mcp-tools.py"
```

### Local development with `adk web`

For ease of local development, the Temporal wrappers automatically fall back to
direct execution when run outside a Temporal Workflow, so you can use `adk web`
and other ADK development commands without a running Temporal server. You won't
get the benefits of durable execution in this mode, nor will you be precisely
testing the production behavior.

- `TemporalModel` and `activity_tool` work automatically — they detect they're
  outside a workflow and call the underlying LLM or function directly.
- `TemporalMcpToolSet` requires the `not_in_workflow_toolset` parameter (shown
  in the MCP example above) so it knows how to instantiate the toolset locally.

## How it works

The plugin ensures your ADK agent runs deterministically inside Temporal
Workflow code, and causes inputs and outputs to be serialized and recorded for
robust recovery. For example:

- **LLM calls** are executed as Temporal Activities via `TemporalModel`. If a
  call fails or the worker crashes, Temporal retries or replays from the last
  successful step, adding resilience and reducing token spend.
- **Non-deterministic operations** like (`time.time()`, `uuid.uuid4()`) are
  automatically replaced with Temporal's deterministic equivalents
  (`workflow.now()`, `workflow.uuid4()`) when run in Workflow code (but not Activity code).
- **ADK and Gemini modules** are configured for Temporal's
  [sandbox](https://docs.temporal.io/develop/python/best-practices/python-sdk-sandbox)
  environment with automatic passthrough.
- **Pydantic serialization** is configured automatically for ADK's data types.

## Additional capabilities

| Capability | Description |
| --- | --- |
| Durable tool execution | `activity_tool` wraps tool functions as Activities, supporting long-running tools, automatic retries, and heartbeating |
| MCP tool support | `TemporalMcpToolSet` executes MCP tools as Activities with full event propagation |
| Human-in-the-loop | Your Agent Workflow can wait for [Signals](https://docs.temporal.io/sending-messages#sending-signals) and [Updates](https://docs.temporal.io/sending-messages#sending-updates) to wait for human input, and clients can send those to resume the Agent |
| Deterministic runtime | `GoogleAdkPlugin` replaces non-deterministic calls with Temporal-safe equivalents |
| Debuggability | Every LLM call and tool execution is visible as an Activity in the Temporal UI, making it trivial to debug faults. |
| Observability | Work with your favorite Observability solution using OpenTelemetry, with cross-process spans that are resilient to crashes. |
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
