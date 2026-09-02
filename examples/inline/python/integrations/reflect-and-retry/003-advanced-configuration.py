class CustomRetryPlugin(ReflectAndRetryToolPlugin):
  async def extract_error_from_result(self, *, tool, tool_args,tool_context,
  result):
    # Detect error based on response content
    if result.get('status') == 'error':
        return result
    return None  # No error detected

# add this modified plugin to your App object:
error_handling_plugin = CustomRetryPlugin(max_retries=5)