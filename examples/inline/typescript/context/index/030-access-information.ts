// Pseudocode: In a Callback
import { Context } from '@google/adk';

function checkInitialIntent(context: Context) {
  let initialText = 'N/A';
  const userContent = context.userContent;
  if (userContent?.parts?.length) {
    initialText = userContent.parts[0].text ?? 'Non-text input';
  }

  console.log(`This invocation started with user input: '${initialText}'`);
}