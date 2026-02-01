---
title: Debug Logging
---

The `DebugLoggingPlugin` captures detailed interaction data to a YAML file for debugging.

## Overview

The `DebugLoggingPlugin` is a tool for developers to capture detailed data from an agent's interactions. This data includes LLM (Large Language Model) requests and responses, tool calls, events, and the agent's session state. The plugin saves this information in a human-readable YAML file, which can be used for debugging and analyzing the agent's behavior.

## Usage

To use the `DebugLoggingPlugin`, you need to import it and add it to the list of plugins when you create a `Runner`.

```python
from google.adk.plugins import DebugLoggingPlugin

debug_plugin = DebugLoggingPlugin(output_path="debug_logs.yaml")
runner = Runner(agent=my_agent, plugins=[debug_plugin])
```

## Output Format

The output is a YAML file where each invocation is a separate document, separated by `---`. This format makes it easy to read and share for debugging.

## Configuration

You can configure the `DebugLoggingPlugin` with the following parameters:

| Parameter | Description |
| :--- | :--- |
| `output_path` | The path to the output file. The default is `adk_debug.yaml`. |
| `include_session_state` | A boolean that determines whether to include the session state in the output. |
| `include_system_instruction` | A boolean that determines whether to include system instructions in the output. |

