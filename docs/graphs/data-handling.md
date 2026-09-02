# Data handling for agent workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
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
events. A step writes its output to a named event field, and the next step
receives it as its typed input.

=== "Python"

    In Python, data is exchanged between graph nodes using ***Events***. The key
    parameters for node data handling are:

    -   **`output`**: Parameter for passing information between *nodes*.
    -   **`message`**: Data intended as a response to a user.
    -   **`state`**: Data automatically persisted across nodes via ***Events***
        throughout an ADK session.

=== "TypeScript"

    In ADK TypeScript v2.0.0, nodes exchange data through events. The key
    fields for node data handling are:

    -   **`output`**: the value passed to the next node. Return a value
        directly and ADK wraps it in an event, or set the field explicitly
        with `createEvent({output})`.
    -   **`content`**: a message for the user. The runtime renders this
        field, but the graph does not pass it to the next node.
    -   **`route`**: the routing keys that select which conditional edge to
        follow.

    Session state is separate from the event. A node reads and writes state
    through `ctx.state`, and the accumulated delta is attached to that
    node's events. State keys can carry a prefix that controls their
    lifetime and scope:

    | Prefix | Scope |
    |---|---|
    | `app:` | Shared across all users and sessions for the app |
    | `user:` | Tied to the user, shared across their sessions |
    | `temp:` | Discarded after the current invocation ends |
    | *(none)* | Persists for the lifetime of the session |

=== "Go"

    In ADK Go v2.0.0, the data-passing mechanism depends on which agent style
    you use:

    **workflow package** (`FunctionNode`, `AgentNode`, `DynamicNode`): nodes
    communicate through `session.Event` fields, mirroring Python closely:

    -   **`Event.Output`**: the node's return value, set automatically by the
        framework when a `FunctionNode` returns a non-`*genai.Content` value.
        The successor node receives this as its typed `input` parameter.
    -   **`Event.Routes`**: routing keys set explicitly by an emitting node to
        select which conditional edge to follow — the Go equivalent of
        Python's `Event(route=...)`.
    -   **`Event.NodeInfo`**: scheduler metadata (`path`, `MessageAsOutput`,
        `OutputFor`). Set by the workflow engine; nodes do not set this
        directly.

    **Prebuilt workflow agents** (`sequentialagent`, `parallelagent`,
    `loopagent`): these agents communicate through session state:

    -   **`OutputKey`** on `llmagent.Config`: the framework writes the agent's
        final text response to `state[OutputKey]` after each turn.
    -   **`ctx.Session().State().Set` / `.Get`**: write or read arbitrary
        values from state inside custom code.
    -   **`{key}` in `Instruction`**: the framework substitutes `state["key"]`
        into the prompt before calling the model.

    State keys may carry a prefix that controls their lifetime and scope:

    | Prefix constant | Prefix string | Scope |
    |---|---|---|
    | `session.KeyPrefixApp` | `"app:"` | Shared across all users and sessions for the app |
    | `session.KeyPrefixUser` | `"user:"` | Tied to the user, shared across their sessions |
    | `session.KeyPrefixTemp` | `"temp:"` | Discarded after the current invocation ends |
    | *(none)* | — | Persists for the lifetime of the session |

### Node output

Each step in a workflow produces output for its successor.

=== "Python"

    Use the ***return*** or ***yield*** syntax to hand off data to the next node:

    ```python
    --8<-- "examples/inline/python/graphs/data-handling/001-node-output.py"
    ```

    Use the ***return*** syntax when outputting ***Event*** data that does not
    require additional processing. When emitting data that requires additional
    processing, or if you are generating more than one data item, you can use
    more than one ***yield*** command. Each ***yield*** call adds to a list of
    data objects on the Event which is passed to the next node of a graph. A
    ***return*** or ***yield*** command without a parameter passes a `None` value
    to the next node.

