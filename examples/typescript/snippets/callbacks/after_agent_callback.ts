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
  CallbackContext,
  isFinalResponse,
  InMemoryRunner,
} from "@google/adk";
import { createUserContent } from "@google/genai";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "after_agent_callback_app";
const USER_ID = "test_user_after_agent";
const SESSION_NORMAL_ID = "session_run_normally_ts";
const SESSION_MODIFY_ID = "session_modify_output_ts";

// --- 1. Define the Callback Function ---
/**
 * Logs exit from an agent and checks "add_concluding_note" in session state.
 * If True, returns new Content to *replace* the agent's original output.
 * If False or not present, returns void, allowing the agent's original output to be used.
 */
function modifyOutputAfterAgent(context: CallbackContext): any {
  const agentName = context.agentName;
  const invocationId = context.invocationId;
  const currentState = context.state;

  console.log(
    `
[Callback] Exiting agent: ${agentName} (Inv: ${invocationId})`
  );
  console.log(`[Callback] Current State:`, currentState);

  // Example: Check state to decide whether to modify the final output
  if (currentState.get("add_concluding_note") === true) {
    console.log(
      `[Callback] State condition "add_concluding_note=true" met: Replacing agent ${agentName}'s output.`
    );
    // Return Content to *replace* the agent's own output
    return createUserContent(
      "Concluding note added by after_agent_callback, replacing original output."
    );
  } else {
    console.log(
      `[Callback] State condition not met: Using agent ${agentName}'s original output.`
    );
    // Return void/undefined - the agent's output will be used.
    return;
  }
}

// --- 2. Setup Agent with Callback ---
const llmAgentWithAfterCb = new LlmAgent({
  name: "MySimpleAgentWithAfter",
  model: MODEL_NAME,
  instruction: "You are a simple agent. Just say \"Processing complete!\"",
  description:
    "An LLM agent demonstrating after_agent_callback for output modification",
  afterAgentCallback: modifyOutputAfterAgent, // Assign the callback here
});

// --- 3. Run the Agent ---
async function main() {
  const runner = new InMemoryRunner({
    agent: llmAgentWithAfterCb,
    appName: APP_NAME,
  });

  // Create session 1: Agent output will be used as is (default empty state)
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_NORMAL_ID,
  });

  // Create session 2: Agent output will be replaced by the callback
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_MODIFY_ID,
    state: { add_concluding_note: true }, // Set the state flag here
  });

  // --- Scenario 1: Run where callback allows agent's original output ---
  console.log(
    `
==================== SCENARIO 1: Running Agent on Session "${SESSION_NORMAL_ID}" (Should Use Original Output) ====================
`
  );
  const eventsNormal = runner.runAsync({
    userId: USER_ID,
    sessionId: SESSION_NORMAL_ID,
    newMessage: createUserContent("Process this please."),
  });

  for await (const event of eventsNormal) {
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

  // --- Scenario 2: Run where callback replaces the agent's output ---
  console.log(
    `
==================== SCENARIO 2: Running Agent on Session "${SESSION_MODIFY_ID}" (Should Replace Output) ====================
`
  );
  const eventsModify = runner.runAsync({
    userId: USER_ID,
    sessionId: SESSION_MODIFY_ID,
    newMessage: createUserContent("Process this and add note."),
  });

  for await (const event of eventsModify) {
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

main();
