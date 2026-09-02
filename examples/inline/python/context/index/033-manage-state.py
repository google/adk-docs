# Example: Tool 1 - Fetches user ID
from google.adk.tools import ToolContext
import uuid

def get_user_profile(tool_context: ToolContext) -> dict:
    user_id = str(uuid.uuid4()) # Simulate fetching ID
    # Save the ID to state for the next tool
    tool_context.state["temp:current_user_id"] = user_id
    return {"profile_status": "ID generated"}

# Example: Tool 2 - Uses user ID from state
def get_user_orders(tool_context: ToolContext) -> dict:
    user_id = tool_context.state.get("temp:current_user_id")
    if not user_id:
        return {"error": "User ID not found in state"}

    print(f"Fetching orders for user ID: {user_id}")
    # ... logic to fetch orders using user_id ...
    return {"orders": ["order123", "order456"]}