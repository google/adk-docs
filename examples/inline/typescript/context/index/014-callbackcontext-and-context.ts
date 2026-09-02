// Pseudocode: Callback receiving Context
import { Context, LlmRequest } from '@google/adk';
import { Content } from '@google/genai';

function myBeforeModelCb(context: Context, request: LlmRequest): Content | undefined {
  // Read/Write state example
  const callCount = (context.state.get('model_calls') as number) || 0;
  context.state.set('model_calls', callCount + 1); // Modify state

  // Optionally load an artifact
  // const configPart = await context.loadArtifact('model_config.json');
  console.log(`Preparing model call #${callCount + 1} for invocation ${context.invocationId}`);
  return undefined; // Allow model call to proceed
}