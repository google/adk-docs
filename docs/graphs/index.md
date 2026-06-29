# Graph-based agent workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.0.0</span><span class="lst-go">Go v2.0.0</span>
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
    from google.adk import Agent
    from google.adk import Workflow
    from google.adk import Event
    from pydantic import BaseModel

    city_generator_agent = Agent(
        name="city_generator_agent",
        model="gemini-flash-latest",
        instruction="""Return the name of a random city.
          Return only the name, nothing else.""",
        output_schema=str,
    )

    class CityTime(BaseModel):
        time_info: str  # time information
        city: str       # city name

    def lookup_time_function(node_input: str):
        """Simulate returning the current time in the specified city."""
        return CityTime(time_info="10:10 AM", city=node_input)

    city_report_agent = Agent(
        name="city_report_agent",
        model="gemini-flash-latest",
        input_schema=CityTime,
        instruction="""Output following line:
        It is {CityTime.time_info} in {CityTime.city} right now.""",
        output_schema=str,
    )

    def completed_message_function(node_input: str):
        return Event(
            message=f"{node_input}\n WORKFLOW COMPLETED.",
        )

    root_agent = Workflow(
        name="root_agent",
        edges=[
            ("START", city_generator_agent, lookup_time_function,
              city_report_agent, completed_message_function)
        ],
    )
    ```

=== "Go"

    In Go, sequential workflows are built by composing sub-agents with
    `sequentialagent.New`. Each agent is an `agent.Agent` implementation whose
    `Run` function yields `*session.Event` values. Agents share data between
    steps by writing to session state with `ctx.Session().State().Set` and
    reading it back with `ctx.Session().State().Get`.

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
    process_message = Agent(
        name="process_message",
        model="gemini-flash-latest",
        instruction="""Classify user message into either "BUG", "CUSTOMER_SUPPORT",
          or "LOGISTICS". If you think a message applies to more than one category,
          reply with a comma separated list of categories.
       """,
        output_schema=str,
    )

    def router(node_input: str):
        routes = node_input.split(",")
        routes = [route.strip() for route in routes]
        return Event(route=routes)

    def response_1_bug():
        return Event(message="Handling bug...")

    def response_2_support():
        return Event(message="Handling customer support...")

    def response_3_logistics():
        return Event(message="Handling logistics...")

    root_agent = Workflow(
       name="routing_workflow",
       edges=[
           ("START", process_message, router),
           ( router,
               {
                   "BUG": response_1_bug,
                   "CUSTOMER_SUPPORT": response_2_support,
                   "LOGISTICS": response_3_logistics,
               }
           )
       ],
    )
    ```

=== "Go"

    In Go, a processing pipeline is assembled by composing workflow agents. The
    example below uses `sequentialagent.New` to run a classification agent
    followed by a handler agent. The classification result is written to session
    state with `ctx.Session().State().Set` and can be read by subsequent agents
    to implement branching logic.

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

-   **Live streaming:** Not supported in graph-based workflows.
-   **Integrations:** Some third-party
    [integrations](/integrations/) may not be compatible with graph-based
    workflows.

!!! note "Go: graph workflow API"

    ADK Go 2.0 provides the equivalent of the Python `Workflow` class in the
    `workflow` package: build a graph with `workflow.New` and a slice of
    `workflow.Edge` values, express conditional routing with `workflow.Route`
    (for example `workflow.StringRoute`, `IntRoute`, or `BoolRoute`) matched
    against the `Routes` on the emitted `session.Event`, and fan results back
    in with `workflow.JoinNode`. Wrap a graph as an agent with
    `workflowagent.New`.

    For simple, deterministic pipelines you can also use the prebuilt workflow
    agents —
    [`sequentialagent`](/agents/workflow-agents/sequential-agents/),
    [`parallelagent`](/agents/workflow-agents/parallel-agents/), and
    [`loopagent`](/agents/workflow-agents/loop-agents/).
