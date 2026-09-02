// Pseudocode: Instruction provider receiving ReadonlyContext
import { ReadonlyContext } from '@google/adk';

function myInstructionProvider(context: ReadonlyContext): string {
  // Read-only access example
  // The state object is read-only
  const userTier = context.state.get('user_tier') ?? 'standard';
  // context.state.set('new_key', 'value'); // This would fail or throw an error
  return `Process the request for a ${userTier} user.`;
}