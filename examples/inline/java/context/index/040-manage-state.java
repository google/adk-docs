// Example: Tool or Callback identifies a preference
import com.google.adk.tools.ToolContext; // Or CallbackContext

public Map<String, String> setUserPreference(ToolContext toolContext, String preference, String value) {
    // Use 'user:' prefix for user-level state (if using a persistent SessionService)
    String stateKey = "user:" + preference;
    toolContext.state().put(stateKey, value);
    System.out.println("Set user preference '" + preference + "' to '" + value + "'");
    return Map.of("status", "Preference updated");
}