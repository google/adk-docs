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
  LlmRequest,
  LlmResponse,
} from '../../../../../../repos/adk-js/core/src/index';
import { Content, createUserContent, Part } from '@google/genai';

const MODEL_NAME = 'gemini-1.5-flash-latest';

// --- Define the Callback Function ---
function simpleBeforeModelModifier(
  callbackContext: CallbackContext,
  llmRequest: LlmRequest,
): LlmResponse | undefined {
  'use strict';
  const agentName = callbackContext.agentName;
  console.log(`[Callback] Before model call for agent: ${agentName}`);

  let lastUserMessage = '';
  const lastContent = llmRequest.contents[llmRequest.contents.length - 1];
  if (lastContent?.role === 'user' && lastContent.parts[0]?.text) {
    lastUserMessage = lastContent.parts[0].text;
  }
  console.log(`[Callback] Inspecting last user message: '${lastUserMessage}'`);

  // --- Modification Example ---
  const prefix = '[Modified by Callback] ';
  if (!llmRequest.config.systemInstruction) {
    llmRequest.config.systemInstruction = { role: 'system', parts: [{ text: '' }] };
  } else if (typeof llmRequest.config.systemInstruction === 'string') {
    llmRequest.config.systemInstruction = {
      role: 'system',
      parts: [{ text: llmRequest.config.systemInstruction }],
    };
  }

  const instructionPart = (llmRequest.config.systemInstruction as Content).parts[0] as Part;
  const modifiedText = prefix + (instructionPart.text || '');
  instructionPart.text = modifiedText;
  console.log(`[Callback] Modified system instruction to: '${modifiedText}'`);

  // --- Skip Example ---
  if (lastUserMessage.toUpperCase().includes('BLOCK')) {
    console.log("[Callback] 'BLOCK' keyword found. Skipping LLM call.");
    return {
      content: {
        role: 'model',
        parts: [{ text: 'LLM call was blocked by before_model_callback.' }],
      },
    };
  }

  console.log('[Callback] Proceeding with LLM call.');
  return undefined;
}

// Create LlmAgent and Assign Callback
const myLlmAgent = new LlmAgent({
  name: 'ModelCallbackAgent',
  model: MODEL_NAME,
  instruction: 'You are a helpful assistant.',
  description: 'An LLM agent demonstrating before_model_callback',
  beforeModelCallback: simpleBeforeModelModifier,
});

// Agent Interaction Logic
async function callAgentAndPrint(runner: InMemoryRunner, query: string) {
  const appName = 'before_model_demo';
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
  const runner = new InMemoryRunner({ agent: myLlmAgent, appName: 'before_model_demo' });

  // Scenario 1: Callback modifies the request
  await callAgentAndPrint(runner, 'Tell me a fact about the moon.');

  // Scenario 2: Callback skips the LLM call
  await callAgentAndPrint(runner, 'Tell me a fact about the sun, but BLOCK the call.');
}

main();
