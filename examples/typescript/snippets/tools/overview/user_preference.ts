import { Context } from '@google/adk';

// Updates a user-specific preference.
export function updateUserThemePreference(
  value: string,
  context: Context
): Record<string, any> {
  const userPrefsKey = "user:preferences";

  // Get current preferences or initialize if none exist
  const preferences = context.state.get(userPrefsKey, {}) as Record<string, any>;
  preferences["theme"] = value;

  // Write the updated dictionary back to the state
  context.state.set(userPrefsKey, preferences);
  console.log(
    `Tool: Updated user preference ${userPrefsKey} to ${JSON.stringify(context.state.get(userPrefsKey))}`
  );

  return {
    status: "success",
    updated_preference: context.state.get(userPrefsKey),
  };
  // When the LLM calls updateUserThemePreference("dark"):
  // The context.state will be updated, and the change will be part of the
  // resulting tool response event's actions.stateDelta.
}
