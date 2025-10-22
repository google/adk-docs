# Reflect and Retry Tool Plugin

The `ReflectAndRetryToolPlugin` provides self-healing, concurrent-safe error recovery for tool failures.

**Key Features:**
- **Concurrency Safe**: Uses locking to safely handle parallel tool executions.
- **Configurable Scope**: Tracks failures per-invocation (default) or globally.
- **Granular Tracking**: Failure counts are tracked per-tool.
- **Custom Error Extraction**: Supports detecting errors in normal tool responses.

## Basic Usage

The following example shows how to use the plugin to retry a tool that can fail.

```python
from google.adk.apps.app import App
from google.adk.plugins import ReflectAndRetryToolPlugin

app = App(
    name="my_app",
    root_agent=root_agent,
    plugins=[
        ReflectAndRetryToolPlugin(
            max_retries=6, throw_exception_if_retry_exceeded=False
        ),
    ],
)
```
For a complete example, see the [plugin_reflect_tool_retry sample](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_reflect_tool_retry).
