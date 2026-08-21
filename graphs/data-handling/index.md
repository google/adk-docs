# Data handling for agent workflows

Supported in ADKPython v2.0.0Go v2.0.0

Structuring and managing data between agents and graph-based nodes is critical for building reliable processes with ADK. This guide explains data handling within graph-based workflows and collaboration agents, including how information is transmitted and received between graph nodes. It covers the essential parameters for passing data, content, and state, and explains how to implement structured data transfer for both function and agent nodes using data format schemas and specific instruction syntax.

## Workflow data flow

Within a graph-based workflow, nodes pass data to downstream steps through events. A step writes its output to a named event field, and the next step receives it as its typed input.

In Python, data is exchanged between graph nodes using ***Events***. The key parameters for node data handling are:

- **`output`**: Parameter for passing information between *nodes*.
- **`message`**: Data intended as a response to a user.
- **`state`**: Data automatically persisted across nodes via ***Events*** throughout an ADK session.

In ADK Go v2.0.0, the data-passing mechanism depends on which agent style you use:

**workflow package** (`FunctionNode`, `AgentNode`, `DynamicNode`): nodes communicate through `session.Event` fields, mirroring Python closely:

- **`Event.Output`**: the node's return value, set automatically by the framework when a `FunctionNode` returns a non-`*genai.Content` value. The successor node receives this as its typed `input` parameter.
- **`Event.Routes`**: routing keys set explicitly by an emitting node to select which conditional edge to follow — the Go equivalent of Python's `Event(route=...)`.
- **`Event.NodeInfo`**: scheduler metadata (`path`, `MessageAsOutput`, `OutputFor`). Set by the workflow engine; nodes do not set this directly.

**Prebuilt workflow agents** (`sequentialagent`, `parallelagent`, `loopagent`): these agents communicate through session state:

- **`OutputKey`** on `llmagent.Config`: the framework writes the agent's final text response to `state[OutputKey]` after each turn.
- **`ctx.Session().State().Set` / `.Get`**: write or read arbitrary values from state inside custom code.
- **`{key}` in `Instruction`**: the framework substitutes `state["key"]` into the prompt before calling the model.

State keys may carry a prefix that controls their lifetime and scope:

| Prefix constant         | Prefix string | Scope                                            |
| ----------------------- | ------------- | ------------------------------------------------ |
| `session.KeyPrefixApp`  | `"app:"`      | Shared across all users and sessions for the app |
| `session.KeyPrefixUser` | `"user:"`     | Tied to the user, shared across their sessions   |
| `session.KeyPrefixTemp` | `"temp:"`     | Discarded after the current invocation ends      |
| *(none)*                | —             | Persists for the lifetime of the session         |

### Node output

Each step in a workflow produces output for its successor.

Use the ***return*** or ***yield*** syntax to hand off data to the next node:

```python
from google.adk import Event

def my_function_node(node_input: str):
    output_value = node_input.upper()
    return Event(output=output_value) # "THE RESULT"
```

Use the ***return*** syntax when outputting ***Event*** data that does not require additional processing. When emitting data that requires additional processing, or if you are generating more than one data item, you can use more than one ***yield*** command. Each ***yield*** call adds to a list of data objects on the Event which is passed to the next node of a graph. A ***return*** or ***yield*** command without a parameter passes a `None` value to the next node.

**workflow package**: a `FunctionNode` simply returns a typed Go value. The framework automatically wraps the return value in a `session.Event` and sets `Event.Output`. The successor node receives this value as its typed `input` parameter — no manual event construction needed:

```go
// newEventOutputPipeline demonstrates the primary data-passing mechanism for
// workflow package nodes: a FunctionNode returns a typed Go value, and the
// framework automatically sets event.Output to that value. The successor node
// receives it as its typed `input` parameter.
//
// This mirrors the Python pattern exactly:
//
//  def my_function_node(node_input: str):
//      return Event(output=node_input.upper())
//
// In Go, the function simply returns the value — no Event construction needed.
func newEventOutputPipeline() (agent.Agent, error) {
    upperFn := func(_ agent.Context, input string) (string, error) {
        return strings.ToUpper(input), nil
    }

    suffixFn := func(_ agent.Context, input string) (string, error) {
        return input + " IS AWESOME!", nil
    }

    nodeA := workflow.NewFunctionNode("upper", upperFn, workflow.NodeConfig{})
    nodeB := workflow.NewFunctionNode("suffix", suffixFn, workflow.NodeConfig{})

    // workflow.Chain wires START → nodeA → nodeB. The output of nodeA is
    // delivered as the typed input of nodeB via event.Output.
    return workflowagent.New(workflowagent.Config{
        Name:        "event_output_pipeline",
        Description: "Demonstrates Event.Output data flow between FunctionNodes.",
        Edges:       workflow.Chain(workflow.Start, nodeA, nodeB),
    })
}
```

