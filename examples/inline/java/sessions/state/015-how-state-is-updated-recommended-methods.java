// In an agent callback or tool method
import com.google.adk.agents.CallbackContext; // or ToolContext
// ... other imports ...

public class MyAgentCallbacks {
    public void onAfterAgent(CallbackContext callbackContext) {
        // Update existing state
        Integer count = (Integer) callbackContext.state().getOrDefault("user_action_count", 0);
        callbackContext.state().put("user_action_count", count + 1);

        // Add new state
        callbackContext.state().put("temp:last_operation_status", "success");

        // State changes are automatically part of the event's state_delta
        // ... rest of callback logic ...
    }
}