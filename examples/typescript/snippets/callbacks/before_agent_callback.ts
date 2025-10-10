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
import { Content, createUserContent } from "@google/genai";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "before_agent_callback_app";
const USER_ID = "test_user_before_agent";
const SESSION_ID_RUN = "session_will_run";
const SESSION_ID_SKIP = "session_will_skip";


// --- 1. Define the Callback Function ---
function checkIfAgentShouldRun(
  callbackContext: CallbackContext
): Content | undefined {
  /**
   * Logs entry and checks 'skip_llm_agent' in session state.
   * If True, returns Content to skip the agent's execution.
   * If False or not present, returns undefined to allow execution.
   */
  const agentName = callbackContext.agentName;
  const invocationId = callbackContext.invocationId;
  const currentState = callbackContext.state;

  console.log(`\n[Callback] Entering agent: ${agentName} (Inv: ${invocationId})`);
  console.log(`[Callback] Current State:`, currentState);

  // Check the condition in session state
  if (currentState.get("skip_llm_agent") === true) {
    console.log(
      `[Callback] State condition 'skip_llm_agent=True' met: Skipping agent ${agentName}.`
    );
    // Return Content to skip the agent's run
    return {
      parts: [
        {
          text: `Agent ${agentName} skipped by before_agent_callback due to state.`,
        },
      ],
      role: "model", // Assign model role to the overriding response
    };
  } else {
    console.log(
      `[Callback] State condition not met: Proceeding with agent ${agentName}.`
    );
    // Return undefined to allow the LlmAgent's normal execution
    return undefined;
  }
}

// --- 2. Setup Agent with Callback ---
const llmAgentWithBeforeCb = new LlmAgent({
  name: "MyControlledAgent",
  model: MODEL_NAME,
  instruction: "You are a concise assistant.",
  description: "An LLM agent demonstrating stateful before_agent_callback",
  beforeAgentCallback: checkIfAgentShouldRun, // Assign the callback
});

// --- 3. Setup Runner and Sessions using InMemoryRunner ---
async function main() {
  // Use InMemoryRunner - it includes InMemorySessionService
  const runner = new InMemoryRunner({
    agent: llmAgentWithBeforeCb,
    appName: APP_NAME,
  });

  // Create session 1: Agent will run (default empty state)
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID_RUN,
    // No initial state means 'skip_llm_agent' will be False in the callback check
  });

  // Create session 2: Agent will be skipped (state has skip_llm_agent=True)
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID_SKIP,
    state: { skip_llm_agent: true }, // Set the state flag here
  });

  // --- Scenario 1: Run where callback allows agent execution ---
  console.log(
    `\n==================== SCENARIO 1: Running Agent on Session "${SESSION_ID_RUN}" (Should Proceed) ====================`
  );
  const eventsRun = runner.runAsync({
    userId: USER_ID,
    sessionId: SESSION_ID_RUN,
    newMessage: createUserContent("Hello, please respond."),
  });

  for await (const event of eventsRun) {
    // Print final output (either from LLM or callback override)
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const finalResponse = event.content.parts
        .map((part: any) => part.text ?? "")
        .join("");
      console.log(
        `Final Output: [${event.author}] ${finalResponse.trim()}`
      );
    } else if (event.errorMessage) {
      console.log(`Error Event: ${event.errorMessage}`);
    }
  }

  // --- Scenario 2: Run where callback intercepts and skips agent ---
  console.log(
    `\n==================== SCENARIO 2: Running Agent on Session "${SESSION_ID_SKIP}" (Should Skip) ====================`
  );
  const eventsSkip = runner.runAsync({
    userId: USER_ID,
    sessionId: SESSION_ID_SKIP,
    newMessage: createUserContent("This message won't reach the LLM."),
  });

  for await (const event of eventsSkip) {
    // Print final output (either from LLM or callback override)
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const finalResponse = event.content.parts
        .map((part: any) => part.text ?? "")
        .join("");
      console.log(
        `Final Output: [${event.author}] ${finalResponse.trim()}`
      );
    } else if (event.errorMessage) {
      console.log(`Error Event: ${event.errorMessage}`);
    }
  }
}

// --- 4. Execute ---
main();