**Prebuilt workflow agents**: use `OutputKey` on `llmagent.Config` to save an agent's text response to session state, then reference it with `{key}` in downstream agents' `Instruction` templates:

```go
// newOutputKeyPipeline demonstrates the OutputKey mechanism for the prebuilt
// sequentialagent. When OutputKey is set on an llmagent.Config, the framework
// automatically writes the agent's final text response to session state under
// that key. Downstream agents read it by referencing {key} in their Instruction.
//
// This pattern applies to sequentialagent / parallelagent / loopagent.
// For the workflow package (FunctionNode / AgentNode), use Event.Output instead.
func newOutputKeyPipeline(ctx context.Context, geminiModel model.LLM) (agent.Agent, error) {
    step1, err := llmagent.New(llmagent.Config{
        Name:        "step_1",
        Model:       geminiModel,
        Description: "Transforms the user's text.",
        Instruction: "Convert the user's message to uppercase. Output only the transformed text.",
        OutputKey:   "upper_result",
    })
    if err != nil {
        return nil, fmt.Errorf("step1: %w", err)
    }

    step2, err := llmagent.New(llmagent.Config{
        Name:        "step_2",
        Model:       geminiModel,
        Description: "Reports the transformed text.",
        Instruction: "The transformed text is: {upper_result}. Report it to the user.",
    })
    if err != nil {
        return nil, fmt.Errorf("step2: %w", err)
    }

    return sequentialagent.New(sequentialagent.Config{
        AgentConfig: agent.Config{
            Name:      "output_key_pipeline",
            SubAgents: []agent.Agent{step1, step2},
        },
    })
}
```

### Node output: passing structured data

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

Caution: Event.output limitation

Nodes are only allowed to emit a single ***Event.output*** data payload per execution. This limitation means that while you can use more than one ***yield*** in a node, having two or more ***yield*** commands with an ***Event.output*** results in a runtime error.

**workflow package**: a `FunctionNode` can return any JSON-serializable Go struct. The framework serializes it into `Event.Output` and deserializes it back into the successor node's typed `input` parameter. There is no single-payload restriction — each node has exactly one typed return value:

```go
// newStructuredOutputPipeline shows how to pass a struct from one FunctionNode
// to another. The framework serialises the return value into event.Output and
// deserialises it back into the successor's typed input parameter.
//
// This is the Go equivalent of:
//
//  class CityTime(BaseModel):
//      time_info: str
//      city: str
//
//  def lookup_time_function(city: str):
//      return Event(output=CityTime(time_info="10:10 AM", city=city))
//
//  def city_report(node_input: CityTime):
//      return Event(output=f"It is {node_input.time_info} in {node_input.city}.")
type CityTime struct {
    TimeInfo string `json:"time_info"`
    City     string `json:"city"`
}

func newStructuredOutputPipeline(ctx context.Context, geminiModel model.LLM) (agent.Agent, error) {
    lookupTimeFn := func(_ agent.Context, city string) (CityTime, error) {
        // Simulate looking up the current time in the city.
        return CityTime{TimeInfo: "10:10 AM", City: city}, nil
    }

    cityReportAgent, err := llmagent.New(llmagent.Config{
        Name:        "city_report_agent",
        Model:       geminiModel,
        Description: "Reports the city and current time from the previous node's output.",
        // When wrapped as an AgentNode, the predecessor's event.Output
        // is delivered as the agent's user content. The {key} template
        // syntax is not required — the struct fields are provided inline.
        Instruction: "Report the city time information you received in a friendly sentence.",
    })
    if err != nil {
        return nil, fmt.Errorf("cityReportAgent: %w", err)
    }

    lookupTimeNode := workflow.NewFunctionNode("lookup_time", lookupTimeFn, workflow.NodeConfig{})
    cityReportNode, err := workflow.NewAgentNode(cityReportAgent, workflow.NodeConfig{})
    if err != nil {
        return nil, fmt.Errorf("NewAgentNode: %w", err)
    }

    return workflowagent.New(workflowagent.Config{
        Name:      "city_time_pipeline",
        Edges:     workflow.Chain(workflow.Start, lookupTimeNode, cityReportNode),
        SubAgents: []agent.Agent{cityReportAgent},
    })
}
```

