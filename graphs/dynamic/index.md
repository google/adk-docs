# Dynamic agent workflows

Supported in ADKPython v2.0.0Go v2.0.0

The ADK framework provides a programmatic way to define workflows as a more flexible and powerful alternative to [graph-based workflows](/graphs/). Using a graph-based approach provides a convenient way to compose multi-step, static process structures with workflow nodes. However, if the logic path for your workflow is more complex, with iterative loops or complex branching logic, a graph-based approach may not suit your needs, or may become too unwieldy to manage.

Dynamic workflows in ADK allow you to put aside graph-based path structures and use the full power of your chosen programming language to build workflows. With dynamic workflows, you can create workflows with simple decorators (Python) or constructor functions (Go), invoke workflow nodes as functions, and build complex routing logic. Here are some of the benefits of dynamic workflows in ADK:

- **Flexible Control Flow:** Define execution order dynamically using loops, conditionals, and recursion which are difficult or impossible to represent in static graphs.
- **Programmatic Experience:** Use familiar constructs like `while` loops and `async/await` (Python) or `for` loops and `workflow.RunNode` (Go) instead of graph-based routing.
- **Automatic Checkpointing:** Dynamic workflows track each node execution. Successful sub-nodes are automatically skipped when resuming the workflow, making complex logic durable and resumable by default.
- **Encapsulation:** Wrap business logic into *parent* nodes that internally compose lower-level nodes, keeping the overall workflow clean and manageable.

## Get started

The following dynamic workflow code example shows how to define a basic workflow containing a single node with a function:

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

