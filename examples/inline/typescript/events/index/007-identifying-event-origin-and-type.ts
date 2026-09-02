// Pseudocode: Basic event identification (TypeScript)
import {
  Event,
  getFunctionCalls,
  getFunctionResponses
} from '@google/adk';

export async function processEvents(runnerEvents: AsyncIterable<Event>) {
  for await (const event of runnerEvents) {
    console.log(`Event from: ${event.author}`);

    if (event.content && event.content.parts && event.content.parts.length > 0) {
      if (getFunctionCalls(event).length > 0) {
        console.log('  Type: Tool Call Request');
      } else if (getFunctionResponses(event).length > 0) {
        console.log('  Type: Tool Result');
      } else if (event.content.parts[0].text) {
        if (event.partial) {
          console.log('  Type: Streaming Text Chunk');
        } else {
          console.log('  Type: Complete Text Message');
        }
      } else {
        console.log('  Type: Other Content (e.g., code result)');
      }
    } else if (
      event.actions &&
      (Object.keys(event.actions.stateDelta).length > 0 ||
        Object.keys(event.actions.artifactDelta).length > 0)
    ) {
      console.log('  Type: State/Artifact Update');
    } else {
      console.log('  Type: Control Signal or Other');
    }
  }
}