**Prebuilt workflow agents**: use multiple `OutputKey` values, one per agent, to store individual fields in session state. Downstream agents read each field independently via `{key}` in their `Instruction`.

### Routing output

Use the `route` parameter of an ***Event*** to drive conditional edge dispatch:

```python
def router(node_input: str):
    return Event(route="BUG")
```

**workflow package**: an emitting `FunctionNode` constructs a `session.Event` directly, sets `Event.Routes` to the desired route keys, and sets `Event.Output` to forward the payload to the successor. The workflow engine reads `Event.Routes` at dispatch time to select the matching edge:

```go
// classifyAndRoute shows how to set event.Routes alongside event.Output from
// an emitting FunctionNode. The function constructs a session.Event directly,
// sets Routes to select the conditional edge, and sets Output to forward the
// payload to the successor node.
//
// This mirrors the Python pattern:
//
//  def router(node_input: str):
//      return Event(route="BUG")
func classifyAndRoute(ctx agent.Context, msg string, emit func(*session.Event) error) (any, error) {
    category := classifyMessage(msg)

    ev := session.NewEvent(ctx, ctx.InvocationID())
    ev.Routes = []string{category} // drives edge dispatch
    ev.Output = msg                // forwarded as typed input to the successor
    if err := emit(ev); err != nil {
        return nil, err
    }
    return nil, nil // nil suppresses the automatic terminal event
}

func classifyMessage(msg string) string {
    switch {
    case strings.Contains(strings.ToLower(msg), "bug"):
        return "BUG"
    case strings.Contains(strings.ToLower(msg), "help"):
        return "CUSTOMER_SUPPORT"
    default:
        return "LOGISTICS"
    }
}

func newRoutingPipeline() (agent.Agent, error) {
    classifyNode := workflow.NewEmittingFunctionNode("classify", classifyAndRoute, workflow.NodeConfig{})

    bugHandler := workflow.NewFunctionNode("bug_handler",
        func(_ agent.Context, msg string) (string, error) {
            return "Handling bug: " + msg, nil
        }, workflow.NodeConfig{})

    supportHandler := workflow.NewFunctionNode("support_handler",
        func(_ agent.Context, msg string) (string, error) {
            return "Handling support: " + msg, nil
        }, workflow.NodeConfig{})

    logisticsHandler := workflow.NewFunctionNode("logistics_handler",
        func(_ agent.Context, msg string) (string, error) {
            return "Handling logistics: " + msg, nil
        }, workflow.NodeConfig{})

    edges := workflow.Concat(
        workflow.Chain(workflow.Start, classifyNode),
        []workflow.Edge{
            {From: classifyNode, To: bugHandler, Route: workflow.StringRoute("BUG")},
            {From: classifyNode, To: supportHandler, Route: workflow.StringRoute("CUSTOMER_SUPPORT")},
            {From: classifyNode, To: logisticsHandler, Route: workflow.StringRoute("LOGISTICS")},
        },
    )
    return workflowagent.New(workflowagent.Config{
        Name:        "routing_pipeline",
        Description: "Classifies and routes a message using Event.Routes.",
        Edges:       edges,
    })
}
```

### User-facing messages

Use the ***message*** parameter of an ***Event*** to send a response to a user rather than pass data to the next node:

```python
async def user_message(node_input: str):
  """Tell user research process is starting."""
  yield Event(message="Beginning research process...")
```

**workflow package**: to emit a user-visible message without advancing the node's typed output, set `Event.Content` on an intermediate event emitted via the `emit` callback in an `EmittingFunctionNode`. The terminal return value (or `nil`) controls `Event.Output`.

**Prebuilt workflow agents**: any `llmagent` step automatically emits its model response as a user-facing event. For non-LLM steps, write a custom `Run` function on an `agent.Agent` that yields events whose `LLMResponse.Content` contains the text.

### Session state and state scopes

Session state persists data across turns within a session. It is the primary data-sharing mechanism for the prebuilt workflow agents, and is also available inside tools and callbacks regardless of which agent style you use.

Use the ***state*** parameter of an ***Event*** to maintain values across nodes. Nodes can modify state values, and the modified state values are available to downstream nodes:

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

State is written with `ctx.Session().State().Set(key, value)` and read with `.Get(key)`. The `session` package defines prefix constants that map to the same lifetime scopes as Python's state parameter. This pattern applies to prebuilt workflow agents and to tools and callbacks in any agent style:

