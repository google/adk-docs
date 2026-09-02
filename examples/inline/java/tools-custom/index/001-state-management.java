import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;

// Updates a user-specific preference.
public Map<String, String> updateUserThemePreference(String value, ToolContext toolContext) {
  String userPrefsKey = "user:preferences:theme";

  // Get current preferences or initialize if none exist
  String preference = toolContext.state().getOrDefault(userPrefsKey, "").toString();
  if (preference.isEmpty()) {
    preference = value;
  }

  // Write the updated dictionary back to the state
  toolContext.state().put("user:preferences", preference);
  System.out.printf("Tool: Updated user preference %s to %s", userPrefsKey, preference);

  return Map.of("status", "success", "updated_preference", toolContext.state().get(userPrefsKey).toString());
  // When the LLM calls updateUserThemePreference("dark"):
  // The toolContext.state will be updated, and the change will be part of the
  // resulting tool response event's actions.stateDelta.
}