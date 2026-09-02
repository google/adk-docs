// Example: In a Tool function
import com.google.adk.tools.ToolContext;

public void myTool(ToolContext toolContext) {
    String userPref = (String) toolContext.state().getOrDefault("user_display_preference", "default_mode");
    String apiEndpoint = (String) toolContext.state().get("app:api_endpoint"); // Read app-level state

    if ("dark_mode".equals(userPref)) {
        // ... apply dark mode logic ...
    }
    System.out.println("Using API endpoint: " + apiEndpoint);
    // ... rest of tool logic ...
}

// Example: In a Callback function
import com.google.adk.agents.CallbackContext;

public void myCallback(CallbackContext callbackContext) {
    String lastToolResult = (String) callbackContext.state().get("temp:last_api_result"); // Read temporary state

    if (lastToolResult != null && !lastToolResult.isEmpty()) {
        System.out.println("Found temporary result from last tool: " + lastToolResult);
    }
    // ... callback logic ...
}