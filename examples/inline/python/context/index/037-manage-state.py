# Example: Tool or Callback identifies a preference
from google.adk.tools import ToolContext # Or Context

def set_user_preference(tool_context: ToolContext, preference: str, value: str) -> dict:
    # Use 'user:' prefix for user-level state (if using a persistent SessionService)
    state_key = f"user:{preference}"
    tool_context.state[state_key] = value
    print(f"Set user preference '{preference}' to '{value}'")
    return {"status": "Preference updated"}