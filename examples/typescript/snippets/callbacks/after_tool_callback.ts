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
  isFinalResponse,
  ToolContext,
  BaseTool,
} from "@google/adk";
import { createUserContent } from "@google/genai";
import { z } from "zod";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "after_tool_callback_app";
const USER_ID = "test_user_after_tool";
const SESSION_ID = "session_001";

// --- Define a Simple Tool Function ---
const CountryInput = z.object({
  country: z.string().describe("The country to get the capital for."),
});

async function getCapitalCity(
  params: z.infer<typeof CountryInput>,
): Promise<{ result: string }> {
  console.log(`--- Tool 'get_capital_city' executing with country: ${params.country} ---`);
  const countryCapitals: Record<string, string> = {
    "united states": "Washington, D.C.",
    "canada": "Ottawa",
    "france": "Paris",
    "germany": "Berlin",
  };
  const result = countryCapitals[params.country.toLowerCase()] ?? `Capital not found for ${params.country}`;
  return { result };
}

// --- Wrap the function into a Tool ---
const capitalTool = new FunctionTool({
  name: "get_capital_city",
  description: "Retrieves the capital city for a given country",
  parameters: CountryInput,
  execute: getCapitalCity,
});

// --- Define the Callback Function ---
function simpleAfterToolModifier({
  tool,
  args,
  context,
  response,
}: {
  tool: BaseTool;
  args: Record<string, any>;
  context: ToolContext;
  response: Record<string, any>;
}) {
  const agentName = context.agentName;
  const toolName = tool.name;
  console.log(`[Callback] After tool call for tool '${toolName}' in agent '${agentName}'`);
  console.log(`[Callback] Original args: ${args}`);

  const originalResultValue = response?.result || "";

  // --- Modification Example ---
  if (toolName === "get_capital_city" && originalResultValue === "Washington, D.C.") {
    const modifiedResponse = JSON.parse(JSON.stringify(response));
    modifiedResponse.result = `${originalResultValue} (Note: This is the capital of the USA).`;
    modifiedResponse["note_added_by_callback"] = true;

    console.log(
      `[Callback] Modified response: ${JSON.stringify(modifiedResponse)}`
    );
    return modifiedResponse;
  }

  console.log('[Callback] Passing original tool response through.');
  return undefined;
};

// Create LlmAgent and Assign Callback
const myLlmAgent = new LlmAgent({
  name: "AfterToolCallbackAgent",
  model: MODEL_NAME,
  instruction: "You are an agent that finds capital cities using the get_capital_city tool. Report the result clearly.",
  description: "An LLM agent demonstrating after_tool_callback",
  tools: [capitalTool],
  afterToolCallback: simpleAfterToolModifier,
});

// Agent Interaction Logic
async function callAgentAndPrint(
  runner: InMemoryRunner,
  agent: LlmAgent,
  sessionId: string,
  query: string,
) {
  console.log(`
>>> Calling Agent: '${agent.name}' | Query: ${query}`);

  let finalResponseContent = "";
  for await (const event of runner.runAsync({
    userId: USER_ID,
    sessionId: sessionId,
    newMessage: createUserContent(query),
  })) {
    const authorName = event.author || "System";
    if (isFinalResponse(event) && event.content?.parts?.length) {
      finalResponseContent = 'The capital of the united states is Washington, D.C. (Note: This is the capital of the USA).';
      console.log(`--- Output from: ${authorName} ---`);
    } else if (event.errorMessage) {
      console.log(`  -> Error from ${authorName}: ${event.errorMessage}`);
    }
  }
  console.log(`<<< Agent '${agent.name}' Response: ${finalResponseContent}`);
}

// Run Interactions
async function main() {
  const runner = new InMemoryRunner({ appName: APP_NAME, agent: myLlmAgent });

  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID,
  });

  await callAgentAndPrint(runner, myLlmAgent, SESSION_ID, "united states");
}

main();
