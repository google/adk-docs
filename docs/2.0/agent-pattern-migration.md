# Migrate ADK 1.x workflow agents to Workflow

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.0.0</span>
</div>

ADK 1.x projects often used ***SequentialAgent***, ***ParallelAgent***, and
***LoopAgent*** to compose multi-step pipelines. On adk-python `main`, these
classes are `@deprecated` in favor of ***Workflow***.

This page maps those **agent patterns** to Workflow equivalents. It does **not**
repeat ADK 2.0 **runtime** breaking changes (event schema, session storage,
callback contracts). Review those in the [ADK 2.0 overview](index.md) before
upgrading production apps.

## When to migrate

| Situation | Recommendation |
|---|---|
| Greenfield ADK 2.x project | Use ***Workflow*** and graph guides from the start |
| Existing 1.x app with template workflow agents | Follow the table below |
| Not ready for 2.0 runtime changes | Stay on `google-adk~=1.0` (see [Installing ADK Python 1.x](index.md#install)) |

All three deprecated agents carry the same note: Workflow cannot yet be used as
an `LlmAgent` sub-agent. The supported replacement for nested pipelines is
**Workflow-as-Tool** (ADK Python 2.4+). See [Nested pipelines](#nested-pipelines-workflow-as-tool).

## Pattern mapping

| ADK 1.x pattern | ADK 2 direction | Sample |
|---|---|---|
| `SequentialAgent` (fixed order) | `Workflow` with sequential `edges` | [`sequence`](https://github.com/google/adk-python/tree/main/contributing/samples/workflows/sequence) |
| `ParallelAgent` fan-out + gather | `Workflow` + `JoinNode` | [`fan_out_fan_in`](https://github.com/google/adk-python/tree/main/contributing/samples/workflows/fan_out_fan_in) |
| `LoopAgent` / generator-critic | `Workflow` conditional loop | [`loop`](https://github.com/google/adk-python/tree/main/contributing/samples/workflows/loop) |
| `SequentialAgent` as `sub_agent` | **Workflow-as-Tool** on `Agent(tools=[...])` | [`node_as_tool`](https://github.com/google/adk-python/tree/main/contributing/samples/workflows/node_as_tool) |

Legacy 1.x samples live under
[`legacy_workflows/`](https://github.com/google/adk-python/tree/main/contributing/samples/legacy_workflows)
for side-by-side comparison.

## SequentialAgent to Workflow

***SequentialAgent*** runs `sub_agents` in list order with no LLM routing. In
ADK 2, model the same fixed pipeline as a ***Workflow*** graph.

=== "Before (1.x)"

    ```python
    from google.adk.agents import SequentialAgent, LlmAgent

    step_a = LlmAgent(name="step_a", ...)
    step_b = LlmAgent(name="step_b", ...)

    pipeline = SequentialAgent(
        name="pipeline",
        sub_agents=[step_a, step_b],
    )
    ```

=== "After (2.x)"

    ```python
    from google.adk import Agent, Workflow

    step_a = Agent(name="step_a", ...)
    step_b = Agent(name="step_b", ...)

    pipeline = Workflow(
        name="pipeline",
        edges=[("START", step_a, step_b)],
    )
    ```

Read [Graph-based workflows](../graphs/index.md) for node types and execution
semantics. Runnable sample:
[`workflows/sequence`](https://github.com/google/adk-python/tree/main/contributing/samples/workflows/sequence).

## ParallelAgent to Workflow and JoinNode

***ParallelAgent*** runs branches concurrently, often followed by a gather step
inside a ***SequentialAgent***. In ADK 2, fan out with a tuple of nodes in
`edges`, synchronize with a ***JoinNode***, then pass a combined `dict` to the
next node.

=== "Concept (2.x)"

    ```python
    from google.adk import Workflow
    from google.adk.workflow import JoinNode

    join_node = JoinNode(name="join_for_results")

    pipeline = Workflow(
        name="parallel_pipeline",
        edges=[
            (
                "START",
                (branch_a, branch_b, branch_c),
                join_node,
                aggregate,
            ),
        ],
    )
    ```

The node after `JoinNode` receives `dict[str, Any]` keyed by upstream node name.
See [Parallel tasks: fan out and join paths](../graphs/routes.md#parallel-tasks-fan-out-and-join-paths) and sample
[`fan_out_fan_in`](https://github.com/google/adk-python/tree/main/contributing/samples/workflows/fan_out_fan_in).

## LoopAgent to Workflow loops

***LoopAgent*** repeats sub-agents until escalation or `max_iterations`. In ADK
2, express iteration with conditional routing: a routing node yields an
`Event(route=...)`, and `edges` map that route back to an earlier node.

For human-in-the-loop inside a loop, nodes can yield ***RequestInput***. See
[Dynamic workflows](../graphs/dynamic.md) and
[Human input](../graphs/human-input.md).

| Use case | Sample |
|---|---|
| Generator / critic loop | [`loop`](https://github.com/google/adk-python/tree/main/contributing/samples/workflows/loop) |
| Pause for approval mid-loop | [`request_input`](https://github.com/google/adk-python/tree/main/contributing/samples/workflows/request_input) |
| Config-driven loop agents | [`loop_config`](https://github.com/google/adk-python/tree/main/contributing/samples/workflows/loop_config) |

## Nested pipelines: Workflow-as-Tool

A common 1.x pattern nests a deterministic pipeline under a coordinator:

```python
root = Agent(
    name="orchestrator",
    sub_agents=[pipeline],  # SequentialAgent or similar
)
```

`Workflow` is a ***BaseNode***, not a ***BaseAgent***, so
`sub_agents=[workflow]` raises a type error. This is intentional: maintainers
closed [adk-python#5872](https://github.com/google/adk-python/issues/5872) with
**Workflow-as-Tool** as the supported path (shipped in ADK Python 2.4.0).

### Workflow-as-Tool (recommended)

Pass the workflow into the parent agent's `tools` list. ADK wraps it as a
callable tool. The parent LLM decides **when** to invoke the pipeline (unlike a
deterministic `sub_agent` step).

=== "After (2.x)"

    ```python
    from google.adk import Agent, Workflow
    from pydantic import BaseModel, Field

    class PipelineArgs(BaseModel):
        task: str = Field(description="Task for the pipeline to run.")

    pipeline = Workflow(
        name="pipeline",
        description="Runs research then summary for a given task.",
        input_schema=PipelineArgs,
        edges=[("START", research, summary)],
    )

    root = Agent(
        name="orchestrator",
        tools=[pipeline],
        ...
    )
    ```

Requirements:

- Set `description` on the workflow (required; otherwise ADK raises
  `ValueError`).
- Set `input_schema` when the tool needs structured arguments.

Full sample with HITL inside a node tool:
[`node_as_tool`](https://github.com/google/adk-python/tree/main/contributing/samples/workflows/node_as_tool).

### What is not supported yet

- **Workflow as `sub_agent`:** still tracked in
  [adk-python#5581](https://github.com/google/adk-python/discussions/5581).
- **Manual BaseAgent bridge:** wrapping `Workflow.run()` inside
  `_run_async_impl` works only for single-turn, non-HITL pipelines. Prefer
  Workflow-as-Tool for new code.

!!! note "Template workflow docs"

    The [Sequential](../agents/workflow-agents/sequential-agents.md),
    [Parallel](../agents/workflow-agents/parallel-agents.md), and
    [Loop](../agents/workflow-agents/loop-agents.md) template guides describe
    the 1.x API. Each page notes that graph-based workflows supersede them in
    ADK 2.0.

## Related reading

- [ADK 2.0 overview](index.md): runtime migration (events, callbacks, retries)
- [Graph-based workflows](../graphs/index.md)
- [Collaborative workflows](../workflows/collaboration.md)
- [Multi-agent workflow patterns](../workflows/patterns.md)
- [All Workflow samples](https://github.com/google/adk-python/tree/main/contributing/samples/workflows)
