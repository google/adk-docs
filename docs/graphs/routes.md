# Build graph routes for agent workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.0.0</span><span class="lst-go">Go v2.0.0</span>
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
    root_agent = Workflow(
      name="routing_workflow",
      edges=[
        ("START", process_message, router),
        (router,
          {
            "output-1": response_1,
            "output-2": response_2,
            "output-3": response_3,
          },
        ),
      ],
    )
    ```

=== "Go"

    In ADK Go, workflow graphs are expressed through three composable workflow
    agent types rather than an `edges` array DSL. Each type maps to a common
    graph topology:

    | Graph topology | Go workflow agent |
    |---|---|
    | Ordered sequence of nodes | `sequentialagent` |
    | Parallel fan-out across nodes | `parallelagent` |
    | Repeated execution / loop with exit condition | `loopagent` |

    Agents are composed by nesting them in each other's `SubAgents` field.
    Data flows between steps through session state: a step writes its output
    to a named key with `llmagent.Config.OutputKey`, and downstream steps
    read it by referencing `{key}` in their `Instruction` template.

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
    from google.adk import Event

    def my_function_node(node_input: str):
        input_text_modified = node_input.upper()
        return Event(output=input_text_modified)
    ```

=== "Go"

    In Go, a workflow step (node) is an `agent.Agent` whose `Run` function
    yields `*session.Event` values. The following custom `Run` function acts
    as a node that transforms its input and writes the result to session state:

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
    be configured for single-turn mode (`ModeSingleTurn`). For more information about
    agent modes, see
    [Build collaborative agent teams](/workflows/collaboration/#mode-configuration-and-behaviors).

### Route sequences

A sequential route runs each node once, in the listed order.

=== "Python"

    The `edges` array uses the `START` keyword to indicate the beginning of a
    graph execution, with each listed node executed in sequence:

    ```python
    edges=[("START", task_A_node)]  # single node run
    edges=[("START",
            task_A_node,
            task_B_node,
            task_C_node)]           # 3 nodes run in order
    ```

=== "Go"

    `sequentialagent.New` accepts a list of `SubAgents` and runs them in the
    listed order — one after another, passing session state between steps:

    ```go
    --8<-- "examples/go/snippets/graphs/routes/main.go:sequential-nodes"
    ```

### Route branches and conditional execution

In Python, branching is handled by a `FunctionNode` that returns an
`Event(route=...)` value, which the `edges` dict dispatches to different nodes.

=== "Python"

    ```python
    def router(node_input: str):
        """Route to task B or C based on node_input."""
        if condition(node_input):
            return Event(route="RUN_TASK_C")
        return Event(route="RUN_TASK_B")

    task_B_node = Agent(name="task_B_agent") # An agent to execute node B

    def task_C_node(node_input: str):
        """A FunctionNode to execute node C."""
        return Event(output="Task C completed")

    root_agent = Workflow(
        name="routing_workflow",
        edges=[
            ("START", task_A_node, router),
            (router,
              {
                # "route value": node_to_run
                "RUN_TASK_B": task_B_node,
                "RUN_TASK_C": task_C_node,
              },
            ),
        ],
    )
    ```

=== "Go"

    In ADK Go 2.0, conditional dispatch is expressed in the `workflow` graph
    API: a node sets one or more route values on its emitted `session.Event`
    (the `Routes` field), and each `workflow.Edge` selects its target with a
    `workflow.Route` matcher — `workflow.StringRoute`, `IntRoute`, `BoolRoute`,
    or `MultiRoute`. For example,
    `workflow.Edge{From: classify, To: question, Route: workflow.StringRoute("question")}`.
    See the runnable
    [string](https://github.com/google/adk-go/tree/main/examples/workflow/routing/string),
    [int](https://github.com/google/adk-go/tree/main/examples/workflow/routing/int),
    and [LLM](https://github.com/google/adk-go/tree/main/examples/workflow/routing/llm)
    routing examples.

    When using the prebuilt workflow agents instead of the graph API, encode
    the routing decision in session state (via `OutputKey`) and let downstream
    agents inspect it in their `Instruction` template, or use a `loopagent`
    with an `Escalate`-based exit for loop-until-done patterns (see the
    [loop and escalation example](#loop-and-escalation-exit) below).

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
    from google.adk.workflow import JoinNode

    my_join_node = JoinNode(name="my_join_node")

    edges=[
        ("START", parallel_task_A, my_join_node),
        ("START", parallel_task_B, my_join_node),
        ("START", parallel_task_C, my_join_node),
        (my_join_node, final_task_D),
    ]
    ```

    !!! warning "Caution: Stuck JoinNode from incomplete nodes"

        The ***JoinNode*** object proceeds only after all its upstream nodes
        have provided an Event output. If one of the upstream nodes fails to
        provide output, the JoinNode is stuck and workflow execution stops.
        Make sure to include failsafe output from any node that outputs to a
        ***JoinNode***.

=== "Go"

    ADK Go 2.0 provides `workflow.JoinNode` (`workflow.NewJoinNode`) for true
    fan-in in the graph API: parallel edges feed into the join node, which
    waits for all of them to complete before continuing. When using the
    prebuilt workflow agents instead, you can express the same fan-out/join by
    nesting a `parallelagent` as the first sub-agent of a `sequentialagent`:
    each parallel branch writes its output to a unique `OutputKey` in session
    state, and after all branches complete the synthesis agent reads those
    keys through its `Instruction` template (shown below):

    ```go
    --8<-- "examples/go/snippets/graphs/routes/main.go:parallel-fan-out"
    ```

    !!! warning "Caution: Parallel agent isolation"

        Each sub-agent in a `parallelagent` runs in an isolated branch
        context. They share the underlying session state for writes, but
        they do not see each other's in-progress events. Use distinct
        `OutputKey` values to avoid write collisions between branches.

## Nested workflows

When building more complex workflows, you may want to encapsulate the
functionality for specific tasks into reusable workflows. One or more
workflow agents can be used as a sub-agent within another workflow agent to
accomplish this goal.

![Nested Workflows inside a parent Workflow](/assets/graph-workflow-nodes.svg)

**Figure 3.** Nested workflow agents as sub-agents inside a parent workflow.

=== "Python"

    ```python
    from google.adk import Workflow

    root_agent = Workflow(
        name="parent_workflow",
        edges=[
           ("START", task_A1, router),
           (router, {
                "RUN_WORKFLOW_B": workflow_B,
                "RUN_WORKFLOW_C": workflow_C,
                },
           ),
        ],
    )
    ```

    #### Nested workflow data output

    Output for nested Workflow objects works slightly differently from
    individual nodes. When the nested workflow completes one of its nodes, it
    transmits data to the next node in the nested workflow's graph *and* the
    system bubbles up the Event for that node to the parent workflow for
    process traceability. When the nested workflow completes the last node in
    its process, the parent node extracts data from the final leaf nodes and
    emits it as the output of the nested workflow.

=== "Go"

    In Go, any workflow agent (sequential, parallel, or loop) can be
    provided as a `SubAgent` of another workflow agent. The nested workflow
    runs to completion as a single logical step from the parent's perspective.
    State written by steps inside the nested workflow is immediately visible
    to steps that follow it in the parent:

    ```go
    --8<-- "examples/go/snippets/graphs/routes/main.go:nested-workflows"
    ```

## Loop and escalation exit

A loop repeats a set of steps until a termination condition is met. In Python
this is a cycle in the `edges` graph that routes back to an earlier node; in
Go it is a `loopagent` that stops when any sub-agent sets
`EventActions.Escalate = true` or when `MaxIterations` is reached.

=== "Python"

    ```python
    def router(node_input: str):
        """Route to task B or C based on node_input."""
        if condition(node_input):
            return Event(route="RUN_TASK_C")
        return Event(route="RUN_TASK_B")

    root_agent = Workflow(
        name="routing_workflow",
        edges=[
            ("START", task_A_node, router),
            (router,
              {
                "RUN_TASK_B": task_B_node,
                "RUN_TASK_C": task_C_node,
              },
            ),
        ],
    )
    ```

=== "Go"

    `loopagent` repeatedly runs its `SubAgents` in order. A sub-agent (or a
    tool called by a sub-agent) signals termination by setting
    `ctx.Actions().Escalate = true`. The loop exits immediately after the
    current iteration completes. This is the idiomatic Go equivalent of
    conditional routing back to an earlier node:

    ```go
    --8<-- "examples/go/snippets/graphs/routes/main.go:loop-escalate"
    ```