=== "TypeScript"

    There are three equivalent ways to produce a node's output: return a
    value directly, return `createEvent({output})`, or yield events from an
    async generator to stream progress alongside the result.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/node_output.ts:node-output"
    ```

    !!! warning "Caution: emit `output` from one event per execution"

        A node can yield any number of events carrying `output`, and ADK
        does not raise an error in this case. Each event overwrites the
        previous one, and the successor node receives only the final value.
        Use `content` for progress messages instead.

=== "Go"

    **workflow package**: a `FunctionNode` simply returns a typed Go value.
    The framework automatically wraps the return value in a `session.Event`
    and sets `Event.Output`. The successor node receives this value as its
    typed `input` parameter — no manual event construction needed:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:event-output"
    ```

    **Prebuilt workflow agents**: use `OutputKey` on `llmagent.Config` to
    save an agent's text response to session state, then reference it with
    `{key}` in downstream agents' `Instruction` templates:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:output-key"
    ```

### Node output: passing structured data

=== "Python"

    You can pass longer, structured data in a serializable format:

    ```python
    --8<-- "examples/inline/python/graphs/data-handling/002-node-output-passing-structured-data.py"
    ```

    !!! warning "Caution: Event.output limitation"

        Nodes are only allowed to emit a single ***Event.output*** data payload
        per execution. This limitation means that while you can use more than
        one ***yield*** in a node, having two or more ***yield*** commands with
        an ***Event.output*** results in a runtime error.

=== "TypeScript"

    The `output` field is not limited to text. Any serializable value is
    passed to the next node, which receives it as a typed object, with no
    JSON parsing or state reads required. Attaching an `outputSchema` to the
    producing node, or an `inputSchema` to the consuming node, makes the
    contract explicit and validates it at runtime:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/structured_output.ts:structured-output"
    ```

=== "Go"

    **workflow package**: a `FunctionNode` can return any JSON-serializable
    Go struct. The framework serializes it into `Event.Output` and
    deserializes it back into the successor node's typed `input` parameter.
    There is no single-payload restriction — each node has exactly one typed
    return value:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:structured-output"
    ```

    **Prebuilt workflow agents**: use multiple `OutputKey` values, one per
    agent, to store individual fields in session state. Downstream agents
    read each field independently via `{key}` in their `Instruction`.

### Routing output

=== "Python"

    Use the `route` parameter of an ***Event*** to drive conditional edge
    dispatch:

    ```python
    --8<-- "examples/inline/python/graphs/data-handling/003-routing-output.py"
    ```

=== "TypeScript"

    The `route` value is independent of `output`, so one event can both
    select a branch and forward a payload to it. The `DEFAULT_ROUTE` setting
    catches any value that no other branch matched:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/routing_output.ts:routing-output"
    ```

=== "Go"

    **workflow package**: an emitting `FunctionNode` constructs a
    `session.Event` directly, sets `Event.Routes` to the desired route keys,
    and sets `Event.Output` to forward the payload to the successor. The
    workflow engine reads `Event.Routes` at dispatch time to select the
    matching edge:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:routing-output"
    ```

### User-facing messages

=== "Python"

    Use the ***message*** parameter of an ***Event*** to send a response to a
    user rather than pass data to the next node:

    ```python
    --8<-- "examples/inline/python/graphs/data-handling/004-user-facing-messages.py"
    ```

=== "TypeScript"

    A message for the user is the event's `content` field. The runtime
    renders `content`, but the graph does not pass it to the next node. Use
    `content` for the user and `output` for the next node. A node can emit
    both by sending two events, where only one carries `output`:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/user_message.ts:user-message"
    ```

=== "Go"

    **workflow package**: to emit a user-visible message without advancing
    the node's typed output, set `Event.Content` on an intermediate event
    emitted via the `emit` callback in an `EmittingFunctionNode`. The
    terminal return value (or `nil`) controls `Event.Output`.

    **Prebuilt workflow agents**: any `llmagent` step automatically emits its
    model response as a user-facing event. For non-LLM steps, write a custom
    `Run` function on an `agent.Agent` that yields events whose
    `LLMResponse.Content` contains the text.

### Session state and state scopes

Session state persists data across turns within a session. It is the primary
data-sharing mechanism for the prebuilt workflow agents, and is also available
inside tools and callbacks regardless of which agent style you use.

=== "Python"

    Use the ***state*** parameter of an ***Event*** to maintain values across
    nodes. Nodes can modify state values, and the modified state values are
    available to downstream nodes:

    ```python
    --8<-- "examples/inline/python/graphs/data-handling/005-session-state-and-state-scopes.py"
    ```

    !!! warning "Caution: `state` property data limitations"

        The state parameter *should not be used to persist large amounts of
        data* between nodes. Use artifacts or other data persistence mechanisms,
        such as database Tools, to persist large data resources during the life
        cycle of a Workflow.

