from google.adk.tools import ToolContext

def my_tool(arg1: str, tool_context: ToolContext):
    # Example: Accessing session state
    user_id = tool_context.state.get("user_id")
    # Example: Triggering an action
    # tool_context.actions.transfer_to_agent = "secondary_agent"