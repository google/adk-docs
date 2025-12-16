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

// --8<-- [start:callback_basic]
import {
  LlmAgent,
  InMemoryRunner,
  CallbackContext,
  LlmRequest,
  LlmResponse,
  Event,
  isFinalResponse,
} from "@google/adk";
import { createUserContent } from "@google/genai";
import type { Content } from "@google/genai";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "basic_callback_app";
const USER_ID = "test_user_basic";
const SESSION_ID = "session_basic_001";


// --- Define your callback function ---
function myBeforeModelLogic({
  context,
  request,
}: {
  context: CallbackContext;
  request: LlmRequest;
}): LlmResponse | undefined {
  console.log(
    `Callback running before model call for agent: ${context.agentName}`
  );
  // ... your custom logic here ...
  return undefined; // Allow the model call to proceed
}

// --- Register it during Agent creation ---
const myAgent = new LlmAgent({
  name: "MyCallbackAgent",
  model: MODEL_NAME,
  instruction: "Be helpful.",
  beforeModelCallback: myBeforeModelLogic,
});
// --8<-- [end:callback_basic]

// Agent Interaction
async function callAgentAsync(query: string) {
  const content: Content = createUserContent(query);

  // The InMemoryRunner creates and manages its own session service.
  const runner = new InMemoryRunner({
    agent: myAgent,
    appName: APP_NAME,
  });
 
  // Create the session before running the agent. The runner will not
  // create it automatically.
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID,
  });

  // The run method returns an async iterator for the events
  const events = runner.runAsync({
    userId: USER_ID,
    sessionId: SESSION_ID,
    newMessage: content,
  });

  for await (const event of events) {
    // In a real application, you would handle different event types.
    // For this example, we'll just print the final text response.
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const finalResponse =
        event.content?.parts?.[0]?.text ?? "No response text found.";
      console.log("Agent Response: ", finalResponse);
    }
  }
}

(async () => {
  await callAgentAsync("write a short joke");
})();
