// Pseudocode: In a Tool function
import { Context } from '@google/adk';

async function myTool(context: Context) {
  const userPref = context.state.get('user_display_preference', 'default_mode');
  const apiEndpoint = context.state.get('app:api_endpoint'); // Read app-level state

  if (userPref === 'dark_mode') {
    // ... apply dark mode logic ...
  }
  console.log(`Using API endpoint: ${apiEndpoint}`);
  // ... rest of tool logic ...
}

// Pseudocode: In a Callback function
import { Context } from '@google/adk';

function myCallback(context: Context) {
  const lastToolResult = context.state.get('temp:last_api_result'); // Read temporary state
  if (lastToolResult) {
    console.log(`Found temporary result from last tool: ${lastToolResult}`);
  }
  // ... callback logic ...
}