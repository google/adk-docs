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
const APP_NAME = "after_model_callback_app";
const USER_ID = "test_user_after_model";
const SESSION_ID_JOKE = "session_modify_model_call";
const SESSION_ID_POEM = "session_normal_model_call";

// --- Define the Callback Function ---
function simpleAfterModelModifier({
  context,
  response,
}: {
  context: CallbackContext;
  response: any;
}): any | undefined {
  console.log(
    `[Callback] After model call for agent: ${context.agentName}`
  );

  const modelResponseText = response.content?.parts?.[0]?.text ?? "";
  console.log(`[Callback] Inspecting model response: "${modelResponseText.substring(0, 50)}..."`);

  // --- Modification Example ---
  // Replace "joke" with "funny story" (case-insensitive)
  const searchTerm = "joke";
  const replaceTerm = "funny story";
  if (modelResponseText.toLowerCase().includes(searchTerm)) {
    console.log(`[Callback] Found '${searchTerm}'. Modifying response.`);

    // Create a deep copy to avoid mutating the original response object
    const modifiedResponse = JSON.parse(JSON.stringify(response));

    // Safely modify the text of the first part
    if (modifiedResponse.content?.parts?.[0]) {
      // Use a regular expression for case-insensitive replacement
      const regex = new RegExp(searchTerm, "gi");
      modifiedResponse.content.parts[0].text = modelResponseText.replace(regex, replaceTerm);
    }

    console.log(`[Callback] Returning modified response.`);
    return modifiedResponse;
  }

  console.log("[Callback] Proceeding with original LLM response.");
  // Return undefined to proceed without any modifications
  return undefined;
}


// --- Create LlmAgent and Assign Callback ---
const myLlmAgent = new LlmAgent({
  name: "AfterModelCallbackAgent",
  model: MODEL_NAME,
  instruction: "You are a helpful assistant who tells jokes.",
  description: "An LLM agent demonstrating after_model_callback",
  afterModelCallback: simpleAfterModelModifier, // Assign the function here
});

// --- Agent Interaction Logic ---
async function callAgentAndPrint({runner, query, sessionId,}: {  runner: InMemoryRunner;  query: string;  sessionId: string;}) {
  console.log(`\n>>> Calling Agent with query: "${query}"`);

  let finalResponseContent = "No final response received.";
  const events = runner.runAsync({
    userId: USER_ID,
    sessionId: sessionId,
    newMessage: createUserContent(query),
  });

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

  // Scenario 1: The callback will find "joke" and modify the response
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID_JOKE,
  });
  await callAgentAndPrint({
    runner: runner,
    query: 'write a short joke about computers',
    sessionId: SESSION_ID_JOKE,
  });

  // Scenario 2: The callback will not find "joke" and will pass the response through unmodified
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID_POEM,
  });
  await callAgentAndPrint({
    runner: runner,
    query: 'write a short poem about coding',
    sessionId: SESSION_ID_POEM,
  });
}

main();
