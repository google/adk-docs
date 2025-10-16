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
  CallbackContext,
  isFinalResponse,
} from "@google/adk";
import { createUserContent } from "@google/genai";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "before_model_callback_app";
const USER_ID = "test_user_before_model";
const SESSION_ID_BLOCK = "session_block_model_call";
const SESSION_ID_NORMAL = "session_normal_model_call";

// --- Define the Callback Function ---
function simpleBeforeModelModifier({
  context,
  request,
}: {
  context: CallbackContext;
  request: any;
}): any | undefined {
  console.log(`[Callback] Before model call for agent: ${context.agentName}`);

  // Inspect the last user message in the request contents
  const lastUserMessage = request.contents?.at(-1)?.parts?.[0]?.text ?? "";
  console.log(`[Callback] Inspecting last user message: '${lastUserMessage}'`);

  // --- Modification Example ---
  // Add a prefix to the system instruction.
  // We create a deep copy to avoid modifying the original agent's config object.
  const modifiedConfig = JSON.parse(JSON.stringify(request.config));
  const originalInstructionText =
    modifiedConfig.systemInstruction?.parts?.[0]?.text ?? "";
  const prefix = "[Modified by Callback] ";
  modifiedConfig.systemInstruction = {
    role: "system",
    parts: [{ text: prefix + originalInstructionText }],
  };
  request.config = modifiedConfig; // Assign the modified config back to the request
  console.log(
    `[Callback] Modified system instruction to: '${modifiedConfig.systemInstruction.parts[0].text}'`
  );

  // --- Skip Example ---
  // Check if the last user message contains "BLOCK"
  if (lastUserMessage.toUpperCase().includes("BLOCK")) {
    console.log("[Callback] 'BLOCK' keyword found. Skipping LLM call.");
    // Return an LlmResponse to skip the actual LLM call
    return {
      content: {
        role: "model",
        parts: [
          { text: "LLM call was blocked by the before_model_callback." },
        ],
      },
    };
  }

  console.log("[Callback] Proceeding with LLM call.");
  // Return undefined to allow the (modified) request to go to the LLM
  return undefined;
}

// --- Create LlmAgent and Assign Callback ---
const myLlmAgent = new LlmAgent({
  name: "ModelCallbackAgent",
  model: MODEL_NAME,
  instruction: "You are a helpful assistant.", // Base instruction
  description: "An LLM agent demonstrating before_model_callback",
  beforeModelCallback: simpleBeforeModelModifier, // Assign the function here
});

// --- Agent Interaction Logic ---
async function callAgentAndPrint(
  runner: InMemoryRunner,
  query: string,
  sessionId: string
) {
  console.log(`\n>>> Calling Agent with query: "${query}"`);

  let finalResponseContent = "No final response received.";
  const events = runner.runAsync({ userId: USER_ID, sessionId, newMessage: createUserContent(query) });

  for await (const event of events) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      finalResponseContent = event.content.parts
        .map((part: { text?: string }) => part.text ?? "")
        .join("");
    }
  }
  console.log("<<< Agent Response: ", finalResponseContent);
}

// --- Run Interactions ---
async function main() {
  const runner = new InMemoryRunner({ agent: myLlmAgent, appName: APP_NAME });

  // Scenario 1: The callback will find "BLOCK" and skip the model call
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID_BLOCK,
  });
  await callAgentAndPrint(
    runner,
    "write a joke about BLOCK",
    SESSION_ID_BLOCK
  );

  // Scenario 2: The callback will modify the instruction and proceed
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID_NORMAL,
  });
  await callAgentAndPrint(runner, "write a short poem", SESSION_ID_NORMAL);
}

main();
