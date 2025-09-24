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
} from '../../../../../../repos/adk-js/core/src/index';
import { Content, createUserContent } from '@google/genai';

const MODEL_NAME = 'gemini-1.5-flash-latest';

// --- 1. Define the Callback Function ---
function checkIfAgentShouldRun(
  callbackContext: CallbackContext,
): Content | undefined {
  'use strict';
  const agentName = callbackContext.agentName;
  const invocationId = callbackContext.invocationId;
  const currentState = callbackContext.state;

  console.log(`\n[Callback] Entering agent: ${agentName} (Inv: ${invocationId})`);
  console.log(`[Callback] Current State: ${JSON.stringify(currentState)}`);

  if (currentState['skip_llm_agent']) {
    console.log(`[Callback] State condition 'skip_llm_agent=true' met: Skipping agent ${agentName}.`);
    return {
      role: 'model',
      parts: [
        {
          text: `Agent ${agentName} skipped by before_agent_callback due to state.`,
        },
      ],
    };
  } else {
    console.log(`[Callback] State condition not met: Proceeding with agent ${agentName}.`);
    return undefined;
  }
}

// --- 2. Setup Agent with Callback ---
const llmAgentWithBeforeCb = new LlmAgent({
  name: 'MyControlledAgent',
  model: MODEL_NAME,
  instruction: 'You are a concise assistant.',
  description: 'An LLM agent demonstrating stateful before_agent_callback',
  beforeAgentCallback: checkIfAgentShouldRun,
});

// --- 3. Setup Runner and Sessions using InMemoryRunner ---
async function main() {
  const appName = 'before_agent_demo';
  const userId = 'test_user';
  const session_id_run = 'session_will_run';
  const session_id_skip = 'session_will_skip';

  const runner = new InMemoryRunner({ agent: llmAgentWithBeforeCb, appName: appName });
  const sessionService = runner.sessionService;

  sessionService.createSession({
    appName: appName,
    userId: userId,
    sessionId: session_id_run,
  });

  sessionService.createSession({
    appName: appName,
    userId: userId,
    sessionId: session_id_skip,
    state: { skip_llm_agent: true },
  });

  // --- Scenario 1: Run where callback allows agent execution ---
  console.log(
    '\n' + '='.repeat(20) + ` SCENARIO 1: Running Agent on Session '${session_id_run}' (Should Proceed) ` + '='.repeat(20)
  );
  for await (const event of runner.runAsync({
    userId: userId,
    sessionId: session_id_run,
    newMessage: createUserContent('Hello, please respond.'),
  })) {
    if (event.isFinalResponse() && event.content) {
      console.log(`Final Output: [${event.author}] ${event.content.parts[0].text?.trim()}`);
    } else if (event.isError()) {
      console.log(`Error Event: ${event.errorDetails}`);
    }
  }

  // --- Scenario 2: Run where callback intercepts and skips agent ---
  console.log(
    '\n' + '='.repeat(20) + ` SCENARIO 2: Running Agent on Session '${session_id_skip}' (Should Skip) ` + '='.repeat(20)
  );
  for await (const event of runner.runAsync({
    userId: userId,
    sessionId: session_id_skip,
    newMessage: createUserContent("This message won't reach the LLM."),
  })) {
    if (event.isFinalResponse() && event.content) {
      console.log(`Final Output: [${event.author}] ${event.content.parts[0].text?.trim()}`);
    } else if (event.isError()) {
      console.log(`Error Event: ${event.errorDetails}`);
    }
  }
}

main();
