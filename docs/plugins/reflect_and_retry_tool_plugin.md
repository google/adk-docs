# Reflect and Retry Tool Plugin

The `ReflectAndRetryToolPlugin` is a powerful plugin that enhances the resilience of your agents by providing a mechanism to handle tool failures gracefully. When a tool fails, this plugin intercepts the error, provides structured guidance to the LLM for reflection and correction, and retries the operation up to a configurable number of times.

## How it Works

The `ReflectAndRetryToolPlugin` works by implementing the `on_tool_error_callback` method. When a tool execution results in an error, this callback is triggered. The plugin then constructs a detailed reflection message for the LLM, which includes:

*   The name of the tool that failed.
*   The arguments that were passed to the tool.
*   The error message that was returned.
*   The number of retry attempts remaining.

This reflection message guides the LLM to understand the cause of the failure and to adjust its subsequent actions to correct the error.

## Features

*   **Automatic Retry**: Automatically retries a failed tool execution up to a specified number of times.
*   **LLM Reflection**: Provides detailed error information to the LLM to help it correct its mistakes.
*   **Configurable**: You can configure the maximum number of retries and whether to throw an exception when the retry limit is exceeded.
*   **Customizable**: You can extend the plugin to implement custom error handling logic.

## How to Use

To use the `ReflectAndRetryToolPlugin`, you need to add it to the `plugins` list of your `App`.

```python
from google.adk.apps import App
from google.adk.agents import LlmAgent
from google.adk.plugins import ReflectAndRetryToolPlugin

# Define your agent
my_agent = LlmAgent(
    # ... your agent configuration
)

# Initialize the plugin
error_handling_plugin = ReflectAndRetryToolPlugin(max_retries=3)

# Create an App with the agent and plugin
my_app = App(
    agent=my_agent,
    plugins=[error_handling_plugin]
)
```

### Configuration

The `ReflectAndRetryToolPlugin` can be configured with the following parameters:

*   **`max_retries`** (int, optional): The maximum number of times to retry a failed tool execution. Defaults to `3`.
*   **`throw_exception_if_retry_exceeded`** (bool, optional): If `True`, the plugin will raise the final exception when the retry limit is reached. If `False`, it will return guidance to the LLM instead. Defaults to `True`.

### Customizing the Plugin

You can also customize the behavior of the plugin by subclassing it and overriding its methods. For example, you can override the `extract_error_from_result` method to implement custom logic for detecting errors in tool responses.

```python
from google.adk.plugins import ReflectAndRetryToolPlugin

class CustomRetryPlugin(ReflectAndRetryToolPlugin):
    def extract_error_from_result(self, result: dict) -> str | None:
        # Implement custom error detection logic here
        if "custom_error_key" in result:
            return result["custom_error_key"]
        return super().extract_error_from_result(result)

# Use the custom plugin
custom_error_handling_plugin = CustomRetryPlugin(max_retries=5)

my_app = App(
    agent=my_agent,
    plugins=[custom_error_handling_plugin]
)
```
