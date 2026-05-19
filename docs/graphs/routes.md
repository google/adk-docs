# Build graph routes for agent workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.0.0</span>
</div>

Graph-based workflows in ADK define agent logic as a graph of execution nodes
and edges, allowing you to build more reliable processes that combine artificial
intelligence (AI) reasoning and code logic. These workflows allow you to create
logical routes of execution nodes that can encapsulate code functions,
AI-powered agents, Tools, and human input. By explicitly mapping out routing
logic, this approach allows you to define a specific, step-wise process workflow
in code, providing improved precision and reliability over purely prompt-based
agents.

![Graph-based flight upgrade agent](/assets/graph-workflow-router.svg)

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

**Figure 1.** Visualization of a task graph and the ***Workflow*** code to
implement it.

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
objects. The following shows a simple ***FunctionNode*** that handles text
inputs and sends a text output:

```python
from google.adk import Event

def my_function_node(node_input: str):
    input_text_modified = node_input.upper()
    return Event(output=input_text_modified)
```

For more information about transferring data between nodes, see .
[Data handling for agent workflows](/graphs/data-handling/).

## Workflow graphs syntax

You define a graph by creating an ***edges*** array, which defines a logical
execution path of *nodes* and conditions to be followed. This section
provides an overview of graph syntax in an ***edges*** array. The following code
example shows a basic workflow with two nodes to be executed in order:

```python
from google.adk import Workflow

root_agent = Workflow(
    name="sequential_workflow",
    edges=[("START", task_A_node, task_B_node)],
)
```

!!! caution "Caution: Workflows and agent limitations"

    You can add ***Agents***, or ***LlmAgents***, to graph-based workflows,
    however they must be set to a task or single-turn mode. For more
    information about agent modes, see
    [Build collaborative agent teams](/workflows/collaboration/#mode-configuration-and-behaviors).

### Route sequences

The ***edges*** array executes nodes based on the order or nodes presented in
the array, starting with the first row and proceeding through the subsequent
rows until execution is complete. The first row of the ***edges*** array uses
the ***START*** keyword to indicate the beginning of a graph execution, with
each listed node executed in sequence, as shown in the following code
snippets:

```python
edges=[("START", task_A_node)]  # single node run
edges=[("START",
        task_A_node,
        task_B_node,
        task_C_node)]           # 3 nodes run in order
```

You can also use ***START*** more than once to initiate parallel tasks at the
beginning of a workflow graph, as shown in the following code snippet:

```python
edges=[
    ("START", parallel_task_A),
    ("START", parallel_task_B),
    ("START", parallel_task_C),
]
```

!!! warning "Caution: Limitations on parallel nodes"

    Not all workflow nodes or subagents can be run in parallel. In particular,
    you cannot run multiple interactive chat sessions within the same agent
    session.

### Route branches and conditional execution

The subsequent rows of the ***edges*** arrays after the START keyword define
additional execution logic for nodes. For branching paths, which is how you create a conditional node, you define a node,
usually a ***FunctionNode***, that outputs an Event with a specific  ***route*** value. In the edges graph, you then define the conditional execution logic by mapping these route values to target nodes, as shown in the following code example of a weekend planner agent:

```python
class WeekendBudget(BaseModel):
  budget: float = Field(
      default=None, description="The budget for the weekend in US dollars."
  )

def process_input(node_input: str):
  """Saves the user's raw text into the workflow state."""
  return Event(state={"latest_input": node_input})

extract_budget = Agent(
    name="extract_budget",
    model=MODEL_NAME,
    instruction=(
        "You are a data extraction assistant. Read the user's latest input:"
        " '{latest_input}'. Extract the budget they have for their weekend"
        " plans. If they do not explicitly mention a budget, set it to 100."
    ),
    output_schema=WeekendBudget,
    output_key="weekend_budget",
)

def route_weekend(weekend_budget: WeekendBudget):
  amount = weekend_budget.budget

  if amount < 5:
    yield Event(route="too_low")
  elif amount < 100:
    yield Event(route="value_ideas")
  else:
    yield Event(route="premium_ideas")

def handle_too_low():
  """Fallback route for very low budgets."""
  yield Event(
      message="I'm sorry, but a budget under $5 is too low to do anything fun!"
  )

value_agent = Agent(
    name="value_agent",
    model=MODEL_NAME,
    instruction=(
        "The user is looking for weekend ideas and has a budget of"
        " ${weekend_budget.budget}. Suggest 2 to 3 fun, cheap ideas they"
        " can do that fit strictly within this budget."
    ),
)

premium_agent = Agent(
    name="premium_agent",
    model=MODEL_NAME,
    instruction=(
        # Changed the variable placeholder here:
        "The user is looking for weekend ideas and has a generous budget of"
        " ${weekend_budget.budget}. Suggest 2 to 3 fancy, premium ideas they"
        " can do that utilize this budget."
    ),
)

root_agent = Workflow(
    name="weekend_planner",
    edges=[
        ("START", process_input, extract_budget, route_weekend),

        (
            route_weekend,
            {
                "too_low": handle_too_low,
                "value_ideas": value_agent,
                "premium_ideas": premium_agent,
            },
        ),
    ],
)
```

## Parallel tasks: fan out and join paths

You can create graphs that split execution across multiple, parallel nodes, and
typically you need to assemble the output of each node for further processing.
You accomplish this by using a ***JoinNode*** object, which waits for each
parallel task to complete and then passes the collection of outputs from these
nodes to the next node.

![Tasks connecting to a JoinNode](/assets/graph-joinnode.svg)

**Figure 2.** The output of parallel task nodes can be assembled using a
JoinNode object.

The following code snippet shows how to implement a basic ***JoinNode*** object
and use it to assemble output of all the nodes:

```python
​​from google.adk.workflow import JoinNode

my_join_node = JoinNode(name="my_join_node")

edges=[
    ("START", parallel_task_A, my_join_node),
    ("START", parallel_task_B, my_join_node),
    ("START", parallel_task_C, my_join_node),
    (my_join_node, final_task_D),
]
```

!!! warning "Caution: Stuck JoinNode from incomplete nodes"

    The ***JoinNode*** object proceeds only after all its upstream nodes have
    provided an Event output. If one of the upstream nodes fails to provide output,
    the JoinNode is stuck and workflow execution stops. Make sure to include
    failsafe output from any node that outputs to a ***JoinNode***.

## Nested workflows

When building more complex workflows, you may want to encapsulate the
functionality for specific tasks into reusable workflows. One or more
***Workflow*** objects can be used as a node within the graph of another
workflow agent to accomplish this goal.

![Nested Workflows inside a parent Workflow](/assets/graph-workflow-nodes.svg)

**Figure 3.** Nested ***Workflows*** as nodes inside a parent ***Workflow***.

The following code snippet shows how to implement a workflow agent with two
nested more ***Workflow*** objects (workflow_B, workflow_C) as nodes in the
graph:

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

### Nested workflow data output

Output for nested Workflow objects works slightly differently from individual
nodes. When the nested workflow completes one of its nodes, it transmits data
to the next node in the nested workflow's graph *and* the system bubbles up the
Event for that node to the parent workflow for process traceability. When the
nested workflow completes the last node in its process, the parent node extracts
data from the final leaf nodes and emits it as the output of the nested
workflow.
