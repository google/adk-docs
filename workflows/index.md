# Graph-based agent workflows

Supported in ADKPython v2.0.0Beta

Graph-based workflows in ADK let you build agents with more precise control, creating deterministic processes that combine code logic and AI reasoning capabilities. Graph-based workflows allow you to define your agent logic as a graph of execution nodes and edges, combining AI-powered agents with deterministic tools and code.

**Figure 1.** A graph-based agent design for flight upgrades, combining workflow nodes of different types, including Functions, human input, Tools, and LLM capabilities.

Prebuilt ADK [workflow agents](/agents/workflow-agents/), such as [Sequential Agents](/agents/workflow-agents/sequential-agents/), provide a defined process flow control only across a set of agents. You can continue to build standard ADK agents with long prompts, tools, and use them in graph-based workflow agents. When you need more precise control, workflow agent graphs give you more flexibility over how tasks are routed and executed. Graph-based workflows provide the following advantages:

- **Define precise logic:** Explicitly map out routing logic to manage transitions between different nodes.
- **Implement complex structures:** Build agent workflows that support branching and state management.
- **Run chains of functions without AI:** Call agent tools and your own code without invoking a generative AI model.
- **Enhance reliability:** Improve the predictability of your agents by relying on structured node definitions rather than prompts alone.

Beta Release

ADK 2.0 is a Beta release and may cause breaking changes when used with prior versions of ADK. Do not use ADK 2.0 if you require backwards compatibility, such as in production environments. We encourage you to test this release and we welcome your [feedback](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)!

Follow the instructions for [installing ADK 2.0](/2.0/#install) and then check out the instructions below to get started with graph-based workflows.

## Get started

This section describes how to get started with graph-based agents. The following example shows how to create a sequential graph-based agent workflow that generates a city name, looks up the current time in that city with code function, and the final agent reports the information.

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

This sample code demonstrates how you can use the ***Workflow*** class to assemble a simple, sequential workflow and alternate between AI agent processing and code execution. While you could perform these steps using a single agent with a longer prompt and a tool call, the graph-based approach gives you precise control over the task execution order and the data output from each step.

For more information about data handling with graph-based workflows, see [Data handling with workflow nodes and agents](/workflows/data-handling/).

## Build processes with graphs

You can use prompt-based agents to define multiple step processes with descriptions of tasks and procedures using the instructions field of an ADK agent. However, as your instructions and procedures become longer and more complicated, making sure that the agent is following each step and guideline becomes more complicated and less reliable.

Graph-based workflow agents provide a significant advantage over prompt-based agents by allowing you to specifically define the overall process workflow in code. With graph-based agent workflows, each step of the process can be defined as an execution ***Node*** in a graph and each node can be an AI agent, Tool, or your programmed code. The following diagram illustrates how a simple prompt-based agent would translate into a workflow agent graph:

**Figure 2.** Structure of prompt-based agent instructions translated into a graph-based workflow.

Moving from prompt-based agents to graph-based workflow agents allows you to explicitly break out the tasks of a procedure to define a specific execution flow. Once defined, the agent application flows the steps in the graph, switching between non-deterministic AI-powered agents and deterministic code as needed.

The following code sample shows how the workflow graph in Figure 2 could be translated into a graph-based agent using the ***Workflow*** class:

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

This sample code demonstrates how you can use an ***edges*** array to define a graph with routes between a set of *nodes*, which are discrete tasks that can include agents, Tools, your code, and even additional ***Workflows***. For information about building advanced graphs for workflows, see [Build graph routes for workflow agents](/workflows/graph-routes/).

## Known limitations

There are some known limitations with graph-based workflows. They are *not compatible* with the following ADK features:

- **Live Streaming** functionality is not compatible with graph-based workflows.
- **Integrations:** Some third-party [Integrations](/integrations/) may not be compatible with graph-based workflows.
