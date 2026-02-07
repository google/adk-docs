# Agent Simulator

The Agent Simulator allows you to simulate and test agent behaviors by mocking tool outputs and injecting faults (latency, errors) without invoking real tools.

## Key Features
- **Tool Mocking**: Define mock strategies (Tool Spec or Tracing) to generate tool responses.
- **Fault Injection**: Inject latency, errors, or custom responses with defined probabilities.
- **Connection Analysis**: Automatically analyze tool connections using an LLM.

## Automatic Connection Analysis
The Agent Simulator uses an LLM to analyze the schemas of your tools and identify "stateful parameters" (e.g., IDs created by one tool and used by another). This allows the simulator to maintain a consistent state across tool calls.

- **Creating Tools**: Tools that generate new resources (e.g., `create_ticket`) will have their output captured.
- **Consuming Tools**: Tools that operate on resources (e.g., `get_ticket`) will be validated against the captured state.

## Configuration
The Agent Simulator is configured using three main classes:

-   `AgentSimulatorConfig`: The main configuration for the simulator.
    -   `tool_simulation_configs`: A list of `ToolSimulationConfig` objects, one for each tool you want to simulate.
    -   `simulation_model`: The model to use for internal simulator LLM calls (tool analysis, mock responses). Defaults to "gemini-2.5-flash".
    -   `simulation_model_configuration`: The configuration for the internal simulator LLM calls.
-   `ToolSimulationConfig`: Configuration for a single tool.
    -   `tool_name`: The name of the tool to be simulated.
    -   `injection_configs`: A list of `InjectionConfig` objects to inject faults or custom responses.
    -   `mock_strategy_type`: The mock strategy to use if no injection is applied. Can be `MOCK_STRATEGY_TOOL_SPEC` or `MOCK_STRATEGY_TRACING`.
-   `InjectionConfig`: Configuration for injecting faults.
    -   `injection_probability`: The probability of the injection happening (0.0 to 1.0).
    -   `match_args`: A dictionary of arguments to match for the injection to be applied.
    -   `injected_latency_seconds`: The amount of latency to inject.
    -   `injected_error`: An `InjectedError` object to simulate an error.
    -   `injected_response`: A dictionary to be returned as the tool's output.

### Example Configuration
```python
from google.adk.tools.agent_simulator.agent_simulator_config import AgentSimulatorConfig, ToolSimulationConfig, InjectionConfig, MockStrategy, InjectedError

config = AgentSimulatorConfig(
    tool_simulation_configs=[
        ToolSimulationConfig(
            tool_name="my_tool",
            injection_configs=[
                InjectionConfig(
                    injection_probability=0.5,
                    injected_error=InjectedError(
                        injected_http_error_code=500,
                        error_message="Internal Server Error"
                    )
                )
            ],
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC
        )
    ]
)
```

## Usage
You can use the Agent Simulator as a **Plugin** or as a **Callback**.

### Using as a Plugin
```python
from google.adk.tools.agent_simulator.agent_simulator_factory import AgentSimulatorFactory
from google.adk.testing import InMemoryRunner

plugin = AgentSimulatorFactory.create_plugin(config)
runner = InMemoryRunner(agent=agent, plugins=[plugin])
```

### Using as a Callback
You can also use the simulator as a `before_tool_callback` or `after_tool_callback`.

```python
from google.adk.tools.agent_simulator.agent_simulator_factory import AgentSimulatorFactory

callback = AgentSimulatorFactory.create_callback(config)
# Pass the callback to the runner
# runner = ...
```