```go
// stateScopes shows how session-state key prefixes control the lifetime and
// visibility of stored values. This pattern applies to the prebuilt workflow
// agents (sequentialagent / parallelagent / loopagent) and to tools and
// callbacks. For the workflow package (FunctionNode / AgentNode), prefer
// returning values directly via Event.Output.
//
// Available prefixes:
//
//  session.KeyPrefixApp  ("app:")  – shared across all users and sessions
//  session.KeyPrefixUser ("user:") – tied to the user, shared across sessions
//  session.KeyPrefixTemp ("temp:") – discarded after the current invocation
//
// Keys with no prefix persist for the lifetime of the session.
func stateScopes(ctx agent.Context) error {
    st := ctx.Session().State()

    // Session-scoped (no prefix) — persists for the life of this session.
    if err := st.Set("attempts", 0); err != nil {
        return fmt.Errorf("state.Set attempts: %w", err)
    }

    // App-scoped — shared across all users and sessions for this app.
    if err := st.Set(session.KeyPrefixApp+"global_counter", 42); err != nil {
        return fmt.Errorf("state.Set app:global_counter: %w", err)
    }

    // User-scoped — shared across all sessions belonging to this user.
    if err := st.Set(session.KeyPrefixUser+"login_count", 1); err != nil {
        return fmt.Errorf("state.Set user:login_count: %w", err)
    }

    // Temp-scoped — discarded after this invocation ends.
    if err := st.Set(session.KeyPrefixTemp+"scratch", "ephemeral"); err != nil {
        return fmt.Errorf("state.Set temp:scratch: %w", err)
    }

    return nil
}
```

Caution: state data limitations

Session state is a lightweight key-value store. Do not use it to persist large payloads such as file contents or binary data. Use ADK artifacts or external storage tools instead.

workflow package: prefer Event.Output over state

For the `workflow` package (`FunctionNode`, `AgentNode`, `DynamicNode`), pass data between nodes by returning typed values — the framework sets `Event.Output` automatically. Only use `State().Set` when you need to share values with tools, callbacks, or agent `Instruction` templates.

## Constrain node data with schemas

You can set input and output data schemas to constrain the data formats accepted and produced by any agent node.

Use `input_schema` and `output_schema` with a class that extends ***BaseModel*** to constrain any agent's input and output:

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

**workflow package**: use `workflow.NewAgentNodeTyped[Input, Output]` to attach schemas to an agent node. The generic type parameters are reflected into `*jsonschema.Schema` automatically — no hand-built schema construction needed. The node's `Event.Output` carries the structured result to the successor — no `OutputKey` or state write is needed:

```go
// FlightSearchInput is the typed input schema for the flight-search agent node.
// workflow.NewAgentNodeTyped[FlightSearchInput, FlightSearchOutput] reflects
// these structs into *jsonschema.Schema automatically — no hand-built schema
// construction needed.
type FlightSearchInput struct {
    Origin        string `json:"origin"         jsonschema:"Departure airport code e.g. SFO"`
    Destination   string `json:"destination"    jsonschema:"Arrival airport code e.g. CDG"`
    DepartureDate string `json:"departure_date" jsonschema:"Travel date in YYYY-MM-DD format"`
}

// FlightSearchOutput is the typed output schema for the flight-search agent node.
type FlightSearchOutput struct {
    CheapestPrice string `json:"cheapest_price" jsonschema:"Cheapest available fare e.g. $450"`
    FlightCount   string `json:"flight_count"   jsonschema:"Number of matching flights found"`
}

// newSchemaAgentPipeline demonstrates workflow.NewAgentNodeTyped, which infers
// *jsonschema.Schema from the generic type parameters. This is the Go equivalent
// of Python's:
//
//  flight_searcher = Agent(
//      input_schema=FlightSearchInput,
//      output_schema=FlightSearchOutput,
//      ...
//  )
//
// The node's event.Output carries the structured result to the successor —
// no OutputKey or state write is needed.
func newSchemaAgentPipeline(ctx context.Context, geminiModel model.LLM) (agent.Agent, error) {
    flightSearchAgent, err := llmagent.New(llmagent.Config{
        Name:        "flight_searcher",
        Model:       geminiModel,
        Description: "Searches for available flights and returns structured results.",
        Instruction: `You are a flight-search assistant. Respond ONLY with a JSON object.`,
    })
    if err != nil {
        return nil, fmt.Errorf("flightSearchAgent: %w", err)
    }

    synthAgent, err := llmagent.New(llmagent.Config{
        Name:        "trip_assistant",
        Model:       geminiModel,
        Description: "Summarises flight search results for the user.",
        Instruction: `You help users plan trips. Summarise the flight result you received.`,
    })
    if err != nil {
        return nil, fmt.Errorf("synthAgent: %w", err)
    }

    // NewAgentNodeTyped[In, Out] reflects FlightSearchInput and FlightSearchOutput
    // into *jsonschema.Schema automatically. The node enforces the input schema
    // and constrains the model reply to the output schema's shape.
    flightNode, err := workflow.NewAgentNodeTyped[FlightSearchInput, FlightSearchOutput](flightSearchAgent, workflow.NodeConfig{})
    if err != nil {
        return nil, fmt.Errorf("flightNode: %w", err)
    }

    synthNode, err := workflow.NewAgentNode(synthAgent, workflow.NodeConfig{})
    if err != nil {
        return nil, fmt.Errorf("synthNode: %w", err)
    }

    return workflowagent.New(workflowagent.Config{
        Name:      "flight_booking_pipeline",
        Edges:     workflow.Chain(workflow.Start, flightNode, synthNode),
        SubAgents: []agent.Agent{flightSearchAgent, synthAgent},
    })
}
```

