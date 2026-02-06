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
The Agent Simulator is configured using three main classes: `AgentSimulatorConfig`, `ToolSimulationConfig`, and `InjectionConfig`.

- `AgentSimulatorConfig`: The main configuration object for the Agent Simulator. It holds a list of `ToolSimulationConfig` objects and global settings like the simulation model.
- `ToolSimulationConfig`: Defines the simulation behavior for a specific tool, including its name, a list of `InjectionConfig` objects, and a mock strategy.
- `InjectionConfig`: Specifies the fault injection parameters for a tool, such as the probability of injection, latency, and the specific error or response to inject.

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
You can integrate the Agent Simulator into your workflow as a Plugin or a Callback.

### Using as a Plugin
To use the Agent Simulator as a plugin, create a plugin instance using `AgentSimulatorFactory.create_plugin(config)` and pass it to the runner.

```python
from google.adk.tools.agent_simulator.agent_simulator_factory import AgentSimulatorFactory
from google.adk.runners import InMemoryRunner

plugin = AgentSimulatorFactory.create_plugin(config)
runner = InMemoryRunner(agent=agent, plugins=[plugin])
```

### Using as a Callback
To use the Agent Simulator as a callback, create a callback function using `AgentSimulatorFactory.create_callback(config)`. This can be used as a `before_tool_callback` or `after_tool_callback`.

```python
from google.adk.tools.agent_simulator.agent_simulator_factory import AgentSimulatorFactory

callback = AgentSimulatorFactory.create_callback(config)
# Use the callback in your tool setup
```