=== "TypeScript"

    Write state through `ctx.state` rather than returning it. A write is
    visible to every later node in the same run, and is committed with the
    writing node's events:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/session_state.ts:session-state"
    ```

    !!! warning "Caution: `state` data limitations"

        Session state is a lightweight key-value store. Do not use it to
        move large payloads between nodes; use artifacts or a database tool
        instead. When only the next node needs a value, pass it along the
        edge as node `output`. Use state when a value must outlive the run,
        or be read by a tool, a callback, or `{key}` instruction templating.

=== "Go"

    State is written with `ctx.Session().State().Set(key, value)` and read
    with `.Get(key)`. The `session` package defines prefix constants that map
    to the same lifetime scopes as Python's state parameter. This pattern
    applies to prebuilt workflow agents and to tools and callbacks in any
    agent style:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:state-scopes"
    ```

    !!! warning "Caution: state data limitations"

        Session state is a lightweight key-value store. Do not use it to persist
        large payloads such as file contents or binary data. Use ADK artifacts
        or external storage tools instead.

    !!! tip "workflow package: prefer Event.Output over state"

        For the `workflow` package (`FunctionNode`, `AgentNode`, `DynamicNode`),
        pass data between nodes by returning typed values — the framework sets
        `Event.Output` automatically. Only use `State().Set` when you need to
        share values with tools, callbacks, or agent `Instruction` templates.

## Constrain node data with schemas

You can set input and output data schemas to constrain the data formats
accepted and produced by any agent node.

=== "Python"

    Use `input_schema` and `output_schema` with a class that extends
    ***BaseModel*** to constrain any agent's input and output:

    ```python
    --8<-- "examples/inline/python/graphs/data-handling/006-constrain-node-data-with-schemas.py"
    ```

=== "TypeScript"

    Schemas are Zod objects or a genai `Schema`. The location of the schema
    determines its effect:

    -   The `LlmAgent.outputSchema` option requires the model to answer in
        that shape.
    -   The `LlmAgent.inputSchema` option applies only when the agent is
        exposed as a tool. Inside a graph, set the schema that validates a
        node's input on the node itself, using `node(agent, {inputSchema})`.

    Agents in a graph must run in `single_turn` mode, which is the default,
    or `task` mode.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/schemas.ts:schemas"
    ```

=== "Go"

    **workflow package**: use `workflow.NewAgentNodeTyped[Input, Output]` to
    attach schemas to an agent node. The generic type parameters are reflected
    into `*jsonschema.Schema` automatically — no hand-built schema construction
    needed. The node's `Event.Output` carries the structured result to the
    successor — no `OutputKey` or state write is needed:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:input-output-schema"
    ```

    **Prebuilt workflow agents**: set `InputSchema` and `OutputSchema` on
    `llmagent.Config`. `OutputSchema` forces the model to reply with a JSON
    object matching the schema (the agent cannot use tools when `OutputSchema`
    is set). Use `OutputKey` to save the JSON string to state for downstream
    agents to reference via `{key}` in their `Instruction`.

## Access structured data in agents

=== "Python"

    Use the curly-brace `{ }` syntax to select properties from the input
    schema, or `< >` to select a property and also qualify it by the name
    of the source node:

    ```python
    --8<-- "examples/inline/python/graphs/data-handling/007-access-structured-data-in-agents.py"
    ```

=== "TypeScript"

    Two data-selection forms are available inside an agent instruction:

    -   The `{Class.field}` form reads a field from this node's input.
    -   The `<Class.field from source_node>` form reads a field from a named
        predecessor's output. Use this form when several upstream nodes
        share a field name.

    Both forms are distinct from `{state_key}`, which reads session state.
    The `Class.` prefix is documentation only; resolution uses the field
    name after the dot.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/structured_access.ts:structured-access"
    ```

=== "Go"

    In ADK Go v2.0.0, a `FunctionNode` returns a typed struct and the
    framework serializes it into `Event.Output`. The successor `AgentNode`
    receives the struct as its user content — the fields are available to the
    agent's `Instruction` without any `{key}` template syntax. This is the
    direct equivalent of Python's `input_schema=CityTime` with
    `{CityTime.time_info}` template placeholders: the struct fields are
    delivered as typed input rather than looked up by name from state.

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:structured-output"
    ```

For a complete example of this workflow, see
[Graph-based agent workflows](/graphs/#get-started).
