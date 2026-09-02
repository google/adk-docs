// Pseudocode: Tool 1 - Fetches user ID
import { Context } from '@google/adk';
import { v4 as uuidv4 } from 'uuid';

function getUserProfile(context: Context): Record<string, string> {
  const userId = uuidv4(); // Simulate fetching ID
  // Save the ID to state for the next tool
  context.state.set('temp:current_user_id', userId);
  return { profile_status: 'ID generated' };
}

// Pseudocode: Tool 2 - Uses user ID from state
function getUserOrders(context: Context): Record<string, string | string[]> {
  const userId = context.state.get('temp:current_user_id');
  if (!userId) {
    return { error: 'User ID not found in state' };
  }

  console.log(`Fetching orders for user ID: ${userId}`);
  // ... logic to fetch orders using user_id ...
  return { orders: ['order123', 'order456'] };
}