# Dynamic agent workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

The ADK framework provides a programmatic way to define workflows as a more
flexible and powerful alternative to [graph-based workflows](/graphs/).
Using a graph-based approach provides a convenient way to compose multi-step,
static process structures with workflow nodes. However, if the logic path for
your workflow is more complex, with iterative loops or complex branching logic,
a graph-based approach may not suit your needs, or may become too unwieldy to
manage.

Dynamic workflows in ADK allow you to put aside graph-based path structures and
use the full power of your chosen programming language to build workflows. With
dynamic workflows, you can create workflows with simple decorators (Python) or
constructor functions (Go), invoke workflow nodes as functions, and build
complex routing logic. Here are some of the benefits of dynamic workflows in ADK:

-   **Flexible Control Flow:** Define execution order dynamically using
    loops, conditionals, and recursion which are difficult or impossible to
    represent in static graphs.
-   **Programmatic Experience:** Use familiar constructs like `while` loops
    and `async/await` (Python) or `for` loops and `workflow.RunNode` (Go)
    instead of graph-based routing.
-   **Automatic Checkpointing:** Dynamic workflows track each node
    execution. Successful sub-nodes are automatically skipped when resuming the
    workflow, making complex logic durable and resumable by default.
-   **Encapsulation:** Wrap business logic into *parent* nodes that
    internally compose lower-level nodes, keeping the overall workflow
    clean and manageable.

## Get started

The following dynamic workflow code example shows how to define a basic
workflow containing a single node with a function:

