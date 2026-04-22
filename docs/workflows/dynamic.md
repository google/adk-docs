# Dynamic workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

The ADK framework provides a programmatic way to define workflows as a more
flexible and powerful alternative to [graph-based workflows](/workflows/).
Using a graph-based approach provides a convenient way to compose multi-step,
static process structures with workflow nodes. However, if the logic path for
your workflow is more complex, with iterative loops or complex branching logic,
a graph-based approach may not suit your needs, or may become too unwieldy to
manage.

Dynamic workflows in ADK allow you to put aside graph-based path structures and
use the full power of your chosen programming language to build workflows. With
Dynamic workflows, you can create workflows with simple decorators, invoke
workflow nodes as functions, and build complex routing logic. Here are some of
the benefits of dynamic workflows in ADK:

-   **Flexible Control Flow:** Define execution order dynamically using
    loops, conditionals, and recursion which are difficult or impossible to
    represent in static graphs.
-   **Programmatic Experience:** Use familiar constructs like `while` loops
    and `async/await` instead of graph-based routing.
-   **Automatic Checkpointing:** Dynamic workflows track each node
    execution. Successful sub-nodes are automatically skipped when resuming the
    workflow, making complex logic durable and resumable by default.
-   **Encapsulation:** Wrap business logic into *parent* nodes that
    internally compose lower-level nodes, keeping the overall workflow graph
    clean and manageable.

!!! example "Alpha Release"

    ADK 2.0 is an Alpha release and may cause breaking changes when used with prior
    versions of ADK. Do not use ADK 2.0 if you require backwards compatibility, such
    as in production environments. We encourage you to test this release and we
    welcome your
    [feedback](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)!

For information on installing ADK 2.0 to test this feature, see
[Welcome to ADK 2.0](/2.0/).

## Get started

The following dynamic workflow code example shows how to define a basic
workflow containing a single node with a function:

```python
from google.adk import Workflow
from google.adk import Event
from google.adk import Context
from typing import Any

@node(name="hello_node")
def my_node(node_input: Any):
    return "Hello World"

# define a dynamic workflow node
@node(rerun_on_resume=True)
async def my_workflow(ctx: Context, node_input: str) -> str:
    # run_node executes a node and returns its output
    result = await ctx.run_node(my_node, input_data="hello")
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

## Building blocks: nodes and workflows

Nodes and workflows represent the basic building blocks of ADK's dynamic
workflows. These classes provide the functionality required to wrap your code so
it can be integrated into code-based workflows in ADK.

### Nodes and @node {#node}

A dynamic workflow in ADK is composed of *nodes*, which are classes derived
from ***BaseNode***. A simple version of a usable workflow node is a
***FunctionNode***, which allows you to wrap code with functionality required to
run within a ***Workflow***. For convenience, the ADK framework provides the
***@node*** annotation which generates the node wrapper, keeping boilerplate
wrapper code to a minimum:

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
functions from an external library, need to create multiple nodes from the same
function with different configurations, or if you are managing node references
in a registry for advanced orchestration.

### Workflows

In an ADK dynamic workflow, you use the ***Workflow*** class as a primary
container for orchestrating nodes. You use a node to define a dynamic workflow
with code that manages running nodes and the execution logic (order and paths)
for those nodes, as shown in the following code sample:

```python
@node(rerun_on_resume=True)
async def my_workflow(ctx):
    # run_node executes a node and returns its output
    result = await ctx.run_node(my_function_node, input_data="Hello")
    result_formatted = await ctx.run_node(my_formatting_node, input_data=result)
    return result_formatted

# Run the workflow
root_agent = Workflow(
    name="root_agent",
    edges=[("START", my_workflow)],
)
```

## Data handling

When using dynamic workflows with ADK, passing data is simpler than
[graph-based workflows](/workflows/) because, with a workflow,
the ***Context*** class's ***run_node()*** method returns the node's output
directly. This eliminates the need to directly handle session state or complex
routing outputs for data transfer. The following code example shows how you can
pass string data between an agent node and a function node:

```python
from google.adk import Context

@node(rerun_on_resume=True)
async def editorial_workflow(ctx: Context, user_request: str):
    # Agent Node generates output
    raw_draft = await ctx.run_node(draft_agent, user_request)

    # Function Node formats text
    formatted_text = await ctx.run_node(format_function_node, raw_draft)

    return formatted_text
```

You can also pass specific data schemas using defined class and configure input
and output schemas, similar to graph-based workflow nodes, as shown in the
following code example:

```python
from google.adk import Agent
from google.adk import Context
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

For more information on data handling between workflow nodes, see
[Data handling for agent workflows](/workflows/data-handling/).

## Workflow routes

Dynamic workflows in ADK provide more flexibility in terms of routing logic
compared to [graph-based workflows](/workflows/), including
iterative loops or more complex branching logic. This section describes some of
the techniques that you can use for routing.

### Sequence route

