# Build graph routes for agent workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

Graph-based workflows in ADK define agent logic as a graph of execution nodes
and edges, allowing you to build more reliable processes that combine artificial
intelligence (AI) reasoning and code logic. These workflows allow you to create
logical routes of execution nodes that can encapsulate code functions,
AI-powered agents, Tools, and human input. By explicitly mapping out routing
logic, this approach allows you to define a specific, step-wise process workflow
in code, providing improved precision and reliability over purely prompt-based
agents.

![Task graph with conditional routing between nodes](/assets/graph-workflow-router.svg)

**Figure 1.** Visualization of a task graph and the routing code to implement it.

=== "Python"

    ```python
    --8<-- "examples/inline/python/graphs/routes/001-build-graph-routes-for-agent-workflows.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/graphs/routes/002-build-graph-routes-for-agent-workflows.ts"
    ```

=== "Go"

    ADK Go v2.0.0 provides the following approach to graph-based
    workflows:

    **Graph engine** (`workflowagent` + `workflow.Edge`): A node-and-edges
    graph API that maps directly to Python's `Workflow(edges=[...])`.
    Nodes are defined with `workflow.NewFunctionNode`, `workflow.NewAgentNode`,
    or `workflow.NewDynamicNode`, edges are declared as `[]workflow.Edge`, and
    the whole graph is wrapped in a `workflowagent.New` call:

    ```go
    --8<-- "examples/inline/go/graphs/routes/003-build-graph-routes-for-agent-workflows.go.txt"
    ```

The advantage of using a graph-based agent workflow is the significant increase
in control, predictability, and reliability over prompt-based agents. By
defining the overall process workflow in code, you gain more control over how
tasks are routed and executed. This structured node definition improves the
predictability of agents and enhances reliability for complex tasks that require
defined steps and process management.

Get started with graph-based workflows in ADK by checking out
[Graph-based agent workflows](/graphs/).

## Nodes

A graph is composed of execution nodes. These *nodes* can be ***Agents***, ADK
***Tools***, human input tasks, or code functions you write. Nodes can take
inputs from previously executed nodes, and emit data through ***Event***
objects.

=== "Python"

    The following shows a simple ***FunctionNode*** that handles text inputs
    and sends a text output:

    ```python
    --8<-- "examples/inline/python/graphs/routes/004-nodes.py"
    ```

=== "TypeScript"

    In ADK TypeScript v2.0.0, the primary node type is a `FunctionNode`,
    created by passing a function to `node()`. A handler always takes
    `(ctx, input)` parameters; ADK does not inject values by parameter name.
    Returning a value directly wraps it in the event's `output` field.
    Returning `createEvent({output})` is the explicit form, which you need
    when you also set `route` or `content`:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/routes/function_node.ts:function-node"
    ```

=== "Go"

    In ADK Go v2.0.0, the primary node type is `workflow.NewFunctionNode`.
    A `FunctionNode` wraps a plain Go function: the function returns a typed
    value, and the framework automatically wraps it in a `session.Event`,
    setting `event.Output`. The successor node receives this value as its
    typed `input` parameter — no manual state writes or event construction
    needed:

    ```go
    --8<-- "examples/go/snippets/graphs/routes/main.go:function-node"
    ```

For more information about transferring data between nodes, see
[Data handling for agent workflows](/graphs/data-handling/).

## Workflow graphs syntax

You define a graph by composing workflow agents. This section provides an
overview of the common routing patterns.

!!! caution "Caution: Workflow agent limitations"

    You can add ***LlmAgents*** to graph-based workflows. However, they must
    be configured for single-turn or task mode. For more information about
    agent modes, see
    [Build collaborative agent teams](/workflows/collaboration/#mode-configuration-and-behaviors).

### Route sequences

A sequential route runs each node once, in the listed order.

=== "Python"

    The `edges` array uses the `START` keyword to indicate the beginning of a
    graph execution, with each listed node executed in sequence:

    ```python
    --8<-- "examples/inline/python/graphs/routes/005-route-sequences.py"
    ```

=== "TypeScript"

    An `edges` row that starts with `'START'` runs each listed node once, in
    order, and passes every node's return value to the next node:

    ```typescript
    --8<-- "examples/inline/typescript/graphs/routes/006-route-sequences.ts"
    ```

    Listing `'START'` in more than one row creates parallel paths instead.
    For more information, see
    [fan out and join](#parallel-tasks-fan-out-and-join-paths).

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/routes/sequence.ts:sequence"
    ```

