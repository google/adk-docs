/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import {
  LlmAgent,
  InMemoryRunner,
  FunctionTool,
  Tool,
  ToolContext,
  BeforeToolCallbackResponse,
} from '../../../../../../repos/adk-js/core/src/index';
import { Content, createUserContent } from '@google/genai';
import { z } from 'zod';

const MODEL_NAME = 'gemini-1.5-flash-latest';

// --- Define a Simple Tool Function ---
const CountryInput = z.object({
  country: z.string().describe('The country to get the capital for.'),
});

async function getCapitalCity(
  params: z.infer<typeof CountryInput>,
): Promise<{ result: string }> {
  console.log(`--- Tool 'get_capital_city' executing with country: ${params.country} ---`);
  const countryCapitals: Record<string, string> = {
    'united states': 'Washington, D.C.',
    canada: 'Ottawa',
    france: 'Paris',
    germany: 'Berlin',
  };
  const result = countryCapitals[params.country.toLowerCase()] ?? `Capital not found for ${params.country}`;
  return { result };
}

const capitalTool = new FunctionTool({
  name: 'get_capital_city',
  description: 'Retrieves the capital city for a given country',
  parameters: CountryInput,
  execute: getCapitalCity,
});

// --- Define the Callback Function ---
function simpleBeforeToolModifier(
  tool: Tool,
  args: Record<string, any>,
  toolContext: ToolContext,
): BeforeToolCallbackResponse | undefined {
  'use strict';
  const agentName = toolContext.agentName;
  const toolName = tool.name;
  console.log(`[Callback] Before tool call for tool '${toolName}' in agent '${agentName}'`);
  console.log(`[Callback] Original args: ${JSON.stringify(args)}`);

  if (toolName === 'get_capital_city' && args['country']?.toLowerCase() === 'canada') {
    console.log("[Callback] Detected 'Canada'. Modifying args to 'France'.");
    const modifiedArgs = { ...args, country: 'France' };
    console.log(`[Callback] Modified args: ${JSON.stringify(modifiedArgs)}`);
    return { args: modifiedArgs }; // Return modified args
  }

  if (toolName === 'get_capital_city' && args['country']?.toUpperCase() === 'BLOCK') {
    console.log("[Callback] Detected 'BLOCK'. Skipping tool execution.");
    return {
      toolResponse: { result: 'Tool execution was blocked by before_tool_callback.' },
    }; // Return a direct response to skip the tool
  }

  console.log('[Callback] Proceeding with original args.');
  return undefined; // Proceed with original args
}

// Create LlmAgent and Assign Callback
const myLlmAgent = new LlmAgent({
  name: 'ToolCallbackAgent',
  model: MODEL_NAME,
  instruction: 'You are an agent that can find capital cities. Use the get_capital_city tool.',
  description: 'An LLM agent demonstrating before_tool_callback',
  tools: [capitalTool],
  beforeToolCallback: simpleBeforeToolModifier,
});

// Agent Interaction Logic
async function callAgentAndPrint(runner: InMemoryRunner, query: string) {
  const appName = 'before_tool_demo';
  const userId = 'test_user';
  const sessionId = `session_${Math.random().toString(36).substring(7)}`;

  await runner.sessionService.createSession({ appName, userId, sessionId });

  console.log(`
>>> Calling Agent: '${myLlmAgent.name}' | Query: ${query}`);
  const message = createUserContent(query);

  for await (const event of runner.run({ userId, sessionId, newMessage: message })) {
    if (event.isFinalResponse() && event.content) {
      console.log(`Final Output: [${event.author}] ${event.content.parts[0].text?.trim()}`);
    } else if (event.isError()) {
      console.log(`Error Event: ${event.errorDetails}`);
    }
  }
}

// Run Interactions
async function main() {
  const runner = new InMemoryRunner({ agent: myLlmAgent, appName: 'before_tool_demo' });

  // Scenario 1: Callback modifies the arguments from "Canada" to "France"
  await callAgentAndPrint(runner, 'What is the capital of Canada?');

  // Scenario 2: Callback skips the tool call
  await callAgentAndPrint(runner, 'What is the capital of BLOCK?');
}

main();
