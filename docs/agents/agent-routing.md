# Agent routing

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-typescript">TypeScript v1.0.0</span><span class="lst-preview">Experimental</span>
</div>

`RoutedAgent` wraps multiple agents and uses a router function to dynamically
select which one handles each invocation at runtime. This enables agent fallback
on error, A/B testing between agent configurations, planning modes, and
auto-routing by input complexity. If the selected agent fails before producing
any output, the router is called again with error context so it can select a
fallback.

`RoutedAgent` is different from [workflow agents](workflow-agents/index.md)
like `SequentialAgent` or `ParallelAgent`, which orchestrate multiple agents in
a fixed pattern, and from
[LLM-driven delegation](multi-agents.md#b-llm-driven-delegation-agent-transfer),
where the LLM decides which agent to hand off to. With `RoutedAgent`, you write
an explicit routing function that selects **one** agent per invocation. For
model-level routing, see [Model routing](models/model-routing.md).

## How routing works

Both `RoutedAgent` and [`RoutedLlm`](models/model-routing.md) are powered by a
shared routing utility that handles selection and failover.

The router function receives the map of available agents and the current
context, and returns the key of the agent to run. It can be synchronous or
async:

=== "TypeScript"

    ```typescript
    type AgentRouter = (
      agents: Readonly<Record<string, BaseAgent>>,
      context: InvocationContext,
      errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
    ) => Promise<string | undefined> | string | undefined;
    ```

**The `agents` parameter** accepts either a `Record<string, BaseAgent>` with
explicit keys, or an array of agents. If an array is provided, each agent's
`name` property is used as its key.

**Failover behavior:**

- The router is first called without `errorContext` to make the initial
  selection.
- If the selected agent throws an error **before yielding any events**, the
  router is called again with `errorContext` containing `failedKeys` and
  `lastError`.
- If the selected agent throws an error **after yielding events**, the error
  propagates directly without retry, because partial results have already been
  emitted.
- A key that has already been tried cannot be re-selected. If the router returns
  a previously failed key, the error propagates.
- If the router returns `undefined`, routing stops and the last error is thrown.

## Basic usage

Create multiple agents, define a router function that returns a key, and wrap
them in a `RoutedAgent`. The following example routes between two agents based
on an external configuration value that can change between invocations:

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/agent-routing/basic_usage.ts:full"
    ```

Change `config.selectedAgent` to `'agent_b'` before the next invocation to
route to a different agent.

## Fallback on error

When an agent fails, the router is called again with `errorContext` so it can
select a fallback. Failover only applies if the agent fails before yielding
any events (see [How routing works](#how-routing-works)). The following example
checks `errorContext.failedKeys` to avoid re-selecting the failed agent:

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/agent-routing/fallback.ts:config"
    ```

## Planning mode

A router can read any external state to select between agents with different
instructions, models, and tools. This lets you implement a planning mode where
the agent switches behavior dynamically. For example, a basic agent might have
read and write tools, while a planning agent is restricted to read-only access
and uses a more powerful model for analysis.

The following example shows a different `RoutedAgent` configuration. See
[basic usage](#basic-usage) for the full runner setup.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/agent-routing/planning_mode.ts:config"
    ```

Set `planningMode = true` before an invocation to route to the planning agent
with its restricted tool set and different instructions.

## Auto-routing by complexity

The router function can call a lightweight classifier model to categorize input
and route to different agents accordingly. Because the router can be async, you
can make LLM calls inside it before selecting an agent.

The following example shows a different `RoutedAgent` configuration. See
[basic usage](#basic-usage) for the full runner setup.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/agent-routing/auto_routing.ts:config"
    ```