=== "Go"

    `workflow.Chain(workflow.Start, nodeA, nodeB, nodeC)` wires nodes into a
    sequential edge slice. Each node's typed return value is forwarded to the
    next node via `event.Output` — no session state writes needed:

    ```go
    --8<-- "examples/go/snippets/graphs/routes/main.go:sequential-nodes"
    ```

### Route branches and conditional execution

=== "Python"

    In Python, branching is handled by a `FunctionNode` that returns an
    `Event(route=...)` value, which the `edges` dict dispatches to different nodes.

    ```python
    --8<-- "examples/inline/python/graphs/routes/007-route-branches-and-conditional-execution.py"
    ```

=== "TypeScript"

    Branching requires a node that emits a `route` value, and an edge row
    that maps each route value to the node that handles it. Route values can
    be strings, numbers, or booleans. The `DEFAULT_ROUTE` setting matches
    when no other route on the same source node matches. A branch target can
    be any node-like value: in this example, `taskBNode` is an `LlmAgent`
    and `taskCNode` is a function.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/routes/branches.ts:branches"
    ```

=== "Go"

    In ADK Go v2.0.0, conditional dispatch uses the `workflow` graph engine.
    A node sets `Event.Routes` to one or more string route keys, and each
    `workflow.Edge` selects its successor using a `workflow.Route` matcher:

    -   `workflow.StringRoute("category")` — matches a single string value
    -   `workflow.IntRoute(n)` or `workflow.MultiRoute[int]{1, 2, 3}` — matches
        integer values
    -   `workflow.BoolRoute(true)` — matches a boolean value
    -   `workflow.Default` — matches when no other route on the same source
        node matches

    The following pattern is the Go equivalent of the Python router:

    ```go
    --8<-- "examples/inline/go/graphs/routes/008-route-branches-and-conditional-execution.go.txt"
    ```

    `workflow.EdgeBuilder` provides a fluent alternative to assembling the
    `[]workflow.Edge` slice by hand. The builder's `Add`, `AddFanOut`, and
    `AddFanIn` methods express the same topology with less repetition:

    ```go
    --8<-- "examples/inline/go/graphs/routes/009-route-branches-and-conditional-execution.go.txt"
    ```

    For complete, runnable routing examples see:
    [string routing](https://github.com/google/adk-go/tree/v2/examples/workflow/routing/string),
    [int / multi-value routing](https://github.com/google/adk-go/tree/v2/examples/workflow/routing/int),
    and [LLM-driven routing](https://github.com/google/adk-go/tree/v2/examples/workflow/routing/llm).

    !!! note "Prebuilt agents: encoding routing in state"

        When using `sequentialagent` / `parallelagent` / `loopagent` instead
        of the graph engine, there is no `Event.Routes` dispatch. Encode the
        routing decision in session state via `OutputKey` and let downstream
        agents inspect it in their `Instruction` template, or use a `loopagent`
        with an `Escalate`-based exit — see the
        [loop and escalation example](#loop-and-escalation-exit) below.

## Parallel tasks: fan out and join paths

You can create graphs that split execution across multiple, parallel nodes, and
typically you need to assemble the output of each node for further processing.
This task execution pattern has two stages. The workflow first fans out when it
starts multiple parallel tasks, and then it re-joins those paths when those
tasks are completed before proceeding to the next step.

![Tasks connecting to a JoinNode](/assets/graph-joinnode.svg)

**Figure 2.** The output of parallel task nodes can be assembled and joined
before passing results to the next step.

=== "Python"

    You accomplish the join step by using a ***JoinNode*** object, which waits
    for each parallel task to complete and then passes the collection of outputs
    from these nodes to the next node.

    ```python
    --8<-- "examples/inline/python/graphs/routes/010-parallel-tasks-fan-out-and-join-paths.py"
    ```

=== "TypeScript"

    A `JoinNode` is the fan-in barrier. This logic mechanism waits for every
    predecessor task to complete, and then passes its successor a record
    keyed by predecessor node name:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/routes/fan_out_join.ts:fan-out-join"
    ```

