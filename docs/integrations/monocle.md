---
catalog_title: Monocle
catalog_description: Open-source observability, tracing, and debugging of LLM applications
catalog_icon: /adk-docs/integrations/assets/monocle.png
catalog_tags: ["observability"]
---

# Monocle observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Monocle](https://github.com/monocle2ai/monocle) is an open-source observability platform for monitoring, debugging, and improving LLM applications and AI Agents. It provides comprehensive tracing capabilities for your Google ADK applications through automatic instrumentation. Monocle generates OpenTelemetry-compatible traces that can be exported to various destinations including local files or console output.

## Overview

Monocle automatically instruments Google ADK applications, allowing you to:

- **Trace agent interactions** - Automatically capture every agent run, tool call, and model request with full context and metadata
- **Monitor execution flow** - Track agent state, delegation events, and execution flow through detailed traces
- **Debug issues** - Analyze detailed traces to quickly identify bottlenecks, failed tool calls, and unexpected agent behavior
- **Flexible export options** - Export traces to local files or console for analysis
- **OpenTelemetry compatible** - Generate standard OpenTelemetry traces that work with any OTLP-compatible backend

Monocle automatically instruments the following Google ADK components:

- **`BaseAgent.run_async`** - Captures agent execution, agent state, and delegation events
- **`FunctionTool.run_async`** - Captures tool execution, including tool name, parameters, and results
- **`Runner.run_async`** - Captures runner execution, including request context and execution flow

## Installation

### 1. Install Required Packages { #install-required-packages }

```bash
pip install monocle_apptrace google-adk
```

## Setup

### 1. Configure Monocle Telemetry { #configure-monocle-telemetry }

Monocle automatically instruments Google ADK when you initialize telemetry. Simply call `setup_monocle_telemetry()` at the start of your application:

```python
from monocle_apptrace import setup_monocle_telemetry

# Initialize Monocle telemetry - automatically instruments Google ADK
setup_monocle_telemetry(workflow_name="my-adk-app")
```

That's it! Monocle will automatically detect and instrument your Google ADK agents, tools, and runners.

### 2. Configure Exporters (Optional) { #configure-exporters }

By default, Monocle exports traces to local JSON files. You can configure different exporters using environment variables.

#### Export to Console (for debugging)

Set the environment variable:

```bash
export MONOCLE_EXPORTER="console"
```

#### Export to Local Files (default)

```bash
export MONOCLE_EXPORTER="file"
```

Or simply omit the `MONOCLE_EXPORTER` variable - it defaults to `file`.

## Observe

Now that you have tracing setup, all Google ADK SDK requests will be automatically traced by Monocle.

```python
from monocle_apptrace import setup_monocle_telemetry
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Initialize Monocle telemetry - must be called before using ADK
setup_monocle_telemetry(workflow_name="weather_app")

# Define a tool function
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }

# Create an agent with tools
agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash-exp",
    description="Agent to answer questions using weather tools.",
    instruction="You must use the available tools to find an answer.",
    tools=[get_weather]
)

app_name = "weather_app"
user_id = "test_user"
session_id = "test_session"
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id
)

# Run the agent (all interactions will be automatically traced)
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[
        types.Part(text="What is the weather in New York?")]
    )
):
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## Accessing Traces

By default, Monocle generates traces in JSON files in the local directory `./monocle`. The file name format is:

```
monocle_trace_{workflow_name}_{trace_id}_{timestamp}.json
```

Each trace file contains an array of OpenTelemetry-compatible spans that capture:

- **Agent execution spans** - Agent state, delegation events, and execution flow
- **Tool execution spans** - Tool name, input parameters, and output results
- **LLM interaction spans** - Model calls, prompts, responses, and token usage (if using Gemini or other LLMs)

You can analyze these trace files using any OpenTelemetry-compatible tool or write custom analysis scripts.

## Visualizing Traces with VS Code Extension

The [Okahu Trace Visualizer](https://marketplace.visualstudio.com/items?itemName=OkahuAI.okahu-ai-observability) VS Code extension provides an interactive way to visualize and analyze Monocle-generated traces directly in Visual Studio Code.

### Installation

1. Open VS Code
2. Press `Ctrl+P` (or `Cmd+P` on Mac) to open Quick Open
3. Paste the following command and press Enter:

```
ext install OkahuAI.okahu-ai-observability
```

Alternatively, you can install it from the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=OkahuAI.okahu-ai-observability).

### Features

The extension provides:

- **Custom Activity Bar Panel** - Dedicated sidebar for trace file management
- **Interactive File Tree** - Browse and select trace files with custom React UI
- **Split View Analysis** - Gantt chart visualization alongside JSON data viewer
- **Real-time Communication** - Seamless data flow between VS Code and React components
- **VS Code Theming** - Fully integrated with VS Code's light/dark themes

### Usage

1. After running your ADK application with Monocle tracing enabled, trace files will be generated in the `./monocle` directory
2. Open the Okahu Trace Visualizer panel from the VS Code Activity Bar
3. Browse and select trace files from the interactive file tree
4. View your traces with:
   - **Gantt chart visualization** - See the timeline and hierarchy of spans
   - **JSON data viewer** - Inspect detailed span attributes and events
   - **Token counts** - View token usage for LLM calls
   - **Error badges** - Quickly identify failed operations

![Monocle VS Code Extension](../assets/monocle-vs-code-ext.png)

## What Gets Traced

Monocle automatically captures the following information from Google ADK:

- **Agent Execution**: Agent state, delegation events, and execution flow
- **Tool Calls**: Tool name, input parameters, and output results
- **Runner Execution**: Request context and overall execution flow
- **Timing Information**: Start time, end time, and duration for each operation
- **Error Information**: Exceptions and error states

All traces are generated in OpenTelemetry format, making them compatible with any OTLP-compatible observability backend.

## Support and Resources

- [Monocle Documentation](https://docs.okahu.ai/monocle_overview/)
- [Monocle GitHub Repository](https://github.com/monocle2ai/monocle)
- [Google ADK Travel Agent Example](https://github.com/okahu-demos/adk-travel-agent)
- [Discord Community](https://discord.gg/D8vDbSUhJX)
