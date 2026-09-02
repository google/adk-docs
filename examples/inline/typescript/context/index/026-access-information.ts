// Pseudocode: In any context
import { Context } from '@google/adk';

function logToolUsage(context: Context) {
  const agentName = context.agentName;
  const invId = context.invocationId;
  const functionCallId = context.functionCallId ?? 'N/A'; // Available when executing a tool

  console.log(`Log: Invocation=${invId}, Agent=${agentName}, FunctionCallID=${functionCallId} - Tool Executed.`);
}