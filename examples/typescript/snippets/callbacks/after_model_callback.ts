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
  LlmResponse,
  Part,
} from '../../../../../../repos/adk-js/core/src/index';
import { Content, createUserContent } from '@google/genai';

const MODEL_NAME = 'gemini-1.5-flash-latest';
const APP_NAME = 'after_model_callback_app';
const USER_ID = 'user_1';
const SESSION_ID = 'session_001';

// --- Define the Callback Function ---
function simpleAfterModelModifier(
  callbackContext: CallbackContext,
  llmResponse: LlmResponse,
): LlmResponse | undefined {
  'use strict';
  const agentName = callbackContext.agentName;
  console.log(`[Callback] After model call for agent: ${agentName}`);

  // --- Inspection ---
  let originalText = '';
  if (llmResponse.content && llmResponse.content.parts) {
    if (llmResponse.content.parts[0].text) {
      originalText = llmResponse.content.parts[0].text;
      console.log(
        `[Callback] Inspected original response text: '${originalText.substring(
          0,
          100,
        )}...'`,
      );
    } else if (llmResponse.content.parts[0].functionCall) {
      console.log(
        `[Callback] Inspected response: Contains function call '${llmResponse.content.parts[0].functionCall.name}'. No text modification.`,
      );
      return undefined;
    } else {
      console.log('[Callback] Inspected response: No text content found.');
      return undefined;
    }
  } else if (llmResponse.errorMessage) {
    console.log(
      `[Callback] Inspected response: Contains error '${llmResponse.errorMessage}'. No modification.`,
    );
    return undefined;
  } else {
    console.log('[Callback] Inspected response: Empty LlmResponse.');
    return undefined;
  }

  // --- Modification Example ---
  const searchTerm = 'joke';
  const replaceTerm = 'funny story';
  if (originalText.toLowerCase().includes(searchTerm)) {
    console.log(`[Callback] Found '${searchTerm}'. Modifying response.`);
    let modifiedText = originalText.replace(new RegExp(searchTerm, 'gi'), replaceTerm);

    const modifiedParts: Part[] = JSON.parse(
      JSON.stringify(llmResponse.content.parts),
    );
    modifiedParts[0].text = modifiedText;

    const newResponse: LlmResponse = {
      content: { role: 'model', parts: modifiedParts },
      groundingMetadata: llmResponse.groundingMetadata,
    };
    console.log(`[Callback] Returning modified response.`);
    return newResponse;
  } else {
    console.log(
      `[Callback] '${searchTerm}' not found. Passing original response through.`,
    );
    return undefined;
  }
}

// Create LlmAgent and Assign Callback
const myLlmAgent = new LlmAgent({
  name: 'AfterModelCallbackAgent',
  model: MODEL_NAME,
  instruction: 'You are a helpful assistant.',
  description: 'An LLM agent demonstrating after_model_callback',
  afterModelCallback: simpleAfterModelModifier,
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
  const message: Content = createUserContent(query);

  let finalResponseContent = 'No final response received.';
  for await (const event of runner.run({
    userId: USER_ID,
    sessionId: sessionId,
    newMessage: message,
  })) {
    const authorName = event.author || 'System';
    if (event.content?.parts && event.isFinalResponse()) {
      finalResponseContent = event.content.parts.map((part) => part.text ?? '').join('');
      console.log(`
--- Output from: ${authorName} ---
`);
      console.log(finalResponseContent);
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
    id: SESSION_ID,
  });

  await callAgentAndPrint(
    runner,
    myLlmAgent,
    SESSION_ID,
    'Tell me a short joke.',
  );
  await callAgentAndPrint(
    runner,
    myLlmAgent,
    SESSION_ID,
    'What is the capital of France?',
  );
}

main();
