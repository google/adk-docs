// Example: Tool 1 - Fetches user ID
import com.google.adk.tools.ToolContext;
import java.util.Map;
import java.util.UUID;

public Map<String, String> getUserProfile(ToolContext toolContext) {
    String userId = UUID.randomUUID().toString();
    // Save the ID to state for the next tool
    toolContext.state().put("temp:current_user_id", userId);
    return Map.of("profile_status", "ID generated");
}

// Example: Tool 2 - Uses user ID from state
public Map<String, String> getUserOrders(ToolContext toolContext) {
    String userId = (String) toolContext.state().get("temp:current_user_id");
    if (userId == null || userId.isEmpty()) {
        return Map.of("error", "User ID not found in state");
    }
    System.out.println("Fetching orders for user id: " + userId);
    // ... logic to fetch orders using userId ...
    return Map.of("orders", "order123");
}