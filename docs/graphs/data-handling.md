# Data handling for agent workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

Structuring and managing data between agents and graph-based nodes is critical
for building reliable processes with ADK. This guide explains data handling
within graph-based workflows and collaboration agents, including how information
is transmitted and received between graph nodes. It covers the essential
parameters for passing data, content, and state, and explains how to implement
structured data transfer for both function and agent nodes using data format
schemas and specific instruction syntax.

## Workflow data flow

Within a graph-based workflow, nodes pass data to downstream steps through
session state. All execution nodes in a workflow can read from and write to
session state; a step writes its output to a named key, and the next step reads
it by referencing that key in its configuration.

=== "Python"

    In Python, data is exchanged between graph nodes using ***Events***. The key
    parameters for node data handling are:

    -   **`output`**: Parameter for passing information between *nodes*.
    -   **`message`**: Data intended as a response to a user.
    -   **`state`**: Data automatically persisted across nodes via ***Events***
        throughout an ADK session.

=== "Go"

    In ADK Go, workflow data flow is managed through **session state** rather
    than through Event fields. The two primary mechanisms are:

    -   **`OutputKey`** on `llmagent.Config`: after each turn, the framework
        automatically captures the agent's final text response and writes it to
        session state under the key you specify. Downstream agents read it by
        placing `{key}` in their `Instruction` template — the same curly-brace
        syntax as Python.
    -   **`ctx.Session().State().Set` / `.Get`**: for custom `Run` functions and
        tools that need to write or read arbitrary values from state directly.

    State keys may carry a prefix that controls their lifetime and scope:

    | Prefix constant | Prefix string | Scope |
    |---|---|---|
    | `session.KeyPrefixApp` | `"app:"` | Shared across all users and sessions for the app |
    | `session.KeyPrefixUser` | `"user:"` | Tied to the user, shared across their sessions |
    | `session.KeyPrefixTemp` | `"temp:"` | Discarded after the current invocation ends |
    | *(none)* | — | Persists for the lifetime of the session |

### Node output

Each step in a workflow produces output by writing to session state. In Python,
a function node returns or yields an `Event(output=...)`. In Go, an
`llmagent` step writes via `OutputKey`, and a custom `Run` function writes via
`ctx.Session().State().Set`.

=== "Python"

    Use the ***return*** or ***yield*** syntax to hand off data to the next node:

    ```python
    from google.adk import Event

    def my_function_node(node_input: str):
        output_value = node_input.upper()
        return Event(output=output_value) # "THE RESULT"
    ```

    Use the ***return*** syntax when outputting ***Event*** data that does not
    require additional processing. When emitting data that requires additional
    processing, or if you are generating more than one data item, you can use
    more than one ***yield*** command. Each ***yield*** call adds to a list of
    data objects on the Event which is passed to the next node of a graph. A
    ***return*** or ***yield*** command without a parameter passes a `None` value
    to the next node.

=== "Go"

    Use `OutputKey` on `llmagent.Config` to automatically save an agent's
    response to session state. For custom `Run` functions, call
    `ctx.Session().State().Set` directly:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:output-key"
    ```

    For custom `Run` functions acting as workflow steps:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:custom-run-node"
    ```

### Node output: passing structured data

=== "Python"

    You can pass longer, structured data in a serializable format:

    ```python
    def my_function_node_3():
        yield Event(
            output={
                "city_name": "Paris",
                "city_time": "10:10 AM",
            },
        )
    ```

    !!! warning "Caution: Event.output limitation"

        Nodes are only allowed to emit a single ***Event.output*** data payload
        per execution. This limitation means that while you can use more than
        one ***yield*** in a node, having two or more ***yield*** commands with
        an ***Event.output*** results in a runtime error.

=== "Go"

    In Go, structured data is stored as separate keys in session state, each
    written by its producing step using `OutputKey` or `State().Set`. There is
    no single-payload restriction; each key is an independent write. Downstream
    agents access individual fields by placing `{key}` in their `Instruction`.

    For example, to pass both a city name and a time value to the next step:

    ```go
    // step1 writes two separate keys to state:
    //   state["city_name"] = "Paris"   (via OutputKey on an llmagent)
    //   state["city_time"] = "10:10 AM" (via OutputKey on another llmagent,
    //                                    or State().Set in a custom Run func)
    //
    // step2 reads both via its Instruction template:
    //   Instruction: "It is {city_time} in {city_name} right now."
    ```

### User-facing messages

=== "Python"

    Use the ***message*** parameter of an ***Event*** to send a response to a
    user rather than pass data to the next node:

    ```python
    async def user_message(node_input: str):
      """Tell user research process is starting."""
      yield Event(message="Beginning research process...")
    ```

=== "Go"

    In Go, a workflow step sends a user-facing message by yielding a
    `session.Event` whose `LLMResponse.Content` contains the text. The runner
    surfaces this to the caller as a normal agent response:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:message-output"
    ```

### Session state and state scopes

Session state persists data across the steps of a workflow and across turns
within a session. State key prefixes control how long values live and who can
see them.

=== "Python"

    Use the ***state*** parameter of an ***Event*** to maintain values across
    nodes. Nodes can modify state values, and the modified state values are
    available to downstream nodes:

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

    !!! warning "Caution: `state` property data limitations"

        The state parameter *should not be used to persist large amounts of
        data* between nodes. Use artifacts or other data persistence mechanisms,
        such as database Tools, to persist large data resources during the life
        cycle of a Workflow.

=== "Go"

    In Go, state is written with `ctx.Session().State().Set(key, value)` and
    read with `.Get(key)`. The `session` package defines prefix constants that
    map to the same lifetime scopes as Python's state parameter:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:state-scopes"
    ```

    !!! warning "Caution: state data limitations"

        Session state is a lightweight key-value store. Do not use it to persist
        large payloads such as file contents or binary data. Use ADK artifacts
        or external storage tools instead.

## Constrain node data with schemas

You can set input and output data schemas to constrain the data formats
accepted and produced by any agent node.

=== "Python"

    Use `input_schema` and `output_schema` with a class that extends
    ***BaseModel*** to constrain any agent's input and output:

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

=== "Go"

    In Go, schemas are defined as `*genai.Schema` values and assigned to
    `InputSchema` and `OutputSchema` on `llmagent.Config`.

    -   **`InputSchema`**: constrains what the agent accepts when called as a
        sub-agent. The caller must provide a JSON object matching this schema.
    -   **`OutputSchema`**: forces the model to reply with a JSON object matching
        the schema. When `OutputSchema` is set the agent cannot use tools.

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:input-output-schema"
    ```

## Access structured data in agents

When structured data has been written to session state by a previous step, a
downstream agent can reference it in its `Instruction` using `{key}` template
placeholders. The ADK framework substitutes the current value of `state[key]`
into the instruction before it is sent to the model.

=== "Python"

    Use the curly-brace `{ }` syntax to select properties from the input
    schema, or `< >` to select a property and also qualify it by the name
    of the source node:

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

=== "Go"

    In Go, each state key is referenced independently using `{key}` in the
    `Instruction` field. There is no class-scoped or source-node-qualified
    syntax; instead, use distinct, descriptive key names and write each value
    to its own key via `OutputKey` or `State().Set`:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:template-data-access"
    ```

For a complete, but simplified version of this workflow, see
[Graph-based agent workflows](/graphs/#get-started).
