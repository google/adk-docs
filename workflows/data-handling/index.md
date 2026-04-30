# Data handling for agent workflows

Supported in ADKPython v2.0.0Beta

Structuring and managing data between agents and graph-based nodes is critical for building reliable processes with ADK. This guide explains data handling within graph-based workflows and collaboration agents, including how information is transmitted and received between graph nodes using ***Events***. It covers the essential parameters for events, data, content, and state, and explains how to implement structured data transfer for both function and agent nodes using data format schemas and specific instruction syntax.

Beta Release

ADK 2.0 is a Beta release and may cause breaking changes when used with prior versions of ADK. Do not use ADK 2.0 if you require backwards compatibility, such as in production environments. We encourage you to test this release and we welcome your [feedback](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)!

## Workflow graph Events

Within a graph-based workflow, you pass data using ***Events***. All execution *nodes* in a workflow graph consume and emit Events. This section covers the basics of transmitting and receiving data between nodes in a ***Workflow***. Events have specific parameters for transmitting different types of data between nodes. The key parameters for node data handling are as follows:

- **`output`**: Parameter for passing information between *nodes*.
- **`message`**: Data intended as a response to a user.
- **`state`**: Data automatically persisted across nodes via ***Events*** throughout an ADK session.

Events also carry additional information about the workflow, including the source node of the Event.

### Node input and output with Events

Each node in a graph receives and transmits data through the ***Event*** class. Use the ***yield*** syntax to hand off data to the next node, as shown in the following code snippet:

```python
from google.adk import Event

def my_function_node(node_input: str):
    output_value = node_input.upper()
    return Event(output=output_value) # "THE RESULT"
```

Use the ***return*** syntax when outputting ***Event*** data that does not require additional processing. When emitting data that requires additional processing, or if you are generating more than one data item, you can use more than one ***yield*** command. Each ***yield*** call adds to a list of data objects on the Event which is passed to the next node of a graph. A ***return*** or ***yield*** command without a parameter passes a `None` value to the next node.

### Event `output` parameter

The ***output*** parameter of an ***Event*** is the standard way to pass data to the next node of a graph. The next node receives a ***node input*** object containing the data, as shown in the following code sample:

```python
def my_function_node_1():
    return Event(output="The Result")

def my_function_node_2(node_input: str):
    output_value = node_input.lower()
    return Event(output=output_value) # "the result"
```

You can pass longer, structured data in a serializable format, as shown in this code sample:

```python
def my_function_node_3():
    yield Event(
        output={
            "city_name": "Paris",
            "city_time": "10:10 AM",
        },
    )
```

Caution: Event.output limitation

Nodes are only allowed to emit a single ***Event.output*** data payload per execution. This limitation means that while you can more than one ***yield*** in a node, having two or more ***yield*** commands with an ***Event.output*** results in a runtime error.

### Event `message` parameter

The ***message*** parameter of an ***Event*** is used to pass data intended as a user response. In general, you should not use the ***message*** parameter in your agent code unless it is specifically to provide information to a user or request information from a user. The following code example show how to provide information to a user during workflow execution:

```python
async def user_message(node_input: str):
  """Tell user research process is starting."""
  yield Event(message="Beginning research process...")
```

### Event `state` parameter

The ***state*** parameter of an ***Event*** is used to maintain a small set of data values during an entire ADK session. Values in the state parameter automatically persist between Nodes and are meant for guiding the execution of more complex workflows. Nodes can modify state values, and the modified state values are available to downstream Nodes.The following code example shows how state is persisted across nodes:

```python
async def init_state_node(attempts: int = 0):
  yield Event(
      state={
          "attempts": attempts,
      },
  )

async def task_attempt_node(node_input: Content, attempts: int):
  yield Event(
      state={
          "attempts": attempts + 1,
      },
  )

async def read_state_node(ctx: Context):
  print(f"attempts state: {ctx.state}") # attempts state: attempts: 1

root_agent = Workflow(
    name="root_agent",
    edges=[("START", init_state_node, task_attempt_node, read_state_node)],
)
```

Caution: `state` property data limitations

The state parameter *should not be used to persist large amounts of data* between nodes. Use artifacts or other data persistence mechanisms, such as database Tools, to persist large data resources during the life cycle of a Workflow.

## Constrain node data input and output with schemas

You can set input and output data schemas to constrain the input and output data formats of any node, including ***FunctionNodes*** and **Agents**. The following parameters are optional settings for any node. You can set both or either one of these parameters on any workflow node as required by your agent project.

- **`input_schema`**: Set the expected input schema using a class that extends ***BaseModel***.
- **`output_schema`**: Set the required output schema using a class that extends ***BaseModel***.

The code example below shows how to set both input and output schemas for a subagent.

```python
from google.adk import Agent
from pydantic import BaseModel

class FlightSearchInput(BaseModel):
    origin: str           # Airport code "SFO"
    destination: str      # Airport code "CDG"
    departure_date: date  # date(2026, 3, 15)
    passengers: int = 1   # Number of passengers

class FlightSearchOutput(BaseModel):
    flights: list[Flight]
    cheapest_price: float

flight_searcher = Agent(
    name="flight_searcher",
    instruction="Search for available flights.",
    input_schema=FlightSearchInput,
    output_schema=FlightSearchOutput,
    tools=[search_flights_api],
    mode="single_turn",
    ...
)

assistant = Agent(
    name="assistant",
    instruction="You help users plan trips.",
    sub_agents=[flight_searcher],
    ...
)
```

## Access structured data in agents

When you pass structured data into an agent from subagent or a workflow node, such as a Function Node, you can use specific syntax to add that data into the agent's instructions. Specifically, you can use the curly braces `{ }` to select the input schema properties, or `< >` to specify the input schema properties, the `from` keyword, and the name of the node providing the data. The following code snippet shows two ways to include data passed through an agent ***input schema***:

```python
class CityTime(BaseModel):
    time_info: str  # time information
    city: str       # city name

def lookup_time_function(city: str):
    """Simulate returning the current time in the specified city."""
    return Event(output=CityTime(time_info='10:10 AM', city=city))

city_report_agent = Agent(
    name="city_report_agent",
    model="gemini-flash-latest",
    input_schema=CityTime,

    # data selection based on class and parameter
    # instruction="""
    #     Return a sentence in the following format:
    #     It is {CityTime.time_info} in {CityTime.city} right now.
    # """,

    # more restrictive data selection based on source node name
    instruction="""
        Return a sentence in the following format:
        It is <CityTime.time_info from lookup_time_function> in
        <CityTime.city from lookup_time_function> right now.
    """,
)

root_agent = Workflow(
    name="root_agent",
    edges=[
        (START, city_generator_agent, lookup_time_function, city_report_agent)
    ],
)
```

For a complete, but simplified version of this workflow, see [Graph-based agent workflows](/workflows/#get-started).
