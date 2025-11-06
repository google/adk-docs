# Reflect and Retry Tool Plugin

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.16.0</span>
</div>

The Reflect and Retry Tool plugin can help your agent recover from error
responses from ADK [Tools](/adk-docs/tools-custom/) and automatically retry the
tool request. This plugin intercepts tool failures, provides structured guidance
to the AI model for reflection and correction, and retries the operation up to a
configurable limit. This plugin can help you build more resilience into your
agent workflows, including the following capabilities:

*   **Concurrency safe**: Uses locking to safely handle parallel tool executions.
*   **Configurable scope**: Tracks failures per-invocation (default) or globally.
*   **Granular tracking**: Failure counts are tracked per-tool.
*   **Custom error extraction**: Supports detecting errors in normal tool responses.

## Add Reflect and Retry Plugin

Add this plugin to your ADK workflow by adding it to the plugins setting of your
ADK project's App object, as shown below:

```python
from google.adk.apps.app import App
from google.adk.plugins import ReflectAndRetryToolPlugin

app = App(
    name="my_app",
    root_agent=root_agent,
    plugins=[
        ReflectAndRetryToolPlugin(max_retries=3),
    ],
)
```

With this configuration, if any tool called by an agent returns an error, the
request is updated and tried again, up to a maximum of 3 attempts, per tool.

## Configuration settings

The Reflect and Retry Plugin has the following configuration options:

*   **`max_retries`**: (optional) Total number of additional attempts the system
    makes to receive a non-error response. Default value is 3.
*   **`throw_exception_if_retry_exceeded`**: (optional) If set to `False`, the
    system does not raise an error if the final retry attempt fails. Default
    value is `True`.
*   **`tracking_scope`**: (optional)
    *   **`TrackingScope.INVOCATION`**: Track tool failures across a single
        invocation and user. This value is the default.
    *   **`TrackingScope.GLOBAL`**: Track tool failures across all invocations
        and all users.

### Advanced configuration

You can further modify the behavior of this plugin by extending the
`ReflectAndRetryToolPlugin` class. The following code sample
demonstrates a simple extension of the behavior by selecting
responses with an error status:

```python
class CustomRetryPlugin(ReflectAndRetryToolPlugin):
  async def extract_error_from_result(self, *, tool, tool_args,tool_context,
  result):
    # Detect error based on response content
    if result.get('status') == 'error':
        return result
    return None  # No error detected

# add this modified plugin to your App object:
error_handling_plugin = CustomRetryPlugin(max_retries=5)
```

## Next steps

For complete code samples using the Reflect and Retry plugin, see the following: 

*   [Basic](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_reflect_tool_retry/basic)
    code sample
*   [Hallucinating function name](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_reflect_tool_retry/hallucinating_func_name)
    code sample