**Prebuilt workflow agents**: set `InputSchema` and `OutputSchema` on `llmagent.Config`. `OutputSchema` forces the model to reply with a JSON object matching the schema (the agent cannot use tools when `OutputSchema` is set). Use `OutputKey` to save the JSON string to state for downstream agents to reference via `{key}` in their `Instruction`.

## Access structured data in agents

Use the curly-brace `{ }` syntax to select properties from the input schema, or `< >` to select a property and also qualify it by the name of the source node:

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

In ADK Go v2.0.0, a `FunctionNode` returns a typed struct and the framework serializes it into `Event.Output`. The successor `AgentNode` receives the struct as its user content — the fields are available to the agent's `Instruction` without any `{key}` template syntax. This is the direct equivalent of Python's `input_schema=CityTime` with `{CityTime.time_info}` template placeholders: the struct fields are delivered as typed input rather than looked up by name from state.

```go
// newStructuredOutputPipeline shows how to pass a struct from one FunctionNode
// to another. The framework serialises the return value into event.Output and
// deserialises it back into the successor's typed input parameter.
//
// This is the Go equivalent of:
//
//  class CityTime(BaseModel):
//      time_info: str
//      city: str
//
//  def lookup_time_function(city: str):
//      return Event(output=CityTime(time_info="10:10 AM", city=city))
//
//  def city_report(node_input: CityTime):
//      return Event(output=f"It is {node_input.time_info} in {node_input.city}.")
type CityTime struct {
    TimeInfo string `json:"time_info"`
    City     string `json:"city"`
}

func newStructuredOutputPipeline(ctx context.Context, geminiModel model.LLM) (agent.Agent, error) {
    lookupTimeFn := func(_ agent.Context, city string) (CityTime, error) {
        // Simulate looking up the current time in the city.
        return CityTime{TimeInfo: "10:10 AM", City: city}, nil
    }

    cityReportAgent, err := llmagent.New(llmagent.Config{
        Name:        "city_report_agent",
        Model:       geminiModel,
        Description: "Reports the city and current time from the previous node's output.",
        // When wrapped as an AgentNode, the predecessor's event.Output
        // is delivered as the agent's user content. The {key} template
        // syntax is not required — the struct fields are provided inline.
        Instruction: "Report the city time information you received in a friendly sentence.",
    })
    if err != nil {
        return nil, fmt.Errorf("cityReportAgent: %w", err)
    }

    lookupTimeNode := workflow.NewFunctionNode("lookup_time", lookupTimeFn, workflow.NodeConfig{})
    cityReportNode, err := workflow.NewAgentNode(cityReportAgent, workflow.NodeConfig{})
    if err != nil {
        return nil, fmt.Errorf("NewAgentNode: %w", err)
    }

    return workflowagent.New(workflowagent.Config{
        Name:      "city_time_pipeline",
        Edges:     workflow.Chain(workflow.Start, lookupTimeNode, cityReportNode),
        SubAgents: []agent.Agent{cityReportAgent},
    })
}
```

For a complete example of this workflow, see [Graph-based agent workflows](/graphs/#get-started).