This example uses the [***@node***](#node) annotation for convenience and to keep the written code as simple as possible. This annotation generates wrappers that allow the code to be run in the context of an ADK dynamic workflow.

In Go, `workflow.NewFunctionNode` replaces the `@node` decorator and `workflow.NewDynamicNode` replaces the `@node(rerun_on_resume=True)` async orchestrator. `workflow.RunNode` is the direct equivalent of `ctx.run_node()`. `workflowagent.New` with `workflow.Chain` replaces `Workflow(edges=[...])`.

Resume behaviour after a human-in-the-loop pause is controlled by `NodeConfig.RerunOnResume` — see [Nodes](#node) below for details.

```go
// helloNode is a simple FunctionNode that returns "Hello World".
// In Python this would be written as:
//
//  @node(name="hello_node")
//  def my_node(node_input: Any):
//      return "Hello World"
//
// In Go, workflow.NewFunctionNode wraps the same logic with the
// required node interface, inferring input and output types from
// the generic parameters.
var helloNode = workflow.NewFunctionNode("hello_node",
    func(_ agent.Context, _ string) (string, error) {
        return "Hello World", nil
    },
    workflow.NodeConfig{},
)

// myWorkflow is a dynamic orchestrator node. It calls workflow.RunNode
// to schedule helloNode as a child and returns its output.
// In Python this would be:
//
//  @node(rerun_on_resume=True)
//  async def my_workflow(ctx: Context, node_input: str) -> str:
//      result = await ctx.run_node(my_node, node_input="hello")
//      return result
//
// workflow.NewDynamicNode defaults RerunOnResume to &true, matching the
// Python @node(rerun_on_resume=True) behaviour.
var myWorkflow = workflow.NewDynamicNode[string, string]("my_workflow",
    func(ctx agent.Context, _ string, _ func(*session.Event) error) (string, error) {
        return workflow.RunNode[string](ctx, helloNode, "hello")
    },
    workflow.NodeConfig{},
)

func runGetStarted() error {
    ctx := context.Background()

    // workflowagent.New creates an agent.Agent backed by the workflow engine.
    // workflow.Chain(workflow.Start, myWorkflow) produces the edges slice
    // equivalent to Python's edges=[("START", my_workflow)].
    wa, err := workflowagent.New(workflowagent.Config{
        Name:        "root_agent",
        Description: "A minimal dynamic workflow.",
        Edges:       workflow.Chain(workflow.Start, myWorkflow),
    })
    if err != nil {
        return fmt.Errorf("workflowagent.New: %w", err)
    }

    l := full.NewLauncher()
    return l.Execute(ctx, &launcher.Config{
        AgentLoader: agent.NewSingleLoader(wa),
    }, os.Args[1:])
}
```

## Building blocks: nodes and workflows

Nodes and workflows represent the basic building blocks of ADK's dynamic workflows. These types and functions provide the functionality required to wrap your code so it can be integrated into code-based workflows in ADK.

### Nodes

A dynamic workflow in ADK is composed of *nodes*. A simple version of a usable workflow node wraps a plain function with the metadata required to run within a workflow.

In Python, the ***@node*** annotation generates the node wrapper, keeping boilerplate to a minimum:

```python
@node(name="hello_node")
def my_function_node(node_input: Any):
    return "Hello World"
```

The following code snippet shows the equivalent code *without* the ***@node*** annotation:

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

Creating the node wrapper code yourself can be useful if you are wrapping functions from an external library, need to create multiple nodes from the same function with different configurations, or if you are managing node references in a registry for advanced orchestration.

In Go, `workflow.NewFunctionNode[IN, OUT]` wraps a plain function as a workflow node, inferring input and output types from the generic parameters. There is no decorator syntax; the node is a value that you pass as a child to `workflow.RunNode` inside a dynamic orchestrator:

```go
// myFunctionNode demonstrates the explicit NewFunctionNode constructor —
// equivalent to wrapping a function in a FunctionNode manually in Python:
//
//  success_node = FunctionNode(my_function_node, name="hello", rerun_on_resume=True)
//
// Creating the node directly (rather than via @node) is useful when you
// need multiple nodes from the same function with different configurations,
// or when wrapping functions from an external library.
var myFunctionNode = workflow.NewFunctionNode("hello",
    func(_ agent.Context, _ any) (string, error) {
        return "Hello World", nil
    },
    workflow.NodeConfig{},
)

// myFormattingNode is a second function node that the dynamic orchestrator
// calls in sequence, mirroring:
//
//  result_formatted = await ctx.run_node(my_formatting_node, node_input=result)
var myFormattingNode = workflow.NewFunctionNode("format",
    func(_ agent.Context, in string) (string, error) {
        return fmt.Sprintf("[formatted] %s", in), nil
    },
    workflow.NodeConfig{},
)
```

`NodeConfig` holds the same options as Python's `@node` arguments. The most important field is `RerunOnResume *bool`, which controls what happens when a workflow resumes after a human-in-the-loop pause:

- **`&true` (re-entry mode)**: the interrupted node is re-run from the beginning on resume. Use this for dynamic orchestrator nodes that call `workflow.RunNode` in a loop — the body re-executes and already-completed child activations are skipped automatically (checkpointing). This mirrors Python's `@node(rerun_on_resume=True)`.
- **`&false` (handoff mode)**: the resume payload is routed directly to the node's successor as input, bypassing the interrupted node entirely. Use this for leaf nodes that simply emit a pause event and expect the human response to flow to the next step.
- **`nil`**: the default depends on node type. `workflow.NewDynamicNode` automatically sets `nil → &true` (re-entry mode), because an orchestrator body must be re-entered on resume to deliver cached child results. `workflow.NewFunctionNode` and other leaf node constructors leave `nil` as-is, which the engine treats as handoff (`&false`). Explicit `&false` is always respected on any node type.

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

In an ADK dynamic workflow, you use a dynamic node as the primary orchestrator for nodes. A dynamic node manages running child nodes and the execution logic (order and paths) for those nodes.

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

`workflow.NewDynamicNode` creates an orchestrator whose body calls `workflow.RunNode` for each child step. `workflowagent.New` with `workflow.Chain(workflow.Start, myWorkflow)` is the equivalent of `Workflow(edges=[("START", my_workflow)])`:

```go
// orchestratorWorkflow is a dynamic node that schedules two children in
// sequence via workflow.RunNode, equivalent to:
//
//  @node(rerun_on_resume=True)
//  async def my_workflow(ctx):
//      result = await ctx.run_node(my_function_node, node_input="Hello")
//      result_formatted = await ctx.run_node(my_formatting_node, node_input=result)
//      return result_formatted
var orchestratorWorkflow = workflow.NewDynamicNode[string, string]("my_workflow",
    func(ctx agent.Context, _ string, _ func(*session.Event) error) (string, error) {
        result, err := workflow.RunNode[string](ctx, myFunctionNode, "Hello")
        if err != nil {
            return "", err
        }
        return workflow.RunNode[string](ctx, myFormattingNode, result)
    },
    workflow.NodeConfig{},
)
```

## Data handling

When using dynamic workflows with ADK, passing data is simpler than [graph-based workflows](/graphs/) because `workflow.RunNode` returns the child node's output directly as a typed Go value — eliminating the need to manually read and write session state keys for data transfer.

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

You can also pass specific data schemas using a defined class and configure input and output schemas, similar to graph-based workflow nodes:

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

In Go, `workflow.NewAgentNode` wraps an `agent.Agent` so it can be invoked via `workflow.RunNode` inside a dynamic orchestrator. The output of each `RunNode` call is returned as a typed value — no session state reads are required:

```go
// newDataHandlingWorkflow demonstrates how to pass data between a dynamic
// orchestrator and an LlmAgent-backed node. workflow.NewAgentNode wraps an
// agent.Agent so it can be invoked via workflow.RunNode.
//
// In Python this mirrors:
//
//  city_report_agent = Agent(name="city_report_agent", ...)
//  @node
//  async def city_workflow(ctx: Context):
//      city_time = await ctx.run_node(city_time_function, "Paris")
//      report_text = await ctx.run_node(city_report_agent, city_time)
//      return report_text
func newDataHandlingWorkflow(ctx context.Context) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{})
    if err != nil {
        return nil, fmt.Errorf("gemini.NewModel: %w", err)
    }

    // cityTimeNode is a FunctionNode that returns a formatted city-time string.
    cityTimeNode := workflow.NewFunctionNode("city_time_function",
        func(_ agent.Context, city string) (string, error) {
            return fmt.Sprintf("10:10 AM in %s", city), nil
        },
        workflow.NodeConfig{},
    )

    // cityReportAgent is an LlmAgent that receives the city-time string and
    // produces a human-friendly report.
    cityReportAgent, err := llmagent.New(llmagent.Config{
        Name:        "city_report_agent",
        Model:       model,
        Description: "Reports city time information.",
        Instruction: "Output the data provided by the previous node in a friendly sentence.",
    })
    if err != nil {
        return nil, fmt.Errorf("llmagent.New (cityReport): %w", err)
    }

    // workflow.NewAgentNode wraps cityReportAgent so it can be called from
    // inside a dynamic node via workflow.RunNode.
    cityReportNode, err := workflow.NewAgentNode(cityReportAgent, workflow.NodeConfig{})
    if err != nil {
        return nil, fmt.Errorf("workflow.NewAgentNode: %w", err)
    }

    cityWorkflow := workflow.NewDynamicNode[string, string]("city_workflow",
        func(ctx agent.Context, _ string, _ func(*session.Event) error) (string, error) {
            cityTime, err := workflow.RunNode[string](ctx, cityTimeNode, "Paris")
            if err != nil {
                return "", err
            }
            return workflow.RunNode[string](ctx, cityReportNode, cityTime)
        },
        workflow.NodeConfig{},
    )

    return workflowagent.New(workflowagent.Config{
        Name:      "data_handling_workflow",
        SubAgents: []agent.Agent{cityReportAgent},
        Edges:     workflow.Chain(workflow.Start, cityWorkflow),
    })
}
```

For more information on data handling between workflow nodes, see [Data handling for agent workflows](/graphs/data-handling/).

## Workflow routes

Dynamic workflows in ADK provide more flexibility in terms of routing logic compared to [graph-based workflows](/graphs/), including iterative loops or more complex branching logic. This section describes some of the techniques that you can use for routing.

### Sequence route

You can create sequential task processing with dynamic workflows in ADK, just as you can with graph-based workflows.

The following code snippet shows a dynamic workflow with an agent, a function node, and a second agent:

```python
@node # workflow node
async def city_workflow(ctx: Context):
    city = await ctx.run_node(city_generator_agent)
    city_time = await ctx.run_node(city_time_function, city)
    report_text = await ctx.run_node(city_report_agent, city_time)

    return report_text
```

Call `workflow.RunNode` sequentially inside a `NewDynamicNode` body — each call awaits the child before the next one starts. The [data handling example above](#data-handling) demonstrates exactly this pattern: `cityWorkflow` calls `workflow.RunNode` for `cityTimeNode` and then `cityReportNode` in order, passing each node's typed output to the next.

### Loop route

For workflows where you want to use an iterative loop for a task, dynamic workflows offer much more flexibility to define the routing logic you need.

The following code example shows how to use dynamic workflows to construct a workflow loop for generating, reviewing, and updating code:

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

  return code
```

In Go, the loop is a plain `for` loop inside the dynamic node body. The lint check node returns an empty string when there are no findings, which signals the loop to exit:

```go
// newLoopWorkflow demonstrates an iterative loop inside a dynamic node.
// The orchestrator body uses a plain Go for loop to keep calling the
// lintCheckNode until there are no findings — equivalent to Python's:
//
//  @node
//  async def code_workflow(ctx: Context, user_request: str):
//      code = await ctx.run_node(coder_agent, user_request)
//      check_resp = await ctx.run_node(compile_lint_check, code)
//      while check_resp.findings:
//          code = await ctx.run_node(fixer_agent, ...)
//          check_resp = await ctx.run_node(compile_lint_check, code)
//      return code
func newLoopWorkflow(ctx context.Context) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{})
    if err != nil {
        return nil, fmt.Errorf("gemini.NewModel: %w", err)
    }

    coderAgent, err := llmagent.New(llmagent.Config{
        Name:        "generator_agent",
        Model:       model,
        Description: "Writes Go code for the user request.",
        Instruction: "Write Go code for the user request. Output only the code.",
        OutputKey:   "generated_code",
    })
    if err != nil {
        return nil, fmt.Errorf("llmagent.New (coder): %w", err)
    }

    coderNode, err := workflow.NewAgentNode(coderAgent, workflow.NodeConfig{})
    if err != nil {
        return nil, fmt.Errorf("workflow.NewAgentNode (coder): %w", err)
    }

    // lintCheckNode simulates a lint/compile check. It returns an empty
    // string when there are no findings, signalling the loop to exit.
    lintCheckNode := workflow.NewFunctionNode("lint_reviewer",
        func(_ agent.Context, code string) (string, error) {
            // Simulate a lint check: return findings or empty string when clean.
            if len(code) < 50 {
                return "Code is too short; add error handling.", nil
            }
            return "", nil // no findings — loop exits
        },
        workflow.NodeConfig{},
    )

    fixerAgent, err := llmagent.New(llmagent.Config{
        Name:        "fixer_agent",
        Model:       model,
        Description: "Refactors code based on lint findings.",
        Instruction: "Refactor the provided code to address the review findings. Output only the improved code.",
    })
    if err != nil {
        return nil, fmt.Errorf("llmagent.New (fixer): %w", err)
    }

    fixerNode, err := workflow.NewAgentNode(fixerAgent, workflow.NodeConfig{})
    if err != nil {
        return nil, fmt.Errorf("workflow.NewAgentNode (fixer): %w", err)
    }

    codeWorkflow := workflow.NewDynamicNode[string, string]("code_workflow",
        func(ctx agent.Context, userRequest string, _ func(*session.Event) error) (string, error) {
            code, err := workflow.RunNode[string](ctx, coderNode, userRequest)
            if err != nil {
                return "", err
            }

            findings, err := workflow.RunNode[string](ctx, lintCheckNode, code)
            if err != nil {
                return "", err
            }

            // Loop until the lint check reports no findings.
            for findings != "" {
                code, err = workflow.RunNode[string](ctx, fixerNode, code)
                if err != nil {
                    return "", err
                }
                findings, err = workflow.RunNode[string](ctx, lintCheckNode, code)
                if err != nil {
                    return "", err
                }
            }
            return code, nil
        },
        workflow.NodeConfig{},
    )

    return workflowagent.New(workflowagent.Config{
        Name:      "code_pipeline",
        SubAgents: []agent.Agent{coderAgent, fixerAgent},
        Edges:     workflow.Chain(workflow.Start, codeWorkflow),
    })
}
```

### Parallel execution routes

Dynamic workflows in ADK can support parallel execution.

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

Tip: Resuming parallel nodes

The workflow framework ensures that if a dynamic workflow is resumed, only failed or interrupted worker nodes are re-executed, including parallel worker nodes.

In Go, `workflow.NewParallelWorker` wraps a child node and runs it concurrently for each element of a list input, collecting results into a single output slice. The `maxConcurrency` parameter caps how many concurrent activations may run simultaneously; `0` means unlimited:

```go
// newParallelWorkflow demonstrates parallel execution using
// workflow.NewParallelWorker. The worker node runs a wrapped child node
// concurrently for each element in a list input, collecting results.
//
// This is the Go equivalent of using asyncio.gather in Python:
//
//  @node(rerun_on_resume=True)
//  async def parallel_supervisor(ctx, node_input, real_node):
//      tasks = [ctx.run_node(real_node, item) for item in node_input]
//      results = await asyncio.gather(*tasks)
//      return results
func newParallelWorkflow() (agent.Agent, error) {
    // workerNode processes a single item. NewParallelWorker will call it
    // once per element of the list input, concurrently.
    workerNode := workflow.NewFunctionNode("worker",
        func(_ agent.Context, item string) (string, error) {
            return fmt.Sprintf("processed: %s", item), nil
        },
        workflow.NodeConfig{},
    )

    // NewParallelWorker wraps workerNode so it runs concurrently for each
    // element of a []string input. maxConcurrency=0 means unlimited.
    parallelWorker, err := workflow.NewParallelWorker(
        "parallel_supervisor",
        workerNode,
        0, // maxConcurrency: 0 = unlimited
        workflow.NodeConfig{},
    )
    if err != nil {
        return nil, fmt.Errorf("workflow.NewParallelWorker: %w", err)
    }

    return workflowagent.New(workflowagent.Config{
        Name:        "parallel_workflow",
        Description: "Runs a worker node in parallel for each item in the input list.",
        Edges:       workflow.Chain(workflow.Start, parallelWorker),
    })
}
```

Tip: Resuming parallel nodes

The workflow framework ensures that if a dynamic workflow is resumed, only failed or interrupted worker nodes are re-executed, including parallel worker nodes managed by `NewParallelWorker`.

## Human input

Dynamic workflows in ADK can also include human input or human in the loop (HITL) steps.

You build human input into workflows by yielding a ***RequestInput*** from a node, which pauses the workflow and waits for user input. The following code example shows how to build a human input node and include it in a workflow:

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

Important: Parent nodes with `ctx.run_node`

Parent nodes in dynamic workflows that call `ctx.run_node` must set `rerun_on_resume=True` to handle interruptions properly.

In Go, use `workflow.NewEmittingFunctionNode` with `workflow.ResumeOrRequestInput` to implement the re-entry HITL pattern. On the first pass `ResumeOrRequestInput` emits a `session.RequestInput` event and returns `ErrNodeInterrupted`, pausing the workflow. After the human replies, the node is re-run from the top (`RerunOnResume: &true`) and `ResumeOrRequestInput` returns the human's reply directly:

```go
// newHITLWorkflow demonstrates the re-entry HITL pattern using
// workflow.ResumeOrRequestInput. On the first pass the node emits a
// RequestInput event and returns ErrNodeInterrupted (pausing the workflow).
// After the human replies, the same node is re-run from the top
// (RerunOnResume=&true) and ResumeOrRequestInput returns the human's reply.
//
// In Python this is equivalent to:
//
//  @node(rerun_on_resume=True)
//  async def get_user_approval(ctx, node_input):
//      yield RequestInput(message="Please approve this request (Yes/No)")
//
//  @node(rerun_on_resume=True)
//  async def handle_process(ctx, node_input):
//      user_response = await ctx.run_node(get_user_approval)
//      if user_response.lower() == "yes":
//          return "Approved"
//      return "Denied"
func newHITLWorkflow() (agent.Agent, error) {
    rerun := true

    // approvalNode pauses on the first pass to ask the user for a Yes/No
    // approval, then resolves their decision on resume.
    // workflow.ResumeOrRequestInput handles both phases.
    approvalNode := workflow.NewEmittingFunctionNode[any, any]("get_user_approval",
        func(nc agent.Context, _ any, emit func(*session.Event) error) (any, error) {
            // ResumeOrRequestInput: on first pass, emits the prompt and
            // returns ErrNodeInterrupted. On re-run after the human replies,
            // it returns the reply payload directly.
            reply, err := workflow.ResumeOrRequestInput(nc, emit, session.RequestInput{
                InterruptID: "user_approval",
                Message:     "Please approve this request (Yes/No)",
            })
            if err != nil {
                return nil, err
            }

            response, _ := reply.(string)
            if response == "" {
                response = "No"
            }
            if response == "yes" || response == "Yes" {
                return "Approved", nil
            }
            return "Denied", nil
        },
        workflow.NodeConfig{RerunOnResume: &rerun},
    )

    return workflowagent.New(workflowagent.Config{
        Name:        "hitl_workflow",
        Description: "Pauses for user approval before completing a task.",
        Edges:       workflow.Chain(workflow.Start, approvalNode),
    })
}
```

## Advanced features

Dynamic workflows offer some advanced features designed to handle more complex development scenarios. These capabilities allow for finer control over execution and better integration with existing technical infrastructure.

### Execution IDs

The ADK framework generates a deterministic identifier (ID) for child node executions based on the parent ID and a counter. ADK workflows use deterministic IDs for each scheduled node to identify previous results. These IDs are generated based on the order of dynamic node schedules, and are used for checkpointing and to re-run tasks in the correct order in the case of a resumed or re-run workflow.

#### Custom execution IDs

In some rare cases, you may need to have stable identifiers, such as when processing a reorderable list. In general, you should avoid this due to the impacts to workflow task retries and process resumes. Specifically, these IDs are used to check node states and skip execution if a node was already run. If you provide custom IDs, make sure they are deterministic for workflow re-runs and logically remain the same for the input.

Warning: Custom execution IDs

Avoid creating custom execution IDs. Since execution IDs are used to determine the execution order of nodes, custom execution IDs can cause problems when the system attempts to re-run those nodes in your workflow.

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

By default, auto-generated run IDs are sequential integers starting from `"1"` (represented as strings). Custom `run_id` values must contain at least one non-numeric character to avoid collisions with these auto-generated IDs.

In Go, pass `workflow.WithRunID("order-x")` as a trailing option to `workflow.RunNode`. The ID must contain at least one non-numeric character to avoid collision with the auto-generated sequential counter IDs:

```go
// newCustomIDWorkflow demonstrates supplying stable custom run IDs via
// workflow.WithRunID — equivalent to Python's:
//
//  task = ctx.run_node(process_order, order, run_id=f"order-{order.order_id}")
//
// Custom run IDs must contain at least one non-numeric character to avoid
// collision with auto-generated sequential integer IDs.
func newCustomIDWorkflow() (agent.Agent, error) {
    processOrderNode := workflow.NewFunctionNode("process_order",
        func(_ agent.Context, orderID string) (string, error) {
            return fmt.Sprintf("processed order %s", orderID), nil
        },
        workflow.NodeConfig{},
    )

    orders := []string{"ord-001", "ord-002", "ord-003"}

    processAllOrders := workflow.NewDynamicNode[any, []string]("process_all_orders",
        func(ctx agent.Context, _ any, _ func(*session.Event) error) ([]string, error) {
            results := make([]string, 0, len(orders))
            for _, orderID := range orders {
                // WithRunID supplies a stable, deterministic identifier for
                // each child invocation. IDs must contain at least one
                // non-numeric character to avoid collision with the
                // auto-generated sequential counter IDs.
                result, err := workflow.RunNode[string](
                    ctx,
                    processOrderNode,
                    orderID,
                    workflow.WithRunID(fmt.Sprintf("order-%s", orderID)),
                )
                if err != nil {
                    return nil, fmt.Errorf("process order %s: %w", orderID, err)
                }
                results = append(results, result)
            }
            return results, nil
        },
        workflow.NodeConfig{},
    )

    return workflowagent.New(workflowagent.Config{
        Name:        "custom_id_workflow",
        Description: "Processes orders with stable per-order execution IDs.",
        Edges:       workflow.Chain(workflow.Start, processAllOrders),
    })
}
```
