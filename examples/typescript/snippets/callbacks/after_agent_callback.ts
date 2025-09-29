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
import { Content, Part } from "@google/genai";

// --- 1. Define the Callback Function ---
/**
 * Logs exit from an agent and checks 'add_concluding_note' in session state.
 * If True, returns new Content to *replace* the agent's original output.
 * If False or not present, returns void, allowing the agent's original output to be used.
 */
function modifyOutputAfterAgent(context: CallbackContext): Content | undefined {
  const agentName = context.agentName;
  const invocationId = context.invocationId;
  const currentState = context.state;

  console.log(
    `\n[Callback] Exiting agent: ${agentName} (Inv: ${invocationId})`
  );
  console.log(`[Callback] Current State:`, currentState);

  // Example: Check state to decide whether to modify the final output
  if (currentState.get("add_concluding_note") === true) {
    console.log(
      `[Callback] State condition 'add_concluding_note=true' met: Replacing agent ${agentName}'s output.`
    );
    // Return Content to *replace* the agent's own output
    return {
      parts: [
        {
          text: `Concluding note added by after_agent_callback, replacing original output.`,
        },
      ],
      role: "model", // Assign model role to the overriding response
    };
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
  model: "gemini-2.5-flash",
  instruction: "You are a simple agent. Just say 'Processing complete!'",
  description:
    "An LLM agent demonstrating after_agent_callback for output modification",
  afterAgentCallback: modifyOutputAfterAgent, // Assign the callback here
});

// --- 3. Run the Agent ---
async function main() {
  const appName = "after_agent_demo_ts";
  const userId = "test_user_after_ts";
  const sessionNormalId = "session_run_normally_ts";
  const sessionModifyId = "session_modify_output_ts";

  const runner = new InMemoryRunner({
    agent: llmAgentWithAfterCb,
    appName: appName,
  });

  // Create session 1: Agent output will be used as is (default empty state)
  await runner.sessionService.createSession({
    appName: appName,
    userId: userId,
    sessionId: sessionNormalId,
  });

  // Create session 2: Agent output will be replaced by the callback
  await runner.sessionService.createSession({
    appName: appName,
    userId: userId,
    sessionId: sessionModifyId,
    state: { add_concluding_note: true }, // Set the state flag here
  });

  // --- Scenario 1: Run where callback allows agent's original output ---
  console.log(
    "\n" +
      "=".repeat(20) +
      ` SCENARIO 1: Running Agent on Session '${sessionNormalId}' (Should Use Original Output) ` +
      "=".repeat(20)
  );
  const eventsNormal = runner.run({
    userId,
    sessionId: sessionNormalId,
    newMessage: { role: "user", parts: [{ text: "Process this please." }] },
  });

  for await (const event of eventsNormal) {
    if (isFinalResponse(event) && event.content?.parts) {
      const finalResponse = event.content.parts
        .map((part: Part) => part.text ?? "")
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
    "\n" +
      "=".repeat(20) +
      ` SCENARIO 2: Running Agent on Session '${sessionModifyId}' (Should Replace Output) ` +
      "=".repeat(20)
  );
  const eventsModify = runner.run({
    userId,
    sessionId: sessionModifyId,
    newMessage: {
      role: "user",
      parts: [{ text: "Process this and add note." }],
    },
  });

  for await (const event of eventsModify) {
    if (isFinalResponse(event) && event.content?.parts) {
      const finalResponse = event.content.parts
        .map((part: Part) => part.text ?? "")
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
