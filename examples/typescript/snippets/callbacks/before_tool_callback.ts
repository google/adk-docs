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
  ToolContext,
  isFinalResponse,
  BaseTool,
} from '@google/adk';
import { createUserContent } from "@google/genai";
import { z } from 'zod';

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "before_tool_callback_app";
const USER_ID = "test_user_before_tool";

// --- Define a Simple Tool Function ---
const CountryInput = z.object({
  country: z.string().describe('The country to get the capital for.'),
});

async function getCapitalCity(params: z.infer<typeof CountryInput>): Promise<{ result: string }> {
    console.log(`\n-- Tool Call: getCapitalCity(country='${params.country}') --`);
    const capitals: Record<string, string> = {
        'united states': 'Washington, D.C.',
        'canada': 'Ottawa',
        'france': 'Paris',
        'japan': 'Tokyo',
    };
    const result = capitals[params.country.toLowerCase()] ??
        `Sorry, I couldn't find the capital for ${params.country}.`;
    console.log(`-- Tool Result: '${result}' --`);
    return { result };
}

const getCapitalCityTool = new FunctionTool({
    name: 'get_capital_city',
    description: 'Retrieves the capital city for a given country',
    parameters: CountryInput,
    execute: getCapitalCity,
});

// --- Define the Callback Function ---
function simpleBeforeToolModifier({
  tool,
  args,
  context,
}: {
  tool: BaseTool;
  args: Record<string, any>;
  context: ToolContext;
}) {
  const agentName = context.agentName;
  const toolName = tool.name;
  console.log(`[Callback] Before tool call for tool '${toolName}' in agent '${agentName}'`);
  console.log(`[Callback] Original args: ${JSON.stringify(args)}`);

  if (
    toolName === "get_capital_city" &&
    args["country"]?.toLowerCase() === "canada"
  ) {
    console.log("[Callback] Detected 'Canada'. Modifying args to 'France'.");
    args["country"] = "France";
    console.log(`[Callback] Modified args: ${JSON.stringify(args)}`);
    return undefined;
  }

  if (
    toolName === "get_capital_city" &&
    args["country"]?.toUpperCase() === "BLOCK"
  ) {
    console.log("[Callback] Detected 'BLOCK'. Skipping tool execution.");
    return { result: "Tool execution was blocked by before_tool_callback." };
  }

  console.log("[Callback] Proceeding with original or previously modified args.");
  return;
}

// Create LlmAgent and Assign Callback
const myLlmAgent = new LlmAgent({
  name: 'ToolCallbackAgent',
  model: MODEL_NAME,
  instruction: 'You are an agent that can find capital cities. Use the get_capital_city tool.',
  description: 'An LLM agent demonstrating before_tool_callback',
  tools: [getCapitalCityTool],
  beforeToolCallback: simpleBeforeToolModifier,
});

// Agent Interaction Logic
async function callAgentAndPrint(runner: InMemoryRunner, query: string, sessionId: string) {
  console.log(`\n>>> Calling Agent for session '${sessionId}' | Query: "${query}"`);

  for await (const event of runner.runAsync({ userId: USER_ID, sessionId, newMessage: createUserContent(query) })) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const finalResponseContent = event.content.parts.map(part => part.text ?? '').join('');
      console.log(`<<< Final Output: ${finalResponseContent}`);
    }
  }
}

// Run Interactions
async function main() {
  const runner = new InMemoryRunner({ agent: myLlmAgent, appName: APP_NAME });

  // Scenario 1: Callback modifies the arguments from "Canada" to "France"
  const canadaSessionId = 'session_canada_test';
  await runner.sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: canadaSessionId });
  await callAgentAndPrint(runner, 'What is the capital of Canada?', canadaSessionId);

  // Scenario 2: Callback skips the tool call
  const blockSessionId = 'session_block_test';
  await runner.sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: blockSessionId });
  await callAgentAndPrint(runner, 'What is the capital of BLOCK?', blockSessionId);
}

main();