You can create sequential task processing with dynamic workflows in ADK, just
as you can with graph-based workflows. The following code snippet shows a
dynamic workflow with an agent, a function node, and a second agent:

```python
@node # workflow node
async def city_workflow(ctx: Context):
    city = await ctx.run_node(city_generator_agent)
    city_time = await ctx.run_node(city_time_function, city)
    report_text = await ctx.run_node(city_report_agent, city_time)

    return report_text
```

### Loop route

For workflows where you want to use an iterative loop for a task, dynamic
workflows offer much more flexibility to define the routing logic you need. The
following code example shows how to use dynamic workflows to construct a
workflow loop for generating, reviewing, and updating code:

```python
coder_agent = LlmAgent(
    name="generator_agent",
    model="gemini-flash-latest",
    instruction="Write python code for user request.",
    output_schema=str,
)

@node(name="lint_reviewer")
compile_lint_check = ApiNode()

fixer_agent = LlmAgent(
    name="generator_agent",
    model="gemini-flash-latest",
    instruction="""Refactor current code {code}.
        Based on compile & lint review: {findings}""",
    output_schema=str,
)

@node # workflow node
async def code_workflow(ctx):
  code = await ctx.run_node(coder_agent)
  check_resp = await ctx.run_node(compile_lint_check, code)

  while check_resp.findings:
    yield Event(state={"code": code, "findings": check_resp.findings})
    code = await ctx.run_node(fixer_agent)

    check_resp = await ctx.run_node(compile_lint_check, code)

  return code
```

### Parallel execution routes

Dynamic workflows in ADK can support parallel execution, and you can use
standard asynchronous libraries, such as the `asyncio`, to build this
functionality. The following code example shows how to build a workflow node
that supports parallel execution, which can then be integrated into a larger
workflow:

```python
from google.adk.workflow import BaseNode
from google.adk import Context
from typing import Any
import asyncio

class ParallelNode(BaseNode):
    """A supervisor node that runs a worker node in parallel."""
    real_node: BaseNode

    async def run(self, ctx: Context, node_input: list[Any]):
        tasks = []

        # Dynamically schedule worker nodes for each item in the input list
        for item in node_input:
            # ctx.run_node returns an awaitable future for the ephemeral node
            tasks.append(ctx.run_node(self.real_node, item))

        # Use asyncio to gather results in parallel
        results = await asyncio.gather(*tasks)

        return results
```

!!! tip "Tip: Resuming parallel nodes"

    The workflow framework ensures that if a dynamic workflow is resumed, only
    failed or interrupted worker nodes are re-executed, including parallel worker
    nodes.

## Human input

Dynamic workflows in ADK can also include human input or human in the loop
(HITL) steps. You build human input into workflows by creating a ***BaseNode***
subclass that interrupts the workflow, combined with a ***RequestInput***
instance for providing a request to the user and retrieving the response. The
following code example shows how to build a human input node and include it in a
workflow:

```python
from google.adk.workflow import BaseNode
from google.adk import Context
from google.adk.events import RequestInput
from typing import Any, AsyncGenerator

class GetInput(BaseNode):
    """A node that pauses execution and waits for human input."""
    rerun_on_resume = False  # Ensure the response is yielded as output on resume

    def __init__(self, request: RequestInput, name: str):
        self.request = request
        self.name = name

    def get_name(self) -> str:
        return self.name

    async def run(self) -> AsyncGenerator[Any, None]:
        # Yielding the request tells the workflow to pause and wait for input
        yield self.request

async def approval_process_node(ctx: Context, node_input: Any):
    """A parent node that coordinates a human approval step."""

    # Define the request for the user
    request = RequestInput(message="Please approve this request (Yes/No)")

    # Invoke the HITL node dynamically. The workflow pauses here.
    user_response = await ctx.run_node(GetInput(request, name="approval_step"))

    if user_response.lower() == "yes":
        return "Request Approved"
    else:
        return "Request Denied"
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
processing a reorderable list, you can supply a custom ID when running a node.
In general, you should avoid this due to the impacts to workflow task retries
and process resumes. Specifically, these IDs are used to check node states and
skip execution if a node was already run. If you provide custom IDs, make sure
they are deterministic for workflow re-runs and logically remain the same for
the input. The following example code shows how to add such an identifier when
executing node in a workflow:

!!! warning "Warning: Custom execution IDs"

    Avoid creating custom execution IDs. Since execution IDs are used to determine
    the execution order of nodes, custom execution IDs can cause problems when the
    system attempts to re-run those nodes in your workflow.

```python
class Order(BaseModel):
  order_id: str
  cart_items: list[Product]

def shorten_link(ctx, node_input: str):

  orders = await get_orders()

  process_tasks = []
  for i, order in enumerate(orders):
    task = ctx.run_node(process_order, order, name=order.order_id))

    process_tasks.append(task)

  result = asyncio.gather(*process_tasks)

  yield result
```
