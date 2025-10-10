# Plugins

Plugins provide a structured way to intercept and modify agent, tool, and model behavior across your entire application. While callbacks apply to a particular agent, plugins apply globally to all agents in the runner.

Plugins are best used for adding custom behaviors such as:

*   **Logging:** Track important information at each callback point.
*   **Context Management:** Filter the LLM context to reduce its size.
*   **Error Handling:** Implement custom logic to handle tool failures.

## How to Use

To use a plugin, you add it to the `plugins` list of your `App`.

```python
from google.adk.apps import App
from my_plugins import MyCustomPlugin

my_app = App(
    agent=my_agent,
    plugins=[MyCustomPlugin()]
)
```

## Available Plugins

*   [Logging Plugin](logging_plugin.md)
*   [Context Filter Plugin](context_filter_plugin.md)
*   [Save Files As Artifacts Plugin](save_files_as_artifacts_plugin.md)
*   [Reflect and Retry Tool Plugin](reflect_and_retry_tool_plugin.md)
