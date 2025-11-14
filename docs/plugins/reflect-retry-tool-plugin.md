# Reflect and Retry Tool Plugin

The `ReflectAndRetryToolPlugin` provides self-healing, concurrent-safe error recovery for tool failures. This plugin intercepts tool failures, provides structured guidance to the LLM for reflection and correction, and retries the operation up to a configurable limit.

## Key Features

- **Concurrency Safe:** Uses locking to safely handle parallel tool executions.
- **Configurable Scope:** Tracks failures per-invocation (default) or globally using the `TrackingScope` enum.
- **Extensible Scoping:** The `_get_scope_key` method can be overridden to implement custom tracking logic (e.g., per-user or per-session).
- **Granular Tracking:** Failure counts are tracked per-tool within the defined scope. A success with one tool resets its counter without affecting others.
- **Custom Error Extraction:** Supports detecting errors in normal tool responses that don't throw exceptions, by overriding the `extract_error_from_result` method.

## How to Use

To use the `ReflectAndRetryToolPlugin`, add it to the `plugins` list in your `App` configuration.

### Basic Usage

The most common usage is to track failures only within the current agent invocation.

```python
from google.adk.plugins import ReflectAndRetryToolPlugin

# Track failures only within the current agent invocation (default).
error_handling_plugin = ReflectAndRetryToolPlugin(max_retries=3)

app = App(
    # ...
    plugins=[error_handling_plugin],
)
```

### Global Scope

You can track failures globally across all turns and users.

```python
from google.adk.plugins import ReflectAndRetryToolPlugin, TrackingScope

# Track failures globally across all turns and users.
global_error_handling_plugin = ReflectAndRetryToolPlugin(
    max_retries=5,
    scope=TrackingScope.GLOBAL
)

app = App(
    # ...
    plugins=[global_error_handling_plugin],
)
```

### Disabling Exceptions

You can configure the plugin to not throw an exception when the retry limit is exceeded and instead return guidance to the LLM.

```python
from google.adk.plugins import ReflectAndRetryToolPlugin

# Retry on failures but do not throw exceptions.
error_handling_plugin = ReflectAndRetryToolPlugin(
    max_retries=3,
    throw_exception_if_retry_exceeded=False
)

app = App(
    # ...
    plugins=[error_handling_plugin],
)
```

### Custom Error Extraction

You can create a custom plugin that inherits from `ReflectAndRetryToolPlugin` to detect errors in successful tool responses that contain error messages.

```python
from google.adk.plugins import ReflectAndRetryToolPlugin

class CustomRetryPlugin(ReflectAndRetryToolPlugin):
  async def extract_error_from_result(self, *, tool, tool_args, tool_context, result):
    # Detect error based on response content
    if result.get('status') == 'error':
        return result
    return None  # No error detected

error_handling_plugin = CustomRetryPlugin(max_retries=5)

app = App(
    # ...
    plugins=[error_handling_plugin],
)
```
