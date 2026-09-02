# Environment simulation for evaluations

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.24.0</span>
</div>

When evaluating agents that rely on external dependencies — such as APIs,
databases, or third-party services — running those tools live during testing can
be slow, costly, or unreliable. The **Environment Simulator** lets you safely
intercept these tool calls during agent execution and replace them with
controlled, deterministic responses, without modifying the agent itself. This
approach can fill a critical gap in the agent improvement loop, allowing you to
create hermetic, offline test runs that isolate your agent logic for reliable
scoring.

Overall, this feature lets you:

*   Test how an agent handles API errors or edge-case responses.
*   Run evaluations offline, without access to live backends.
*   Generate realistic mock responses automatically using an LLM.
*   Produce reproducible test runs by seeding probabilistic injections.

The Environment Simulation integrates with ADK's tool execution pipeline via the
[`before_tool_callback`](/callbacks/types-of-callbacks/#tool-execution-callbacks)
hook or the [plugin system](/plugins/), so no
changes to your agent code are required.

```
The Environment Simulation is an experimental feature. Its API may change in future
releases.
```

## How it works

While [User Simulation](/evaluate/user-sim/)
drives the conversation forward, Environment Simulation provides the stable
backend. At a high level, the Environment Simulator sits between your agent and
its tools. When the agent calls a tool, the simulator intercepts the call and
decides whether to return a synthetic response — either a predefined injection
or an LLM-generated mock — or to let the real tool execute.

The decision logic follows this order for each configured tool:

1.  **Injection configs** are checked first, in order. If a matching injection
    is found (based on argument matching and probability), its error or response
    is returned immediately.
2.  **Mock strategy** is used as a fallback if no injection config applies. The
    simulator calls an LLM to generate a realistic response based on the tool's
    schema and any stateful context.
3.  **No-op** is returned (`None`) if the tool is not in the simulator config,
    allowing the real tool to execute normally.

## Integration

The `EnvironmentSimulationFactory` class provides two integration points:

*   `create_callback()` — Returns an async callable suitable for use as a
    `before_tool_callback` on any `LlmAgent`.
*   `create_plugin()` — Returns an `EnvironmentSimulationPlugin` instance that
    integrates with the ADK plugin system.

### Using as a callback

The following example shows how to create an environment simulation as one of the adk agent callbacks.


```python
--8<-- "examples/inline/python/evaluate/environment_simulation/001-using-as-a-callback.py"
```

### Using as a plugin

The following example shows how to create environment simulation as an ADK agent plugin.

```python
--8<-- "examples/inline/python/evaluate/environment_simulation/002-using-as-a-plugin.py"
```

## Configuration reference

You can configure the Environment Simulator with a set of dataclasses. The
following sections provide a detailed reference for each configuration object.

### `EnvironmentSimulationConfig`

The top-level configuration object.

Field                            | Type                         | Default              | Description
:------------------------------- | :--------------------------- | :------------------- | :----------
`tool_simulation_configs`        | `List[ToolSimulationConfig]` | required             | One entry per tool to simulate. Must not be empty, and tool names must be unique.
`simulation_model`               | `str`                        | `"gemini-flash-latest"` | The LLM used for tool connection analysis and mock response generation.
`simulation_model_configuration` | `GenerateContentConfig`      | thinking enabled     | LLM generation config for internal simulator calls.
`environment_data`               | `str \| None`                | `None`               | Optional environment context (e.g., a JSON database snapshot) passed to mock strategies to generate more realistic responses.
`tracing`                        | `str \| None`                | `None`               | Tracing data (e.g., a prior agent run trace in JSON string format) to provide historical context.

### `ToolSimulationConfig`

Defines how a single named tool should be simulated.

Field                | Type                    | Default                     | Description
:------------------- | :---------------------- | :-------------------------- | :----------
`tool_name`          | `str`                   | required                    | Must match the tool's registered name exactly.
`injection_configs`  | `List[InjectionConfig]` | `[]`                        | Zero or more injection configs, checked in order before the mock strategy.
`mock_strategy_type` | `MockStrategy`          | `MOCK_STRATEGY_UNSPECIFIED` | Fallback strategy when no injection is triggered.

### `InjectionConfig`

Controls a single synthetic response that can be injected into a tool call.
Exactly one of `injected_error` or `injected_response` must be set.

Field                      | Type                     | Default | Description
:------------------------- | :----------------------- | :------ | :----------
`injected_error`           | `InjectedError \| None`  | `None`  | Error to return (mutually exclusive with `injected_response`).
`injected_response`        | `Dict[str, Any] \| None` | `None`  | Fixed response dict to return (mutually exclusive with `injected_error`).
`injection_probability`    | `float`                  | `1.0`   | Probability `[0.0, 1.0]` that this injection fires.
`match_args`               | `Dict[str, Any] \| None` | `None`  | If set, the injection only fires when the tool's arguments contain all key-value pairs in `match_args`.
`injected_latency_seconds` | `float`                  | `0.0`   | Artificial delay (≤ 120 s) added before returning the injection result.
`random_seed`              | `int \| None`            | `None`  | Seed for the probability check, enabling deterministic injection behavior.

### `InjectedError`

Defines an HTTP-style error response.

| Field                      | Type  | Description                             |
| :------------------------- | :---- | :-------------------------------------- |
| `injected_http_error_code` | `int` | HTTP status code to surface as          |
:                            :       : `"error_code"` in the tool response.    :
| `error_message`            | `str` | Human-readable message surfaced as      |
:                            :       : `"error_message"` in the tool response. :

### `MockStrategy`

Enum controlling how the simulator generates responses when no injection fires.

| Value                     | Description                                     |
| :------------------------ | :---------------------------------------------- |
| `MOCK_STRATEGY_TOOL_SPEC` | Uses the tool's schema and stateful context to  |
:                           : prompt an LLM to generate a realistic response. :
| `MOCK_STRATEGY_TRACING`   | *(Deprecated)* Please use                       |
:                           : `MOCK_STRATEGY_TOOL_SPEC` with tracing input.   :

## Injection mode

Use injection configs to test specific failure or edge-case scenarios.
Injections are evaluated in list order; the first one whose `match_args`
criteria are met (and whose probability check passes) is applied.

### Injecting errors

The following example shows how to inject errors with specific error code and error message to the agent.

```python
--8<-- "examples/inline/python/evaluate/environment_simulation/003-injecting-errors.py"
```

The agent will receive `{"error_code": 402, "error_message": "Payment
declined."}` instead of a real tool result, allowing you to evaluate how the
agent handles payment failures.

### Injecting fixed responses

Use the following InjectionConfig to specify a success response with fixed response payload. 

```python
--8<-- "examples/inline/python/evaluate/environment_simulation/004-injecting-fixed-responses.py"
```

### Conditional injection with argument matching

Use `match_args` to inject only when specific arguments are passed.

```python
--8<-- "examples/inline/python/evaluate/environment_simulation/005-conditional-injection-with-argument-matc.py"
```

Here, the error is injected only when the tool is called with
`item_id="ITEM-404"`. All other calls pass through to the next injection config
or to the mock strategy.

### Probabilistic injection

Set `injection_probability` to a value between `0.0` and `1.0` to simulate flaky
behavior. For reproducible test runs, pin the random outcome with `random_seed`.

```python
--8<-- "examples/inline/python/evaluate/environment_simulation/006-probabilistic-injection.py"
```

### Injecting latency

Use `injected_latency_seconds` to simulate slow backend responses, useful for
testing timeout handling or user experience under degraded conditions.

```python
--8<-- "examples/inline/python/evaluate/environment_simulation/007-injecting-latency.py"
```

### Combining multiple injection configs

Multiple injection configs on a single tool are checked in order. You can
combine them to test multiple scenarios:

```python
--8<-- "examples/inline/python/evaluate/environment_simulation/008-combining-multiple-injection-configs.py"
```

## Mock strategy mode

When you want the simulator to generate plausible responses automatically —
rather than returning hand-crafted values — use `MOCK_STRATEGY_TOOL_SPEC`.

The simulator uses an LLM to:

1.  Analyze the schemas of all tools the agent has access to, and identify
    *stateful dependencies* between them (e.g., a `create_order` tool produces
    an `order_id` that `get_order` consumes).
2.  Track a **state store** of IDs and resources created during the session.
3.  Generate a response that is consistent with the tool's schema and the
    current state — returning a 404-style error if a consuming tool requests a
    resource that was never created.

```python
--8<-- "examples/inline/python/evaluate/environment_simulation/009-mock-strategy-mode.py"
```

With this config, the simulator will automatically generate an `order_id` when
`create_order` is mocked, and use it to return consistent results (or a
not-found error) when `get_order` or `cancel_order` are subsequently called.

### Providing environment data

Pass domain-specific context through `environment_data` to make mock responses
more realistic. This can be a JSON string representing a snapshot of your
database or any structured context the LLM should use when generating responses.

```python
--8<-- "examples/inline/python/evaluate/environment_simulation/010-providing-environment-data.py"
```

The LLM will use this data to return product names, prices, and stock levels
that match your domain, rather than generating arbitrary placeholder values.

### Providing tracing data

Feed traces generated in the agent to be mocked through `tracing` to make mock
responses more realistic.

```python
--8<-- "examples/inline/python/evaluate/environment_simulation/011-providing-tracing-data.py"
```

The LLM will use this data to return product names, prices, and stock levels
that match your domain, rather than generating arbitrary placeholder values.

## Mixing injections and mock strategy

Injection configs and a mock strategy can be combined on the same tool.
Injections are always checked first; the mock strategy fires only when no
injection applies.

```python
--8<-- "examples/inline/python/evaluate/environment_simulation/012-mixing-injections-and-mock-strategy.py"
```

