// Pseudocode: Tool or Callback identifies a preference
import { Context } from '@google/adk';

function setUserPreference(context: Context, preference: string, value: string): Record<string, string> {
  // Use 'user:' prefix for user-level state (if using a persistent SessionService)
  const stateKey = `user:${preference}`;
  context.state.set(stateKey, value);
  console.log(`Set user preference '${preference}' to '${value}'`);
  return { status: 'Preference updated' };
}