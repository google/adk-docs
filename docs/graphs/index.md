# Graph-based agent workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

Graph-based agent workflows in ADK let you build agents with more precise control,
creating deterministic processes that combine code logic and AI reasoning
capabilities. Graph-based workflows allow you to define your agent logic as a
graph of execution nodes and edges, combining AI-powered agent reasoning with
deterministic tools and code.

![Graph-based flight upgrade agent](/assets/workflow-design.svg)

**Figure 1.** A graph-based agent design for flight upgrades, combining workflow
nodes of different types, including Functions, human input, Tools, and LLM
capabilities.

Prebuilt ADK [template workflows](/agents/workflow-agents/),
such as [Sequential Agents](/agents/workflow-agents/sequential-agents/),
provide a defined process flow control only across a set of agents. You can continue to
build standard ADK agents with long prompts, tools, and use them in graph-based
workflow agents. When you need more precise control, workflow agent graphs give
you more flexibility over how tasks are routed and executed. Graph-based workflows
provide the following advantages:

-   **Define precise logic:** Explicitly map out routing logic to manage
    transitions between different nodes.
-   **Implement complex structures:** Build agent workflows that support
    branching and state management.
-   **Run chains of functions without AI:** Call agent tools and your own
    code without invoking a generative AI model.
-   **Enhance reliability:** Improve the predictability of your agents by
    relying on structured node definitions rather than prompts alone.

!!! note "Workflow styles in ADK"

    ADK offers three complementary ways to compose multi-step work:

    -   **Graph-based workflows** (this section): a declarative graph of nodes
        and edges with explicit routing — best for deterministic, structured
        processes.
    -   **[Dynamic workflows](/graphs/dynamic/):** programmatic orchestration
        in your own code (loops, conditionals, recursion) — best when the
        control flow is too complex or iterative for a static graph.
    -   **[Prebuilt workflow agents](/agents/workflow-agents/)** (sequential,
        parallel, loop): higher-level building blocks for common patterns
        without assembling a graph yourself.

## Get started

This section describes how to get started with graph-based agents. The following
example shows how to create a sequential graph-based agent workflow that
generates a city name, looks up the current time in that city with a code
function, and the final agent reports the information.

=== "Python"

    ```python
    --8<-- "examples/inline/python/graphs/index/001-get-started.py"
    ```

=== "TypeScript"

    In ADK TypeScript v2.0.0, a `Workflow` takes an `edges` array. Each row
    lists the nodes to run in order. The `node()` function wraps a function,
    an agent, a tool, or another `Workflow` as a graph node, and sets the
    node's name and its `inputSchema` and `outputSchema` contracts. Schemas
    are Zod objects or a genai `Schema`. Each node's return value is passed
    to the next node as its input, so you do not need to write to session
    state.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/index/get_started.ts:get-started"
    ```

=== "Go"

    In ADK Go v2.0.0, sequential workflows use the graph engine:
    `workflow.NewFunctionNode` wraps each step, and `workflow.Chain` wires
    the nodes into a sequential `edges` slice. The framework automatically
    passes each node's typed return value to the next node via
    `event.Output` — no session state writes are needed. The whole graph is
    wrapped in `workflowagent.New`, which produces a standard `agent.Agent`.

    ```go
    --8<-- "examples/go/snippets/graphs/index/main.go:sequential-get-started"
    ```

This sample code demonstrates how you can assemble a simple, sequential
workflow and alternate between agent processing and code execution. While you
could perform these steps using a single agent with a longer prompt and a tool
call, the graph-based approach gives you precise control over the task
execution order and the data output from each step.

For more information about data handling with graph-based workflows, see
[Data handling with workflow nodes and agents](/graphs/data-handling/).

## Build processes with graphs

You can use prompt-based agents to define multiple step processes with
descriptions of tasks and procedures using the instructions field of an ADK
agent. However, as your instructions and procedures become longer and more
complicated, making sure that the agent is following each step and guideline
becomes more complicated and less reliable.

Graph-based workflow agents provide a significant advantage over prompt-based
agents by allowing you to specifically define the overall process workflow in
code. With graph-based agent workflows, each step of the process can be defined
as an execution ***Node*** in a graph and each node can be an AI agent, Tool, or
your programmed code. The following diagram illustrates how a simple
prompt-based agent would translate into a workflow agent graph:

![Prompt-based agent to graph-based workflow](/assets/prompts-to-graphs.svg)

**Figure 2.** Structure of prompt-based agent instructions translated into a
graph-based workflow.

Moving from prompt-based agents to graph-based workflow agents allows you to
explicitly break out the tasks of a procedure to define a specific execution
flow. Once defined, the agent application flows the steps in the graph,
switching between non-deterministic AI-powered agents and deterministic code as
needed.

The following code sample shows how the workflow graph in Figure 2 could be
translated into a graph-based agent:

=== "Python"

    ```python
    --8<-- "examples/inline/python/graphs/index/002-build-processes-with-graphs.py"
    ```

=== "TypeScript"

    In ADK TypeScript v2.0.0, a router node returns an event carrying a
    `route` value, created with `createEvent({route})`. A second edge row
    maps each route value to the node that handles it. Setting `route` to an
    array dispatches to every matching branch, which lets the classifier in
    this example return more than one category. The `DEFAULT_ROUTE` setting
    catches any value that no branch matched.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/index/process_pipeline.ts:process-pipeline"
    ```

=== "Go"

    In ADK Go v2.0.0, conditional routing uses `workflow.NewEmittingFunctionNode`
    to set `event.Routes` and `workflow.StringRoute` edges to dispatch to the
    matching handler — the direct equivalent of Python's `router` function and
    dict dispatch. `workflow.Concat` merges the chain and the conditional edges
    into a single `edges` slice passed to `workflowagent.New`.

    ```go
    --8<-- "examples/go/snippets/graphs/index/main.go:process-pipeline"
    ```

This sample code demonstrates how you can compose a sequence of agents to
define a graph with routes between a set of *nodes*, which are discrete tasks
that can include agents, Tools, your code, and even additional workflow agents.
For information about building advanced pipelines, see
[Build graph routes for workflow agents](/graphs/routes/).

## Known limitations {#known-limitations}

There are some known limitations with graph-based workflows. They
are *not compatible* with the following ADK features:

-   **Integrations:** Some third-party
    [integrations](/integrations/) may not be compatible with graph-based
    workflows.

!!! note "Go: graph workflow API"

    The `workflow` package in ADK Go v2.0.0 is the direct equivalent of the
    Python `Workflow` class. Use `workflow.NewFunctionNode` and
    `workflow.NewAgentNode` to define nodes, `workflow.Chain` or
    `workflow.Concat` with `[]workflow.Edge` to wire them, and
    `workflowagent.New` to wrap the graph as a runnable agent. Conditional
    routing uses `workflow.StringRoute`, `workflow.IntRoute`, or
    `workflow.BoolRoute` matched against `event.Routes`. Fan-in is handled by
    `workflow.NewJoinNode`.

    For advanced routing patterns and fan-out/join examples, see
    [Build graph routes for workflow agents](/graphs/routes/). For prebuilt
    higher-level alternatives (sequential, parallel, loop), see
    [Prebuilt workflow agents](/agents/workflow-agents/).
