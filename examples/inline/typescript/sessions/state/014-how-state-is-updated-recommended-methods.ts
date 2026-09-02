// In an agent callback or tool function
import { Context } from "@google/adk";

function myCallbackOrToolFunction(
    context: Context,
    // ... other parameters ...
) {
    // Update existing state
    const count = context.state.get("user_action_count", 0);
    context.state.set("user_action_count", count + 1);

    // Add new state
    context.state.set("temp:last_operation_status", "success");

    // State changes are automatically part of the event's stateDelta
    // ... rest of callback/tool logic ...
}