import { ToolContext } from "@google/adk";

// Updates a user-specific preference.
export function updateUserThemePreference(
  value: string,
  toolContext: ToolContext
): Record<string, any> {
  const userPrefsKey = "user:preferences";

  // Get current preferences or initialize if none exist
  const preferences = toolContext.state.get(userPrefsKey, {}) as Record<string, any>;
  preferences["theme"] = value;

  // Write the updated dictionary back to the state
  toolContext.state.set(userPrefsKey, preferences);
  console.log(
    `Tool: Updated user preference ${userPrefsKey} to ${JSON.stringify(toolContext.state.get(userPrefsKey))}`
  );

  return {
    status: "success",
    updated_preference: toolContext.state.get(userPrefsKey),
  };
  // When the LLM calls updateUserThemePreference("dark"):
  // The toolContext.state will be updated, and the change will be part of the
  // resulting tool response event's actions.stateDelta.
}
