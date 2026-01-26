# Debug Logging Plugin

The `DebugLoggingPlugin` captures detailed interaction data to a YAML file for debugging. This data includes LLM requests and responses, tool calls, events, and session state.

## Usage

To use the `DebugLoggingPlugin`, initialize it and add it to the `Runner`.

```python
from google.adk.plugins import DebugLoggingPlugin

debug_plugin = DebugLoggingPlugin(output_path="debug_logs.yaml")
runner = Runner(agent=my_agent, plugins=[debug_plugin])
```

## Output Format

The output is written in YAML format. Each invocation is appended to the file as a separate YAML document, separated by `---`. This format is human-readable and can be shared for debugging purposes.

## Configuration

You can configure the `DebugLoggingPlugin` with the following parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `output_path` | `str` | `"adk_debug.yaml"` | The path to the output file. |
| `include_session_state` | `bool` | `True` | Whether to include a snapshot of the session state at the end of each invocation. |
| `include_system_instruction` | `bool` | `True` | Whether to include the full system instructions in the log. |
