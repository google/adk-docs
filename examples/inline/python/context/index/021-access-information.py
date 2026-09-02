# Example: In a Tool function
from google.adk.tools import ToolContext

def my_tool(tool_context: ToolContext, **kwargs):
    user_pref = tool_context.state.get("user_display_preference", "default_mode")
    api_endpoint = tool_context.state.get("app:api_endpoint") # Read app-level state

    if user_pref == "dark_mode":
        # ... apply dark mode logic ...
        pass
    print(f"Using API endpoint: {api_endpoint}")
    # ... rest of tool logic ...

# Example: In a Callback function
from google.adk.agents.context import Context

def my_callback(context: Context, **kwargs):
    last_tool_result = context.state.get("temp:last_api_result") # Read temporary state
    if last_tool_result:
        print(f"Found temporary result from last tool: {last_tool_result}")
    # ... callback logic ...