=== "Python"

    ```python
    from google.adk import Context
    from google.adk import Workflow
    from google.adk.workflow import node
    from typing import Any

    @node(name="hello_node")
    def my_node(node_input: Any):
        return "Hello World"

    # define a dynamic workflow node
    @node(rerun_on_resume=True)
    async def my_workflow(ctx: Context, node_input: str) -> str:
        # run_node executes a node and returns its output
        result = await ctx.run_node(my_node, node_input="hello")
        return result

    # Run the workflow
    root_agent = Workflow(
        name="root_agent",
        edges=[("START", my_workflow)],
    )
    ```

    This example uses the [***@node***](#node) annotation for convenience and to
    keep the written code as simple as possible. This annotation generates wrappers
    that allow the code to be run in the context of an ADK dynamic workflow.

=== "TypeScript"

    TypeScript has no `@node` decorator. Use the `node(fn, options)` factory
    function instead. The `ctx.runNode()` method is the equivalent of
    `ctx.run_node()`:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/get_started.ts:get-started"
    ```

    When you write an orchestrator node, two details affect how you read
    results and how the workflow behaves after a pause:

    -   The `ctx.runNode()` method resolves to a node result, not to the
        output value. Read the `.output` property to get the value.
    -   An orchestrator that calls `ctx.runNode()` must set
        `rerunOnResume: true`. This setting causes the node body to re-run
        on resume, so already-finished children are replayed from their
        checkpoints instead of being executed again.

=== "Go"

    In Go, `workflow.NewFunctionNode` replaces the `@node` decorator and
    `workflow.NewDynamicNode` replaces the `@node(rerun_on_resume=True)` async
    orchestrator. `workflow.RunNode` is the direct equivalent of
    `ctx.run_node()`. `workflowagent.New` with `workflow.Chain` replaces
    `Workflow(edges=[...])`.

    Resume behaviour after a human-in-the-loop pause is controlled by
    `NodeConfig.RerunOnResume` — see [Nodes](#node) below for details.

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:get-started"
    ```

## Building blocks: nodes and workflows

Nodes and workflows represent the basic building blocks of ADK's dynamic
workflows. These types and functions provide the functionality required to
wrap your code so it can be integrated into code-based workflows in ADK.

### Nodes {#node}

A dynamic workflow in ADK is composed of *nodes*. A simple version of a
usable workflow node wraps a plain function with the metadata required to
run within a workflow.

=== "Python"

    In Python, the ***@node*** annotation generates the node wrapper, keeping
    boilerplate to a minimum:

    ```python
    @node(name="hello_node")
    def my_function_node(node_input: Any):
        return "Hello World"
    ```

    The following code snippet shows the equivalent code *without* the
    ***@node*** annotation:

    ```python
    # base function
    def my_function_node(node_input: Any):
        return "Hello World"

    # FunctionNode wrapper with options
    success_node = FunctionNode(
        my_function_node,
        name="hello",
        rerun_on_resume=True,
    )
    ```

    Creating the node wrapper code yourself can be useful if you are wrapping
    functions from an external library, need to create multiple nodes from the
    same function with different configurations, or if you are managing node
    references in a registry for advanced orchestration.

=== "TypeScript"

    There are two ways to build a node: the `node(fn, options)` factory
    function, and the explicit `new FunctionNode(name, fn, config)`
    constructor. Use the constructor when you are wrapping a function from
    another library, need several differently configured nodes from one
    function, or keep node references in a registry for advanced
    orchestration.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/nodes.ts:node-forms"
    ```

    In this code sample, the most important option is `rerunOnResume`, which
    controls what happens when a workflow resumes after a human-in-the-loop
    pause:

    -   **`true` (re-entry):** the node body re-runs from the top. Use this
        setting for any orchestrator that calls `ctx.runNode()`. The body
        re-executes, and already-completed child activations are skipped
        automatically.
    -   **`false` (handoff, the leaf default):** the resume payload is
        routed to the node's successor as input, bypassing the interrupted
        node.

=== "Go"

    In Go, `workflow.NewFunctionNode[IN, OUT]` wraps a plain function as a
    workflow node, inferring input and output types from the generic parameters.
    There is no decorator syntax; the node is a value that you pass as a child
    to `workflow.RunNode` inside a dynamic orchestrator:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:building-blocks-nodes"
    ```

    `NodeConfig` holds the same options as Python's `@node` arguments.
    The most important field is `RerunOnResume *bool`, which controls what
    happens when a workflow resumes after a human-in-the-loop pause:

    -   **`&true` (re-entry mode)**: the interrupted node is re-run from the
        beginning on resume. Use this for dynamic orchestrator nodes that call
        `workflow.RunNode` in a loop — the body re-executes and already-completed
        child activations are skipped automatically (checkpointing). This mirrors
        Python's `@node(rerun_on_resume=True)`.
    -   **`&false` (handoff mode)**: the resume payload is routed directly to
        the node's successor as input, bypassing the interrupted node entirely.
        Use this for leaf nodes that simply emit a pause event and expect the
        human response to flow to the next step.
    -   **`nil`**: the default depends on node type. `workflow.NewDynamicNode`
        automatically sets `nil → &true` (re-entry mode), because an
        orchestrator body must be re-entered on resume to deliver cached child
        results. `workflow.NewFunctionNode` and other leaf node constructors
        leave `nil` as-is, which the engine treats as handoff (`&false`).
        Explicit `&false` is always respected on any node type.

    ```go
    // NewDynamicNode: nil RerunOnResume is automatically set to &true.
    // Passing &rerun explicitly is equivalent and makes the intent clear.
    rerun := true
    orchestratorNode := workflow.NewDynamicNode[string, string]("my_workflow",
        myOrchestratorfn,
        workflow.NodeConfig{RerunOnResume: &rerun}, // re-entry: node body re-runs on resume
    )

    // NewFunctionNode: nil RerunOnResume stays nil → engine treats as handoff.
    handoffNode := workflow.NewFunctionNode("leaf_node",
        myLeafFn,
        workflow.NodeConfig{}, // nil RerunOnResume → handoff for FunctionNode
    )
    ```


### Workflows

In an ADK dynamic workflow, you use a dynamic node as the primary
orchestrator for nodes. A dynamic node manages running child nodes and the
execution logic (order and paths) for those nodes.

=== "Python"

    ```python
    @node(rerun_on_resume=True)
    async def my_workflow(ctx):
        # run_node executes a node and returns its output
        result = await ctx.run_node(my_function_node, node_input="Hello")
        result_formatted = await ctx.run_node(my_formatting_node, node_input=result)
        return result_formatted

    # Run the workflow
    root_agent = Workflow(
        name="root_agent",
        edges=[("START", my_workflow)],
    )
    ```

=== "TypeScript"

    The orchestrator is an async function that awaits `ctx.runNode()` for
    each child step. Wrap it as a node with `rerunOnResume: true` and use it
    as the graph's only edge:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/nodes.ts:workflows"
    ```

=== "Go"

    `workflow.NewDynamicNode` creates an orchestrator whose body calls
    `workflow.RunNode` for each child step. `workflowagent.New` with
    `workflow.Chain(workflow.Start, myWorkflow)` is the equivalent of
    `Workflow(edges=[("START", my_workflow)])`:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:building-blocks-workflow"
    ```

## Data handling

When using dynamic workflows with ADK, passing data is simpler than
[graph-based workflows](/graphs/) because `workflow.RunNode` returns the
child node's output directly as a typed Go value — eliminating the need to
manually read and write session state keys for data transfer.

=== "Python"

    ```python
    from google.adk import Context
    from google.adk.workflow import node

    @node(rerun_on_resume=True)
    async def editorial_workflow(ctx: Context, user_request: str):
        # Agent Node generates output
        raw_draft = await ctx.run_node(draft_agent, user_request)

        # Function Node formats text
        formatted_text = await ctx.run_node(format_function_node, raw_draft)

        return formatted_text
    ```

    You can also pass specific data schemas using a defined class and configure
    input and output schemas, similar to graph-based workflow nodes:

    ```python
    from google.adk import Agent
    from google.adk import Context
    from google.adk.workflow import node
    from pydantic import BaseModel

    class CityTime(BaseModel):
        time_info: str  # time information
        city: str       # city name

    @node
    def city_time_function(city: str):
        """Simulate returning the current time in a specified city."""
        return CityTime(time_info="10:10 AM", city=city)

    city_report_agent = Agent(
        name="city_report_agent",
        model="gemini-flash-latest",
        input_schema=CityTime,
        instruction="""output the data provided by the previous node.""",
    )

    @node # workflow node
    async def city_workflow(ctx: Context):
        city_time = await ctx.run_node(city_time_function, "Paris")
        report_text = await ctx.run_node(city_report_agent, city_time)

        return report_text
    ```

=== "TypeScript"

    The `ctx.runNode()` function returns the child's result directly, so
    there are no session-state keys to read and write to move a value one
    step downstream. This function accepts any node-like value, including an
    `LlmAgent`, without wrapping it in `node()` first:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/data_handling.ts:data-handling"
    ```

    Schemas work the same way as in a graph. Attach them to the nodes you
    run, as shown in the [sequence route](#sequence-route) section.

=== "Go"

    In Go, `workflow.NewAgentNode` wraps an `agent.Agent` so it can be
    invoked via `workflow.RunNode` inside a dynamic orchestrator. The output
    of each `RunNode` call is returned as a typed value — no session state
    reads are required:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:data-handling"
    ```

For more information on data handling between workflow nodes, see
[Data handling for agent workflows](/graphs/data-handling/).

## Workflow routes

Dynamic workflows in ADK provide more flexibility in terms of routing logic
compared to [graph-based workflows](/graphs/), including
iterative loops or more complex branching logic. This section describes some of
the techniques that you can use for routing.

### Sequence route

You can create sequential task processing with dynamic workflows in ADK, just
as you can with graph-based workflows.

=== "Python"

    The following code snippet shows a dynamic workflow with an agent, a
    function node, and a second agent:

    ```python
    @node # workflow node
    async def city_workflow(ctx: Context):
        city = await ctx.run_node(city_generator_agent)
        city_time = await ctx.run_node(city_time_function, city)
        report_text = await ctx.run_node(city_report_agent, city_time)

        return report_text
    ```

=== "TypeScript"

    A sequential route awaits `ctx.runNode()` calls one after another. Each
    call finishes before the next one starts:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/sequence_route.ts:sequence-route"
    ```

=== "Go"

    Call `workflow.RunNode` sequentially inside a `NewDynamicNode` body —
    each call awaits the child before the next one starts. The
    [data handling example above](#data-handling) demonstrates exactly this
    pattern: `cityWorkflow` calls `workflow.RunNode` for `cityTimeNode` and
    then `cityReportNode` in order, passing each node's typed output to the
    next.

### Loop route

For workflows where you want to use an iterative loop for a task, dynamic
workflows offer much more flexibility to define the routing logic you need.

=== "Python"

    The following code example shows how to use dynamic workflows to construct
    a workflow loop for generating, reviewing, and updating code:

    ```python
    from google.adk import Context
    from google.adk import Event
    from google.adk.agents import LlmAgent
    from google.adk.workflow import node

    coder_agent = LlmAgent(
        name="generator_agent",
        model="gemini-flash-latest",
        instruction="Write python code for user request.",
        output_schema=str,
    )

    @node(name="lint_reviewer")
    async def compile_lint_check(ctx: Context, code: str):
        # Simulate API call or lint check
        class Response:
            findings = ""
        return Response()

    fixer_agent = LlmAgent(
        name="fixer_agent",
        model="gemini-flash-latest",
        instruction="""Refactor current code {code}.
            Based on compile & lint review: {findings}""",
        output_schema=str,
    )

    @node # workflow node
    async def code_workflow(ctx: Context, user_request: str):
      code = await ctx.run_node(coder_agent, user_request)
      check_resp = await ctx.run_node(compile_lint_check, code)

      while check_resp.findings:
        yield Event(state={"code": code, "findings": check_resp.findings})
        code = await ctx.run_node(fixer_agent, {"code": code, "findings": check_resp.findings})

        check_resp = await ctx.run_node(compile_lint_check, code)

      yield Event(output=code)
    ```

=== "TypeScript"

    Dynamic workflows can help keep workflow logic simple by defining an
    iteration as an ordinary loop rather than a back-edge in a graph. Values
    are held in local variables, and state is written only where an agent's
    instruction template needs to read it back. Unlike a graph cycle, the
    loop is bounded by its loop condition:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/loop_route.ts:loop-route"
    ```

=== "Go"

    In Go, the loop is a plain `for` loop inside the dynamic node body. The
    lint check node returns an empty string when there are no findings,
    which signals the loop to exit:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:loop-route"
    ```

### Parallel execution routes

Dynamic workflows in ADK can support parallel execution.

=== "Python"

    In Python, you can use `asyncio.gather` to build parallel execution:

    ```python
    import asyncio
    from typing import Any
    from google.adk import Context
    from google.adk.workflow import BaseNode, node


    @node(rerun_on_resume=True)
    async def parallel_supervisor(
        ctx: Context, node_input: list[Any], real_node: BaseNode
    ):
        """Runs a worker node in parallel for each item in the input list."""
        tasks = []
        for item in node_input:
            # ctx.run_node returns a future. Append instead of awaiting immediately.
            tasks.append(ctx.run_node(real_node, item))

        # Collect all results in parallel
        results = await asyncio.gather(*tasks)
        return results
    ```

    !!! tip "Tip: Resuming parallel nodes"

        The workflow framework ensures that if a dynamic workflow is resumed,
        only failed or interrupted worker nodes are re-executed, including
        parallel worker nodes.

=== "TypeScript"

    The `ctx.runNode()` method returns a promise, so starting every child
    before awaiting any of them runs the children concurrently, and
    `Promise.all` collects the results. Run IDs are assigned in call order,
    so start the children in a synchronous loop to keep the IDs
    deterministic across a resume:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/parallel_route.ts:parallel-route"
    ```

    !!! tip "Tip: prefer the built-in parallel worker"

        To run one node over each item in a list, use
        `node(worker, {parallelWorker: true, maxParallelWorkers: 4})`. This
        option performs the fan-out and bounds concurrency, which defaults
        to 8. Use the manual approach shown above when you need custom
        scheduling or partial-failure handling. On resume, only failed or
        interrupted workers re-execute in both cases.

=== "Go"

    In Go, `workflow.NewParallelWorker` wraps a child node and runs it
    concurrently for each element of a list input, collecting results into a
    single output slice. The `maxConcurrency` parameter caps how many
    concurrent activations may run simultaneously; `0` means unlimited:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:parallel-route"
    ```

    !!! tip "Tip: Resuming parallel nodes"

        The workflow framework ensures that if a dynamic workflow is resumed,
        only failed or interrupted worker nodes are re-executed, including
        parallel worker nodes managed by `NewParallelWorker`.

## Human input

Dynamic workflows in ADK can also include human input or human in the loop
(HITL) steps.

=== "Python"

    You build human input into workflows by yielding a ***RequestInput*** from
    a node, which pauses the workflow and waits for user input. The following
    code example shows how to build a human input node and include it in a
    workflow:

    ```python
    from typing import Any
    from google.adk import Context
    from google.adk.events import RequestInput
    from google.adk.workflow import node


    @node(rerun_on_resume=False)
    async def get_user_approval(ctx: Context, node_input: Any):
        """Yields a RequestInput to pause the workflow and wait for user input."""
        yield RequestInput(message="Please approve this request (Yes/No)")


    @node(rerun_on_resume=True)
    async def handle_process(ctx: Context, node_input: Any):
        """The orchestrator calling the interactive step."""
        user_response = await ctx.run_node(get_user_approval)

        if user_response.lower() == "yes":
            return "Approved"
        return "Denied"
    ```

    !!! important "Important: Parent nodes with `ctx.run_node`"

        Parent nodes in dynamic workflows that call `ctx.run_node` must set
        `rerun_on_resume=True` to handle interruptions properly.

=== "TypeScript"

    The leaf node returns a `RequestInput` to pause the workflow, and keeps
    the default `rerunOnResume: false` so the reply becomes its output. The
    orchestrator that calls it must set `rerunOnResume: true`:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/human_input.ts:human-input"
    ```

    !!! important "Important: check `interruptIds` before deciding"

        The `ctx.runNode()` method does **not** throw an error when a child
        node interrupts. It returns normally, with the `interruptIds`
        property of the result populated and the `output` property still
        `undefined`. Check `interruptIds` before you use the result. An
        orchestrator that skips this check treats the missing output as an
        answer and continues with a value the user never supplied.

=== "Go"

    In Go, use `workflow.NewEmittingFunctionNode` with
    `workflow.ResumeOrRequestInput` to implement the re-entry HITL pattern.
    On the first pass `ResumeOrRequestInput` emits a `session.RequestInput`
    event and returns `ErrNodeInterrupted`, pausing the workflow. After the
    human replies, the node is re-run from the top (`RerunOnResume: &true`)
    and `ResumeOrRequestInput` returns the human's reply directly:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:human-input"
    ```

## Advanced features

Dynamic workflows offer some advanced features designed to handle more complex
development scenarios. These capabilities allow for finer control over execution
and better integration with existing technical infrastructure.

### Execution IDs

The ADK framework generates a deterministic identifier (ID) for child node
executions based on the parent ID and a counter. ADK workflows use deterministic
IDs for each scheduled node to identify previous results. These IDs are
generated based on the order of dynamic node schedules, and are used for
checkpointing and to re-run tasks in the correct order in the case of a resumed
or re-run workflow.

#### Custom execution IDs

In some rare cases, you may need to have stable identifiers, such as when
processing a reorderable list. In general, you should avoid this due to the
impacts to workflow task retries and process resumes. Specifically, these IDs
are used to check node states and skip execution if a node was already run. If
you provide custom IDs, make sure they are deterministic for workflow re-runs
and logically remain the same for the input.

!!! warning "Warning: Custom execution IDs"

    Avoid creating custom execution IDs. Since execution IDs are used to
    determine the execution order of nodes, custom execution IDs can cause
    problems when the system attempts to re-run those nodes in your workflow.

=== "Python"

    ```python
    from google.adk import Context
    from google.adk.workflow import node
    from pydantic import BaseModel
    from typing import Any
    import asyncio

    class Order(BaseModel):
      order_id: str
      cart_items: list[Product]

    @node(rerun_on_resume=True)
    async def process_all_orders(ctx: Context, node_input: Any):
      orders = await get_orders()

      process_tasks = []
      for order in orders:
        # Use run_id to provide a custom identifier.
        # Custom run_ids must contain at least one non-numeric character
        # to avoid collision with auto-generated sequential numeric IDs.
        task = ctx.run_node(process_order, order, run_id=f"order-{order.order_id}")
        process_tasks.append(task)

      results = await asyncio.gather(*process_tasks)
      return results
    ```

    By default, auto-generated run IDs are sequential integers starting from
    `"1"` (represented as strings). Custom `run_id` values must contain at
    least one non-numeric character to avoid collisions with these
    auto-generated IDs.

=== "TypeScript"

    Pass a `runId` as a trailing option to `ctx.runNode()`. The ID must
    contain at least one non-numeric character so it does not collide with
    the auto-generated sequential IDs:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/custom_run_ids.ts:custom-execution-ids"
    ```

=== "Go"

    In Go, pass `workflow.WithRunID("order-x")` as a trailing option to
    `workflow.RunNode`. The ID must contain at least one non-numeric character
    to avoid collision with the auto-generated sequential counter IDs:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:custom-execution-ids"
    ```