=== "Go"

    ADK Go v2.0.0 provides `workflow.NewJoinNode` for true fan-in in the
    graph engine: fan-out edges from `workflow.Start` (or any shared source
    node) feed in parallel to the join node, which waits for all of them to
    complete before emitting a `map[string]any` keyed by predecessor node name
    to the next node.

    `workflow.EdgeBuilder` makes the fan-out / fan-in wiring concise with its
    dedicated `AddFanOut` and `AddFanIn` helpers (as shown in the
    [complex workflow example](https://github.com/google/adk-go/tree/v2/examples/workflow/complex)):

    ```go
    --8<-- "examples/inline/go/graphs/routes/011-parallel-tasks-fan-out-and-join-paths.go.txt"
    ```

    The following snippet shows the complete fan-out / join pattern using
    `workflow.NewJoinNode` and `EdgeBuilder.AddFanOut` / `AddFanIn`:

    ```go
    --8<-- "examples/go/snippets/graphs/routes/main.go:parallel-fan-out"
    ```

!!! warning "Caution: nodes that feed a JoinNode must produce output"

    A `JoinNode` releases only after all of its predecessor nodes finish.
    Make sure that every node that feeds a join has an output of its own, and attach a
    retry configuration to any node that can fail. A predecessor that
    finishes without an output leaves the join with no value for that
    branch, and the resulting failure appears downstream, away from the node
    that caused it.

## Nested workflows

When building more complex workflows, you may want to encapsulate the
functionality for specific tasks into reusable workflows. One or more
workflow agents can be used as a sub-agent within another workflow agent to
accomplish this goal.

![Nested Workflows inside a parent Workflow](/assets/graph-workflow-nodes.svg)

**Figure 3.** Nested workflow agents as sub-agents inside a parent workflow.

=== "Python"

    ```python
    --8<-- "examples/inline/python/graphs/routes/012-nested-workflows.py"
    ```

    #### Nested workflow data output

    Output for nested Workflow objects works slightly differently from
    individual nodes. When the nested workflow completes one of its nodes, it
    transmits data to the next node in the nested workflow's graph *and* the
    system bubbles up the Event for that node to the parent workflow for
    process traceability. When the nested workflow completes the last node in
    its process, the parent node extracts data from the final leaf nodes and
    emits it as the output of the nested workflow.

=== "TypeScript"

    A `Workflow` is itself a node, so you can use one inside another
    workflow's edges to encapsulate a reusable sub-process:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/routes/nested_workflow.ts:nested-workflow"
    ```

    **Nested workflow data output.** While the inner workflow runs, each of
    its node events bubbles up to the parent for traceability. When it
    finishes, the output of its terminal node becomes the output of the
    nested-workflow node.

=== "Go"

    ADK Go v2.0.0 supports nested workflows in two complementary ways:

    **Graph engine** (`workflowagent` + `workflow.Edge`): A `workflowagent`
    created with `workflowagent.New` is itself an `agent.Agent`, so it can
    be wrapped with `workflow.NewAgentNode` and used as a node inside another
    workflow's `edges` slice. The inner workflow runs to completion as a single
    node from the outer graph's perspective, and its terminal output is emitted
    as the node output on the outer graph's edge:

    ```go
    --8<-- "examples/inline/go/graphs/routes/013-nested-workflows.go.txt"
    ```

    The following snippet shows both the inner and outer graph construction.
    `workflow.NewAgentNode` wraps the inner `workflowagent` so it can be
    placed in the outer graph's `workflow.Chain`:

    ```go
    --8<-- "examples/go/snippets/graphs/routes/main.go:nested-workflows"
    ```

## Loop and escalation exit

A loop repeats a set of steps until a termination condition is met. In Python
this is expressed as a back-edge in the `edges` graph that routes back to an
earlier node. In ADK Go v2.0.0, the graph engine supports the same pattern
directly: add an edge from a downstream node back to an earlier node with a
route condition, and the engine re-activates the target node with a fresh
lifecycle on each iteration.

=== "Python"

    ```python
    --8<-- "examples/inline/python/graphs/routes/014-loop-and-escalation-exit.py"
    ```

=== "TypeScript"

    A loop is a back-edge: a downstream node routes back to an earlier node,
    and the engine re-activates that node with a fresh lifecycle on each
    iteration. The loop exits when the router selects the terminal branch:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/routes/loop_escalation.ts:loop-escalation"
    ```

=== "Go"

    The following example uses the graph engine with `workflow.EdgeBuilder`.
    The critic node returns a verdict, a router node sets `Event.Routes`, and
    a back-edge from the refiner to the critic creates the loop. When the
    critic is satisfied it routes to the terminal `done` node instead:

    ```go
    --8<-- "examples/go/snippets/graphs/routes/main.go:loop-escalate"
    ```

!!! warning "Caution: unbounded graph cycles"

    A graph cycle is not bounded automatically. Make sure the exit condition
    eventually becomes true, or express the iteration as a
    [dynamic workflow](/graphs/dynamic/#loop-route), where the loop runs in
    your own code and you control its bound.
