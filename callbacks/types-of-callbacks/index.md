# Types of Callbacks

Supported in ADKPython v0.1.0TypeScript v0.2.0Go v0.1.0Java v0.1.0

The framework provides different types of callbacks that trigger at various stages of an agent's execution. Understanding when each callback fires and what context it receives is key to using them effectively.

## Agent Lifecycle Callbacks

These callbacks are available on *any* agent that inherits from `BaseAgent` (including `LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent`, etc).

Note

The specific method names or return types may vary slightly by SDK language (e.g., return `None` in Python, return `Optional.empty()` or `Maybe.empty()` in Java). Refer to the language-specific API documentation for details.

### Before Agent Callback

**When:** Called *immediately before* the agent's `_run_async_impl` (or `_run_live_impl`) method is executed. It runs after the agent's `InvocationContext` is created but *before* its core logic begins.

**Purpose:** Ideal for setting up resources or state needed only for this specific agent's run, performing validation checks on the session state (callback_context.state) before execution starts, logging the entry point of the agent's activity, or potentially modifying the invocation context before the core logic uses it.

Code

```python
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# # --- Setup Instructions ---
# # 1. Install the ADK package:
# !pip install google-adk
# # Make sure to restart kernel if using colab/jupyter notebooks

# # 2. Set up your Gemini API Key:
# #    - Get a key from Google AI Studio: https://aistudio.google.com/app/apikey
# #    - Set it as an environment variable:
# import os
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE" # <--- REPLACE with your actual key
# # Or learn about other authentication methods (like Vertex AI):
# # https://google.github.io/adk-docs/agents/models/

# ADK Imports
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import InMemoryRunner # Use InMemoryRunner
from google.genai import types # For types.Content
from typing import Optional

# Define the model - Use the specific model name requested
GEMINI_2_FLASH="gemini-2.0-flash"

# --- 1. Define the Callback Function ---
def check_if_agent_should_run(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Logs entry and checks 'skip_llm_agent' in session state.
    If True, returns Content to skip the agent's execution.
    If False or not present, returns None to allow execution.
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    print(f"\n[Callback] Entering agent: {agent_name} (Inv: {invocation_id})")
    print(f"[Callback] Current State: {current_state}")

    # Check the condition in session state dictionary
    if current_state.get("skip_llm_agent", False):
        print(f"[Callback] State condition 'skip_llm_agent=True' met: Skipping agent {agent_name}.")
        # Return Content to skip the agent's run
        return types.Content(
            parts=[types.Part(text=f"Agent {agent_name} skipped by before_agent_callback due to state.")],
            role="model" # Assign model role to the overriding response
        )
    else:
        print(f"[Callback] State condition not met: Proceeding with agent {agent_name}.")
        # Return None to allow the LlmAgent's normal execution
        return None

# --- 2. Setup Agent with Callback ---
llm_agent_with_before_cb = LlmAgent(
    name="MyControlledAgent",
    model=GEMINI_2_FLASH,
    instruction="You are a concise assistant.",
    description="An LLM agent demonstrating stateful before_agent_callback",
    before_agent_callback=check_if_agent_should_run # Assign the callback
)

# --- 3. Setup Runner and Sessions using InMemoryRunner ---
async def main():
    app_name = "before_agent_demo"
    user_id = "test_user"
    session_id_run = "session_will_run"
    session_id_skip = "session_will_skip"

    # Use InMemoryRunner - it includes InMemorySessionService
    runner = InMemoryRunner(agent=llm_agent_with_before_cb, app_name=app_name)
    # Get the bundled session service to create sessions
    session_service = runner.session_service

    # Create session 1: Agent will run (default empty state)
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_run
        # No initial state means 'skip_llm_agent' will be False in the callback check
    )

    # Create session 2: Agent will be skipped (state has skip_llm_agent=True)
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_skip,
        state={"skip_llm_agent": True} # Set the state flag here
    )

    # --- Scenario 1: Run where callback allows agent execution ---
    print("\n" + "="*20 + f" SCENARIO 1: Running Agent on Session '{session_id_run}' (Should Proceed) " + "="*20)
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_run,
        new_message=types.Content(role="user", parts=[types.Part(text="Hello, please respond.")])
    ):
        # Print final output (either from LLM or callback override)
        if event.is_final_response() and event.content:
            print(f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}")
        elif event.is_error():
             print(f"Error Event: {event.error_details}")

    # --- Scenario 2: Run where callback intercepts and skips agent ---
    print("\n" + "="*20 + f" SCENARIO 2: Running Agent on Session '{session_id_skip}' (Should Skip) " + "="*20)
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_skip,
        new_message=types.Content(role="user", parts=[types.Part(text="This message won't reach the LLM.")])
    ):
         # Print final output (either from LLM or callback override)
         if event.is_final_response() and event.content:
            print(f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}")
         elif event.is_error():
             print(f"Error Event: {event.error_details}")

# --- 4. Execute ---
# In a Python script:
# import asyncio
# if __name__ == "__main__":
#     # Make sure GOOGLE_API_KEY environment variable is set if not using Vertex AI auth
#     # Or ensure Application Default Credentials (ADC) are configured for Vertex AI
#     asyncio.run(main())

# In a Jupyter Notebook or similar environment:
await main()
```

```typescript
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
```

```go
package main

import (
    "context"
    "fmt"
    "log"
    "regexp"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)



// 1. Define the Callback Function
func onBeforeAgent(ctx agent.CallbackContext) (*genai.Content, error) {
    agentName := ctx.AgentName()
    log.Printf("[Callback] Entering agent: %s", agentName)
    if skip, _ := ctx.State().Get("skip_llm_agent"); skip == true {
        log.Printf("[Callback] State condition met: Skipping agent %s", agentName)
        return genai.NewContentFromText(
                fmt.Sprintf("Agent %s skipped by before_agent_callback.", agentName),
                genai.RoleModel,
            ),
            nil
    }
    log.Printf("[Callback] State condition not met: Running agent %s", agentName)
    return nil, nil
}

// 2. Define a function to set up and run the agent with the callback.
func runBeforeAgentExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("FATAL: Failed to create model: %v", err)
    }

    // 3. Register the callback in the agent configuration.
    llmCfg := llmagent.Config{
        Name:                 "AgentWithBeforeAgentCallback",
        BeforeAgentCallbacks: []agent.BeforeAgentCallback{onBeforeAgent},
        Model:                geminiModel,
        Instruction:          "You are a concise assistant.",
    }
    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("FATAL: Failed to create agent: %v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
    if err != nil {
        log.Fatalf("FATAL: Failed to create runner: %v", err)
    }

    // 4. Run scenarios to demonstrate the callback's behavior.
    log.Println("--- SCENARIO 1: Agent should run normally ---")
    runScenario(ctx, r, sessionService, appName, "session_normal", nil, "Hello, world!")

    log.Println("\n--- SCENARIO 2: Agent should be skipped ---")
    runScenario(ctx, r, sessionService, appName, "session_skip", map[string]any{"skip_llm_agent": true}, "This should be skipped.")
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.CallbackContext;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.sessions.State;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class BeforeAgentCallbackExample {

  private static final String APP_NAME = "AgentWithBeforeAgentCallback";
  private static final String USER_ID = "test_user_456";
  private static final String SESSION_ID = "session_id_123";
  private static final String MODEL_NAME = "gemini-2.0-flash";

  public static void main(String[] args) {
    BeforeAgentCallbackExample callbackAgent = new BeforeAgentCallbackExample();
    callbackAgent.defineAgent("Write a document about a cat");
  }

  // --- 1. Define the Callback Function ---
  /**
   * Logs entry and checks 'skip_llm_agent' in session state. If True, returns Content to skip the
   * agent's execution. If False or not present, returns None to allow execution.
   */
  public Maybe<Content> checkIfAgentShouldRun(CallbackContext callbackContext) {
    String agentName = callbackContext.agentName();
    String invocationId = callbackContext.invocationId();
    State currentState = callbackContext.state();

    System.out.printf("%n[Callback] Entering agent: %s (Inv: %s)%n", agentName, invocationId);
    System.out.printf("[Callback] Current State: %s%n", currentState.entrySet());

    // Check the condition in session state dictionary
    if (Boolean.TRUE.equals(currentState.get("skip_llm_agent"))) {
      System.out.printf(
          "[Callback] State condition 'skip_llm_agent=True' met: Skipping agent %s", agentName);
      // Return Content to skip the agent's run
      return Maybe.just(
          Content.fromParts(
              Part.fromText(
                  String.format(
                      "Agent %s skipped by before_agent_callback due to state.", agentName))));
    }

    System.out.printf(
        "[Callback] State condition 'skip_llm_agent=True' NOT met: Running agent %s \n", agentName);
    // Return empty response to allow the LlmAgent's normal execution
    return Maybe.empty();
  }

  public void defineAgent(String prompt) {
    // --- 2. Setup Agent with Callback ---
    BaseAgent llmAgentWithBeforeCallback =
        LlmAgent.builder()
            .model(MODEL_NAME)
            .name(APP_NAME)
            .instruction("You are a concise assistant.")
            .description("An LLM agent demonstrating stateful before_agent_callback")
            // You can also use a sync version of this callback "beforeAgentCallbackSync"
            .beforeAgentCallback(this::checkIfAgentShouldRun)
            .build();

    // --- 3. Setup Runner and Sessions using InMemoryRunner ---

    // Use InMemoryRunner - it includes InMemorySessionService
    InMemoryRunner runner = new InMemoryRunner(llmAgentWithBeforeCallback, APP_NAME);
    // Scenario 1: Initial state is null, which means 'skip_llm_agent' will be false in the callback
    // check
    runAgent(runner, null, prompt);
    // Scenario 2: Agent will be skipped (state has skip_llm_agent=true)
    runAgent(runner, new ConcurrentHashMap<>(Map.of("skip_llm_agent", true)), prompt);
  }

  public void runAgent(InMemoryRunner runner, ConcurrentHashMap<String, Object> initialState, String prompt) {
    // InMemoryRunner automatically creates a session service. Create a session using the service.
    Session session =
        runner
            .sessionService()
            .createSession(APP_NAME, USER_ID, initialState, SESSION_ID)
            .blockingGet();
    Content userMessage = Content.fromParts(Part.fromText(prompt));

    // Run the agent
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    // Print final output (either from LLM or callback override)
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
```

**Note on the `before_agent_callback` Example:**

- **What it Shows:** This example demonstrates the `before_agent_callback`. This callback runs *right before* the agent's main processing logic starts for a given request.
- **How it Works:** The callback function (`check_if_agent_should_run`) looks at a flag (`skip_llm_agent`) in the session's state.
  - If the flag is `True`, the callback returns a `types.Content` object. This tells the ADK framework to **skip** the agent's main execution entirely and use the callback's returned content as the final response.
  - If the flag is `False` (or not set), the callback returns `None` or an empty object. This tells the ADK framework to **proceed** with the agent's normal execution (calling the LLM in this case).
- **Expected Outcome:** You'll see two scenarios:
  1. In the session *with* the `skip_llm_agent: True` state, the agent's LLM call is bypassed, and the output comes directly from the callback ("Agent... skipped...").
  1. In the session *without* that state flag, the callback allows the agent to run, and you see the actual response from the LLM (e.g., "Hello!").
- **Understanding Callbacks:** This highlights how `before_` callbacks act as **gatekeepers**, allowing you to intercept execution *before* a major step and potentially prevent it based on checks (like state, input validation, permissions).

### After Agent Callback

**When:** Called *immediately after* the agent's `_run_async_impl` (or `_run_live_impl`) method successfully completes. It does *not* run if the agent was skipped due to `before_agent_callback` returning content or if `end_invocation` was set during the agent's run.

**Purpose:** Useful for cleanup tasks, post-execution validation, logging the completion of an agent's activity, modifying final state, or augmenting the agent's final output.

Code

```python
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# # --- Setup Instructions ---
# # 1. Install the ADK package:
# !pip install google-adk
# # Make sure to restart kernel if using colab/jupyter notebooks

# # 2. Set up your Gemini API Key:
# #    - Get a key from Google AI Studio: https://aistudio.google.com/app/apikey
# #    - Set it as an environment variable:
# import os
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE" # <--- REPLACE with your actual key
# # Or learn about other authentication methods (like Vertex AI):
# # https://google.github.io/adk-docs/agents/models/


# ADK Imports
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import InMemoryRunner # Use InMemoryRunner
from google.genai import types # For types.Content
from typing import Optional

# Define the model - Use the specific model name requested
GEMINI_2_FLASH="gemini-2.0-flash"

# --- 1. Define the Callback Function ---
def modify_output_after_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Logs exit from an agent and checks 'add_concluding_note' in session state.
    If True, returns new Content to *replace* the agent's original output.
    If False or not present, returns None, allowing the agent's original output to be used.
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    print(f"\n[Callback] Exiting agent: {agent_name} (Inv: {invocation_id})")
    print(f"[Callback] Current State: {current_state}")

    # Example: Check state to decide whether to modify the final output
    if current_state.get("add_concluding_note", False):
        print(f"[Callback] State condition 'add_concluding_note=True' met: Replacing agent {agent_name}'s output.")
        # Return Content to *replace* the agent's own output
        return types.Content(
            parts=[types.Part(text=f"Concluding note added by after_agent_callback, replacing original output.")],
            role="model" # Assign model role to the overriding response
        )
    else:
        print(f"[Callback] State condition not met: Using agent {agent_name}'s original output.")
        # Return None - the agent's output produced just before this callback will be used.
        return None

# --- 2. Setup Agent with Callback ---
llm_agent_with_after_cb = LlmAgent(
    name="MySimpleAgentWithAfter",
    model=GEMINI_2_FLASH,
    instruction="You are a simple agent. Just say 'Processing complete!'",
    description="An LLM agent demonstrating after_agent_callback for output modification",
    after_agent_callback=modify_output_after_agent # Assign the callback here
)

# --- 3. Setup Runner and Sessions using InMemoryRunner ---
async def main():
    app_name = "after_agent_demo"
    user_id = "test_user_after"
    session_id_normal = "session_run_normally"
    session_id_modify = "session_modify_output"

    # Use InMemoryRunner - it includes InMemorySessionService
    runner = InMemoryRunner(agent=llm_agent_with_after_cb, app_name=app_name)
    # Get the bundled session service to create sessions
    session_service = runner.session_service

    # Create session 1: Agent output will be used as is (default empty state)
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_normal
        # No initial state means 'add_concluding_note' will be False in the callback check
    )
    # print(f"Session '{session_id_normal}' created with default state.")

    # Create session 2: Agent output will be replaced by the callback
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_modify,
        state={"add_concluding_note": True} # Set the state flag here
    )
    # print(f"Session '{session_id_modify}' created with state={{'add_concluding_note': True}}.")


    # --- Scenario 1: Run where callback allows agent's original output ---
    print("\n" + "="*20 + f" SCENARIO 1: Running Agent on Session '{session_id_normal}' (Should Use Original Output) " + "="*20)
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_normal,
        new_message=types.Content(role="user", parts=[types.Part(text="Process this please.")])
    ):
        # Print final output (either from LLM or callback override)
        if event.is_final_response() and event.content:
            print(f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}")
        elif event.is_error():
             print(f"Error Event: {event.error_details}")

    # --- Scenario 2: Run where callback replaces the agent's output ---
    print("\n" + "="*20 + f" SCENARIO 2: Running Agent on Session '{session_id_modify}' (Should Replace Output) " + "="*20)
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_modify,
        new_message=types.Content(role="user", parts=[types.Part(text="Process this and add note.")])
    ):
         # Print final output (either from LLM or callback override)
         if event.is_final_response() and event.content:
            print(f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}")
         elif event.is_error():
             print(f"Error Event: {event.error_details}")

# --- 4. Execute ---
# In a Python script:
# import asyncio
# if __name__ == "__main__":
#     # Make sure GOOGLE_API_KEY environment variable is set if not using Vertex AI auth
#     # Or ensure Application Default Credentials (ADC) are configured for Vertex AI
#     asyncio.run(main())

# In a Jupyter Notebook or similar environment:
await main()
```

```typescript
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
```

```go
package main

import (
    "context"
    "fmt"
    "log"
    "regexp"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)



func onAfterAgent(ctx agent.CallbackContext) (*genai.Content, error) {
    agentName := ctx.AgentName()
    invocationID := ctx.InvocationID()
    state := ctx.State()

    log.Printf("\n[Callback] Exiting agent: %s (Inv: %s)", agentName, invocationID)
    log.Printf("[Callback] Current State: %v", state)

    if addNote, _ := state.Get("add_concluding_note"); addNote == true {
        log.Printf("[Callback] State condition 'add_concluding_note=True' met: Replacing agent %s's output.", agentName)
        return genai.NewContentFromText(
            "Concluding note added by after_agent_callback, replacing original output.",
            genai.RoleModel,
        ), nil
    }

    log.Printf("[Callback] State condition not met: Using agent %s's original output.", agentName)
    return nil, nil
}

func runAfterAgentExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("FATAL: Failed to create model: %v", err)
    }

    llmCfg := llmagent.Config{
        Name:                "AgentWithAfterAgentCallback",
        AfterAgentCallbacks: []agent.AfterAgentCallback{onAfterAgent},
        Model:               geminiModel,
        Instruction:         "You are a simple agent. Just say 'Processing complete!'",
    }
    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("FATAL: Failed to create agent: %v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
    if err != nil {
        log.Fatalf("FATAL: Failed to create runner: %v", err)
    }

    log.Println("--- SCENARIO 1: Should use original output ---")
    runScenario(ctx, r, sessionService, appName, "session_normal", nil, "Process this.")

    log.Println("\n--- SCENARIO 2: Should replace output ---")
    runScenario(ctx, r, sessionService, appName, "session_modify", map[string]any{"add_concluding_note": true}, "Process and add note.")
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.CallbackContext;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.State;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class AfterAgentCallbackExample {

  // --- Constants ---
  private static final String APP_NAME = "after_agent_demo";
  private static final String USER_ID = "test_user_after";
  private static final String SESSION_ID_NORMAL = "session_run_normally";
  private static final String SESSION_ID_MODIFY = "session_modify_output";
  private static final String MODEL_NAME = "gemini-2.0-flash";

  public static void main(String[] args) {
    AfterAgentCallbackExample demo = new AfterAgentCallbackExample();
    demo.defineAgentAndRunScenarios();
  }

  // --- 1. Define the Callback Function ---
  /**
   * Log exit from an agent and checks 'add_concluding_note' in session state. If True, returns new
   * Content to *replace* the agent's original output. If False or not present, returns
   * Maybe.empty(), allowing the agent's original output to be used.
   */
  public Maybe<Content> modifyOutputAfterAgent(CallbackContext callbackContext) {
    String agentName = callbackContext.agentName();
    String invocationId = callbackContext.invocationId();
    State currentState = callbackContext.state();

    System.out.printf("%n[Callback] Exiting agent: %s (Inv: %s)%n", agentName, invocationId);
    System.out.printf("[Callback] Current State: %s%n", currentState.entrySet());

    Object addNoteFlag = currentState.get("add_concluding_note");

    // Example: Check state to decide whether to modify the final output
    if (Boolean.TRUE.equals(addNoteFlag)) {
      System.out.printf(
          "[Callback] State condition 'add_concluding_note=True' met: Replacing agent %s's"
              + " output.%n",
          agentName);

      // Return Content to *replace* the agent's own output
      return Maybe.just(
          Content.builder()
              .parts(
                  List.of(
                      Part.fromText(
                          "Concluding note added by after_agent_callback, replacing original output.")))
              .role("model") // Assign model role to the overriding response
              .build());

    } else {
      System.out.printf(
          "[Callback] State condition not met: Using agent %s's original output.%n", agentName);
      // Return None - the agent's output produced just before this callback will be used.
      return Maybe.empty();
    }
  }

  // --- 2. Setup Agent with Callback ---
  public void defineAgentAndRunScenarios() {
    LlmAgent llmAgentWithAfterCb =
        LlmAgent.builder()
            .name(APP_NAME)
            .model(MODEL_NAME)
            .description("An LLM agent demonstrating after_agent_callback for output modification")
            .instruction("You are a simple agent. Just say 'Processing complete!'")
            .afterAgentCallback(this::modifyOutputAfterAgent) // Assign the callback here
            .build();

    // --- 3. Setup Runner and Sessions using InMemoryRunner ---
    // Use InMemoryRunner - it includes InMemorySessionService
    InMemoryRunner runner = new InMemoryRunner(llmAgentWithAfterCb, APP_NAME);

    // --- Scenario 1: Run where callback allows agent's original output ---
    System.out.printf(
        "%n%s SCENARIO 1: Running Agent (Should Use Original Output) %s%n",
        "=".repeat(20), "=".repeat(20));
    // No initial state means 'add_concluding_note' will be false in the callback check
    runScenario(
        runner,
        llmAgentWithAfterCb.name(), // Use agent name for runner's appName consistency
        SESSION_ID_NORMAL,
        null,
        "Process this please.");

    // --- Scenario 2: Run where callback replaces the agent's output ---
    System.out.printf(
        "%n%s SCENARIO 2: Running Agent (Should Replace Output) %s%n",
        "=".repeat(20), "=".repeat(20));
    Map<String, Object> modifyState = new HashMap<>();
    modifyState.put("add_concluding_note", true); // Set the state flag here
    runScenario(
        runner,
        llmAgentWithAfterCb.name(), // Use agent name for runner's appName consistency
        SESSION_ID_MODIFY,
        new ConcurrentHashMap<>(modifyState),
        "Process this and add note.");
  }

  // --- 3. Method to Run a Single Scenario ---
  public void runScenario(
      InMemoryRunner runner,
      String appName,
      String sessionId,
      ConcurrentHashMap<String, Object> initialState,
      String userQuery) {

    // Create session using the runner's bundled session service
    runner.sessionService().createSession(appName, USER_ID, initialState, sessionId).blockingGet();

    System.out.printf(
        "Running scenario for session: %s, initial state: %s%n", sessionId, initialState);
    Content userMessage =
        Content.builder().role("user").parts(List.of(Part.fromText(userQuery))).build();

    Flowable<Event> eventStream = runner.runAsync(USER_ID, sessionId, userMessage);

    // Print final output
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse() && event.content().isPresent()) {
            String author = event.author() != null ? event.author() : "UNKNOWN";
            String text =
                event
                    .content()
                    .flatMap(Content::parts)
                    .filter(parts -> !parts.isEmpty())
                    .map(parts -> parts.get(0).text().orElse("").trim())
                    .orElse("[No text in final response]");
            System.out.printf("Final Output for %s: [%s] %s%n", sessionId, author, text);
          } else if (event.errorCode().isPresent()) {
            System.out.printf(
                "Error Event for %s: %s%n",
                sessionId, event.errorMessage().orElse("Unknown error"));
          }
        });
  }
}
```

**Note on the `after_agent_callback` Example:**

- **What it Shows:** This example demonstrates the `after_agent_callback`. This callback runs *right after* the agent's main processing logic has finished and produced its result, but *before* that result is finalized and returned.
- **How it Works:** The callback function (`modify_output_after_agent`) checks a flag (`add_concluding_note`) in the session's state.
  - If the flag is `True`, the callback returns a *new* `types.Content` object. This tells the ADK framework to **append** the agent's original output with the content returned by the callback.
  - If the flag is `False` (or not set), the callback returns `None` or an empty object. This tells the ADK framework to **use** the original output generated by the agent.
- **Expected Outcome:** You'll see two scenarios:
  1. In the session *without* the `add_concluding_note: True` state, the callback allows the agent's original output ("Processing complete!") to be used.
  1. In the session *with* that state flag, the callback intercepts the agent's original output and appends it with its own message ("Concluding note added...").
- **Understanding Callbacks:** This highlights how `after_` callbacks allow **post-processing** or **modification**. You can inspect the result of a step (the agent's run) and decide whether to let it pass through, change it, or completely replace it based on your logic.

## LLM Interaction Callbacks

These callbacks are specific to `LlmAgent` and provide hooks around the interaction with the Large Language Model.

### Before Model Callback

**When:** Called just before the `generate_content_async` (or equivalent) request is sent to the LLM within an `LlmAgent`'s flow.

**Purpose:** Allows inspection and modification of the request going to the LLM. Use cases include adding dynamic instructions, injecting few-shot examples based on state, modifying model config, implementing guardrails (like profanity filters), or implementing request-level caching.

**Return Value Effect:** If the callback returns `None` (or a `Maybe.empty()` object in Java), the LLM continues its normal workflow. If the callback returns an `LlmResponse` object, then the call to the LLM is **skipped**. The returned `LlmResponse` is used directly as if it came from the model. This is powerful for implementing guardrails or caching.

Code

```python
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.runners import Runner
from typing import Optional
from google.genai import types 
from google.adk.sessions import InMemorySessionService

GEMINI_2_FLASH="gemini-2.0-flash"

# --- Define the Callback Function ---
def simple_before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    print(f"[Callback] Before model call for agent: {agent_name}")

    # Inspect the last user message in the request contents
    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
         if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
    print(f"[Callback] Inspecting last user message: '{last_user_message}'")

    # --- Modification Example ---
    # Add a prefix to the system instruction
    original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
    prefix = "[Modified by Callback] "
    # Ensure system_instruction is Content and parts list exists
    if not isinstance(original_instruction, types.Content):
         # Handle case where it might be a string (though config expects Content)
         original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])
    if not original_instruction.parts:
        original_instruction.parts.append(types.Part(text="")) # Add an empty part if none exist

    # Modify the text of the first part
    modified_text = prefix + (original_instruction.parts[0].text or "")
    original_instruction.parts[0].text = modified_text
    llm_request.config.system_instruction = original_instruction
    print(f"[Callback] Modified system instruction to: '{modified_text}'")

    # --- Skip Example ---
    # Check if the last user message contains "BLOCK"
    if "BLOCK" in last_user_message.upper():
        print("[Callback] 'BLOCK' keyword found. Skipping LLM call.")
        # Return an LlmResponse to skip the actual LLM call
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="LLM call was blocked by before_model_callback.")],
            )
        )
    else:
        print("[Callback] Proceeding with LLM call.")
        # Return None to allow the (modified) request to go to the LLM
        return None


# Create LlmAgent and Assign Callback
my_llm_agent = LlmAgent(
        name="ModelCallbackAgent",
        model=GEMINI_2_FLASH,
        instruction="You are a helpful assistant.", # Base instruction
        description="An LLM agent demonstrating before_model_callback",
        before_model_callback=simple_before_model_modifier # Assign the function here
)

APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("write a joke on BLOCK")
```

```typescript
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
```

```go
package main

import (
    "context"
    "fmt"
    "log"
    "regexp"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)



func onBeforeModel(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
    log.Printf("[Callback] BeforeModel triggered for agent %q.", ctx.AgentName())

    // Modification Example: Add a prefix to the system instruction.
    if req.Config.SystemInstruction != nil {
        prefix := "[Modified by Callback] "
        // This is a simplified example; production code might need deeper checks.
        if len(req.Config.SystemInstruction.Parts) > 0 {
            req.Config.SystemInstruction.Parts[0].Text = prefix + req.Config.SystemInstruction.Parts[0].Text
        } else {
            req.Config.SystemInstruction.Parts = append(req.Config.SystemInstruction.Parts, &genai.Part{Text: prefix})
        }
        log.Printf("[Callback] Modified system instruction.")
    }

    // Skip Example: Check for "BLOCK" in the user's prompt.
    for _, content := range req.Contents {
        for _, part := range content.Parts {
            if strings.Contains(strings.ToUpper(part.Text), "BLOCK") {
                log.Println("[Callback] 'BLOCK' keyword found. Skipping LLM call.")
                return &model.LLMResponse{
                    Content: &genai.Content{
                        Parts: []*genai.Part{{Text: "LLM call was blocked by before_model_callback."}},
                        Role:  "model",
                    },
                }, nil
            }
        }
    }

    log.Println("[Callback] Proceeding with LLM call.")
    return nil, nil
}

func runBeforeModelExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("FATAL: Failed to create model: %v", err)
    }

    llmCfg := llmagent.Config{
        Name:                 "AgentWithBeforeModelCallback",
        Model:                geminiModel,
        BeforeModelCallbacks: []llmagent.BeforeModelCallback{onBeforeModel},
    }
    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("FATAL: Failed to create agent: %v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
    if err != nil {
        log.Fatalf("FATAL: Failed to create runner: %v", err)
    }

    log.Println("--- SCENARIO 1: Should proceed to LLM ---")
    runScenario(ctx, r, sessionService, appName, "session_normal", nil, "Tell me a fun fact.")

    log.Println("\n--- SCENARIO 2: Should be blocked by callback ---")
    runScenario(ctx, r, sessionService, appName, "session_blocked", nil, "write a joke on BLOCK")
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.CallbackContext;
import com.google.adk.events.Event;
import com.google.adk.models.LlmRequest;
import com.google.adk.models.LlmResponse;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterables;
import com.google.genai.types.Content;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.ArrayList;
import java.util.List;

public class BeforeModelCallbackExample {

  // --- Define Constants ---
  private static final String AGENT_NAME = "ModelCallbackAgent";
  private static final String MODEL_NAME = "gemini-2.0-flash";
  private static final String AGENT_INSTRUCTION = "You are a helpful assistant.";
  private static final String AGENT_DESCRIPTION =
      "An LLM agent demonstrating before_model_callback";

  // For session and runner
  private static final String APP_NAME = "guardrail_app_java";
  private static final String USER_ID = "user_1_java";

  public static void main(String[] args) {
    BeforeModelCallbackExample demo = new BeforeModelCallbackExample();
    demo.defineAgentAndRun();
  }

  // --- 1. Define the Callback Function ---
  // Inspects/modifies the LLM request or skips the actual LLM call.
  public Maybe<LlmResponse> simpleBeforeModelModifier(
      CallbackContext callbackContext, LlmRequest llmRequest) {
    String agentName = callbackContext.agentName();
    System.out.printf("%n[Callback] Before model call for agent: %s%n", agentName);

    String lastUserMessage = "";
    if (llmRequest.contents() != null && !llmRequest.contents().isEmpty()) {
      Content lastContentItem = Iterables.getLast(llmRequest.contents());
      if ("user".equals(lastContentItem.role().orElse(null))
          && lastContentItem.parts().isPresent()
          && !lastContentItem.parts().get().isEmpty()) {
        lastUserMessage = lastContentItem.parts().get().get(0).text().orElse("");
      }
    }
    System.out.printf("[Callback] Inspecting last user message: '%s'%n", lastUserMessage);

    // --- Modification Example ---
    // Add a prefix to the system instruction
    Content systemInstructionFromRequest = Content.builder().parts(ImmutableList.of()).build();
    // Ensure system_instruction is Content and parts list exists
    if (llmRequest.config().isPresent()) {
      systemInstructionFromRequest =
          llmRequest
              .config()
              .get()
              .systemInstruction()
              .orElseGet(() -> Content.builder().role("system").parts(ImmutableList.of()).build());
    }
    List<Part> currentSystemParts =
        new ArrayList<>(systemInstructionFromRequest.parts().orElse(ImmutableList.of()));
    // Ensure a part exists for modification
    if (currentSystemParts.isEmpty()) {
      currentSystemParts.add(Part.fromText(""));
    }
    // Modify the text of the first part
    String prefix = "[Modified by Callback] ";
    String conceptuallyModifiedText = prefix + currentSystemParts.get(0).text().orElse("");
    llmRequest =
        llmRequest.toBuilder()
            .config(
                GenerateContentConfig.builder()
                    .systemInstruction(
                        Content.builder()
                            .parts(List.of(Part.fromText(conceptuallyModifiedText)))
                            .build())
                    .build())
            .build();
    System.out.printf(
        "Modified System Instruction %s", llmRequest.config().get().systemInstruction());

    // --- Skip Example ---
    // Check if the last user message contains "BLOCK"
    if (lastUserMessage.toUpperCase().contains("BLOCK")) {
      System.out.println("[Callback] 'BLOCK' keyword found. Skipping LLM call.");
      // Return an LlmResponse to skip the actual LLM call
      return Maybe.just(
          LlmResponse.builder()
              .content(
                  Content.builder()
                      .role("model")
                      .parts(
                          ImmutableList.of(
                              Part.fromText("LLM call was blocked by before_model_callback.")))
                      .build())
              .build());
    }

    // Return Empty response to allow the (modified) request to go to the LLM
    System.out.println("[Callback] Proceeding with LLM call (using the original LlmRequest).");
    return Maybe.empty();
  }

  // --- 2. Define Agent and Run Scenarios ---
  public void defineAgentAndRun() {
    // Setup Agent with Callback
    LlmAgent myLlmAgent =
        LlmAgent.builder()
            .name(AGENT_NAME)
            .model(MODEL_NAME)
            .instruction(AGENT_INSTRUCTION)
            .description(AGENT_DESCRIPTION)
            .beforeModelCallback(this::simpleBeforeModelModifier)
            .build();

    // Create an InMemoryRunner
    InMemoryRunner runner = new InMemoryRunner(myLlmAgent, APP_NAME);
    // InMemoryRunner automatically creates a session service. Create a session using the service
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();
    Content userMessage =
        Content.fromParts(
            Part.fromText("Tell me about quantum computing. This is a test. So BLOCK."));

    // Run the agent
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    // Stream event response
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
```

### After Model Callback

**When:** Called just after a response (`LlmResponse`) is received from the LLM, before it's processed further by the invoking agent.

**Purpose:** Allows inspection or modification of the raw LLM response. Use cases include

- logging model outputs,
- reformatting responses,
- censoring sensitive information generated by the model,
- parsing structured data from the LLM response and storing it in `callback_context.state`
- or handling specific error codes.

Code

```python
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import Runner
from typing import Optional
from google.genai import types 
from google.adk.sessions import InMemorySessionService
from google.adk.models import LlmResponse
from copy import deepcopy

GEMINI_2_FLASH="gemini-2.0-flash"

# --- Define the Callback Function ---
def simple_after_model_modifier(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM response after it's received."""
    agent_name = callback_context.agent_name
    print(f"[Callback] After model call for agent: {agent_name}")

    # --- Inspection ---
    original_text = ""
    if llm_response.content and llm_response.content.parts:
        # Assuming simple text response for this example
        if llm_response.content.parts[0].text:
            original_text = llm_response.content.parts[0].text
            print(f"[Callback] Inspected original response text: '{original_text[:100]}...'") # Log snippet
        elif llm_response.content.parts[0].function_call:
             print(f"[Callback] Inspected response: Contains function call '{llm_response.content.parts[0].function_call.name}'. No text modification.")
             return None # Don't modify tool calls in this example
        else:
             print("[Callback] Inspected response: No text content found.")
             return None
    elif llm_response.error_message:
        print(f"[Callback] Inspected response: Contains error '{llm_response.error_message}'. No modification.")
        return None
    else:
        print("[Callback] Inspected response: Empty LlmResponse.")
        return None # Nothing to modify

    # --- Modification Example ---
    # Replace "joke" with "funny story" (case-insensitive)
    search_term = "joke"
    replace_term = "funny story"
    if search_term in original_text.lower():
        print(f"[Callback] Found '{search_term}'. Modifying response.")
        modified_text = original_text.replace(search_term, replace_term)
        modified_text = modified_text.replace(search_term.capitalize(), replace_term.capitalize()) # Handle capitalization

        # Create a NEW LlmResponse with the modified content
        # Deep copy parts to avoid modifying original if other callbacks exist
        modified_parts = [deepcopy(part) for part in llm_response.content.parts]
        modified_parts[0].text = modified_text # Update the text in the copied part

        new_response = LlmResponse(
             content=types.Content(role="model", parts=modified_parts),
             # Copy other relevant fields if necessary, e.g., grounding_metadata
             grounding_metadata=llm_response.grounding_metadata
             )
        print(f"[Callback] Returning modified response.")
        return new_response # Return the modified response
    else:
        print(f"[Callback] '{search_term}' not found. Passing original response through.")
        # Return None to use the original llm_response
        return None


# Create LlmAgent and Assign Callback
my_llm_agent = LlmAgent(
        name="AfterModelCallbackAgent",
        model=GEMINI_2_FLASH,
        instruction="You are a helpful assistant.",
        description="An LLM agent demonstrating after_model_callback",
        after_model_callback=simple_after_model_modifier # Assign the function here
)

APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

# Agent Interaction
async def call_agent_async(query):
  session, runner = await setup_session_and_runner()

  content = types.Content(role='user', parts=[types.Part(text=query)])
  events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

  async for event in events:
      if event.is_final_response():
          final_response = event.content.parts[0].text
          print("Agent Response: ", final_response)

# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("""write multiple time the word "joke" """)
```

```typescript
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
```

```go
package main

import (
    "context"
    "fmt"
    "log"
    "regexp"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)



func onAfterModel(ctx agent.CallbackContext, resp *model.LLMResponse, respErr error) (*model.LLMResponse, error) {
    log.Printf("[Callback] AfterModel triggered for agent %q.", ctx.AgentName())
    if respErr != nil {
        log.Printf("[Callback] Model returned an error: %v. Passing it through.", respErr)
        return nil, respErr
    }
    if resp == nil || resp.Content == nil || len(resp.Content.Parts) == 0 {
        log.Println("[Callback] Response is nil or has no parts, nothing to process.")
        return nil, nil
    }
    // Check for function calls and pass them through without modification.
    if resp.Content.Parts[0].FunctionCall != nil {
        log.Println("[Callback] Response is a function call. No modification.")
        return nil, nil
    }

    originalText := resp.Content.Parts[0].Text

    // Use a case-insensitive regex with word boundaries to find "joke".
    re := regexp.MustCompile(`(?i)\bjoke\b`)
    if !re.MatchString(originalText) {
        log.Println("[Callback] 'joke' not found. Passing original response through.")
        return nil, nil
    }

    log.Println("[Callback] 'joke' found. Modifying response.")
    // Use a replacer function to handle capitalization.
    modifiedText := re.ReplaceAllStringFunc(originalText, func(s string) string {
        if strings.ToUpper(s) == "JOKE" {
            if s == "Joke" {
                return "Funny story"
            }
            return "funny story"
        }
        return s // Should not be reached with this regex, but it's safe.
    })

    resp.Content.Parts[0].Text = modifiedText
    return resp, nil
}

func runAfterModelExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("FATAL: Failed to create model: %v", err)
    }

    llmCfg := llmagent.Config{
        Name:                "AgentWithAfterModelCallback",
        Model:               geminiModel,
        AfterModelCallbacks: []llmagent.AfterModelCallback{onAfterModel},
    }
    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("FATAL: Failed to create agent: %v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
    if err != nil {
        log.Fatalf("FATAL: Failed to create runner: %v", err)
    }

    log.Println("--- SCENARIO 1: Response should be modified ---")
    runScenario(ctx, r, sessionService, appName, "session_modify", nil, `Give me a paragraph about different styles of jokes.`)
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.CallbackContext;
import com.google.adk.events.Event;
import com.google.adk.models.LlmResponse;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class AfterModelCallbackExample {

  // --- Define Constants ---
  private static final String AGENT_NAME = "AfterModelCallbackAgent";
  private static final String MODEL_NAME = "gemini-2.0-flash";
  private static final String AGENT_INSTRUCTION = "You are a helpful assistant.";
  private static final String AGENT_DESCRIPTION = "An LLM agent demonstrating after_model_callback";

  // For session and runner
  private static final String APP_NAME = "AfterModelCallbackAgentApp";
  private static final String USER_ID = "user_1";

  // For text replacement
  private static final String SEARCH_TERM = "joke";
  private static final String REPLACE_TERM = "funny story";
  private static final Pattern SEARCH_PATTERN =
      Pattern.compile("\\b" + Pattern.quote(SEARCH_TERM) + "\\b", Pattern.CASE_INSENSITIVE);

  public static void main(String[] args) {
    AfterModelCallbackExample example = new AfterModelCallbackExample();
    example.defineAgentAndRun();
  }

  // --- Define the Callback Function ---
  // Inspects/modifies the LLM response after it's received.
  public Maybe<LlmResponse> simpleAfterModelModifier(
      CallbackContext callbackContext, LlmResponse llmResponse) {
    String agentName = callbackContext.agentName();
    System.out.printf("%n[Callback] After model call for agent: %s%n", agentName);

    // --- Inspection Phase ---
    if (llmResponse.errorMessage().isPresent()) {
      System.out.printf(
          "[Callback] Response has error: '%s'. No modification.%n",
          llmResponse.errorMessage().get());
      return Maybe.empty(); // Pass through errors
    }

    Optional<Part> firstTextPartOpt =
        llmResponse
            .content()
            .flatMap(Content::parts)
            .filter(parts -> !parts.isEmpty() && parts.get(0).text().isPresent())
            .map(parts -> parts.get(0));

    if (!firstTextPartOpt.isPresent()) {
      // Could be a function call, empty content, or no text in the first part
      llmResponse
          .content()
          .flatMap(Content::parts)
          .filter(parts -> !parts.isEmpty() && parts.get(0).functionCall().isPresent())
          .ifPresent(
              parts ->
                  System.out.printf(
                      "[Callback] Response is a function call ('%s'). No text modification.%n",
                      parts.get(0).functionCall().get().name().orElse("N/A")));
      if (!llmResponse.content().isPresent()
          || !llmResponse.content().flatMap(Content::parts).isPresent()
          || llmResponse.content().flatMap(Content::parts).get().isEmpty()) {
        System.out.println(
            "[Callback] Response content is empty or has no parts. No modification.");
      } else if (!firstTextPartOpt.isPresent()) { // Already checked for function call
        System.out.println("[Callback] First part has no text content. No modification.");
      }
      return Maybe.empty(); // Pass through non-text or unsuitable responses
    }

    String originalText = firstTextPartOpt.get().text().get();
    System.out.printf("[Callback] Inspected original text: '%.100s...'%n", originalText);

    // --- Modification Phase ---
    Matcher matcher = SEARCH_PATTERN.matcher(originalText);
    if (!matcher.find()) {
      System.out.printf(
          "[Callback] '%s' not found. Passing original response through.%n", SEARCH_TERM);
      return Maybe.empty();
    }

    System.out.printf("[Callback] Found '%s'. Modifying response.%n", SEARCH_TERM);

    // Perform the replacement, respecting original capitalization of the found term's first letter
    String foundTerm = matcher.group(0); // The actual term found (e.g., "joke" or "Joke")
    String actualReplaceTerm = REPLACE_TERM;
    if (Character.isUpperCase(foundTerm.charAt(0)) && REPLACE_TERM.length() > 0) {
      actualReplaceTerm = Character.toUpperCase(REPLACE_TERM.charAt(0)) + REPLACE_TERM.substring(1);
    }
    String modifiedText = matcher.replaceFirst(Matcher.quoteReplacement(actualReplaceTerm));

    // Create a new LlmResponse with the modified content
    Content originalContent = llmResponse.content().get();
    List<Part> originalParts = originalContent.parts().orElse(ImmutableList.of());

    List<Part> modifiedPartsList = new ArrayList<>(originalParts.size());
    if (!originalParts.isEmpty()) {
      modifiedPartsList.add(Part.fromText(modifiedText)); // Replace first part's text
      // Add remaining parts as they were (shallow copy)
      for (int i = 1; i < originalParts.size(); i++) {
        modifiedPartsList.add(originalParts.get(i));
      }
    } else { // Should not happen if firstTextPartOpt was present
      modifiedPartsList.add(Part.fromText(modifiedText));
    }

    LlmResponse.Builder newResponseBuilder =
        LlmResponse.builder()
            .content(
                originalContent.toBuilder().parts(ImmutableList.copyOf(modifiedPartsList)).build())
            .groundingMetadata(llmResponse.groundingMetadata());

    System.out.println("[Callback] Returning modified response.");
    return Maybe.just(newResponseBuilder.build());
  }

  // --- 2. Define Agent and Run Scenarios ---
  public void defineAgentAndRun() {
    // Setup Agent with Callback
    LlmAgent myLlmAgent =
        LlmAgent.builder()
            .name(AGENT_NAME)
            .model(MODEL_NAME)
            .instruction(AGENT_INSTRUCTION)
            .description(AGENT_DESCRIPTION)
            .afterModelCallback(this::simpleAfterModelModifier)
            .build();

    // Create an InMemoryRunner
    InMemoryRunner runner = new InMemoryRunner(myLlmAgent, APP_NAME);
    // InMemoryRunner automatically creates a session service. Create a session using the service
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();
    Content userMessage =
        Content.fromParts(
            Part.fromText(
                "Tell me a joke about quantum computing. Include the word 'joke' in your response"));

    // Run the agent
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    // Stream event response
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
```

## Tool Execution Callbacks

These callbacks are also specific to `LlmAgent` and trigger around the execution of tools (including `FunctionTool`, `AgentTool`, etc.) that the LLM might request.

### Before Tool Callback

**When:** Called just before a specific tool's `run_async` method is invoked, after the LLM has generated a function call for it.

**Purpose:** Allows inspection and modification of tool arguments, performing authorization checks before execution, logging tool usage attempts, or implementing tool-level caching.

**Return Value Effect:**

1. If the callback returns `None` (or a `Maybe.empty()` object in Java), the tool's `run_async` method is executed with the (potentially modified) `args`.
1. If a dictionary (or `Map` in Java) is returned, the tool's `run_async` method is **skipped**. The returned dictionary is used directly as the result of the tool call. This is useful for caching or overriding tool behavior.

Code

```python
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from typing import Optional
from google.genai import types 
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any


GEMINI_2_FLASH="gemini-2.0-flash"

def get_capital_city(country: str) -> str:
    """Retrieves the capital city of a given country."""
    print(f"--- Tool 'get_capital_city' executing with country: {country} ---")
    country_capitals = {
        "united states": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "germany": "Berlin",
    }
    return country_capitals.get(country.lower(), f"Capital not found for {country}")

capital_tool = FunctionTool(func=get_capital_city)

def simple_before_tool_modifier(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """Inspects/modifies tool args or skips the tool call."""
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[Callback] Before tool call for tool '{tool_name}' in agent '{agent_name}'")
    print(f"[Callback] Original args: {args}")

    if tool_name == 'get_capital_city' and args.get('country', '').lower() == 'canada':
        print("[Callback] Detected 'Canada'. Modifying args to 'France'.")
        args['country'] = 'France'
        print(f"[Callback] Modified args: {args}")
        return None

    # If the tool is 'get_capital_city' and country is 'BLOCK'
    if tool_name == 'get_capital_city' and args.get('country', '').upper() == 'BLOCK':
        print("[Callback] Detected 'BLOCK'. Skipping tool execution.")
        return {"result": "Tool execution was blocked by before_tool_callback."}

    print("[Callback] Proceeding with original or previously modified args.")
    return None

my_llm_agent = LlmAgent(
        name="ToolCallbackAgent",
        model=GEMINI_2_FLASH,
        instruction="You are an agent that can find capital cities. Use the get_capital_city tool.",
        description="An LLM agent demonstrating before_tool_callback",
        tools=[capital_tool],
        before_tool_callback=simple_before_tool_modifier
)

APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("Canada")
```

```typescript
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
  ToolContext,
  isFinalResponse,
  BaseTool,
} from '@google/adk';
import { createUserContent } from "@google/genai";
import { z } from 'zod';

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "before_tool_callback_app";
const USER_ID = "test_user_before_tool";

// --- Define a Simple Tool Function ---
const CountryInput = z.object({
  country: z.string().describe('The country to get the capital for.'),
});

async function getCapitalCity(params: z.infer<typeof CountryInput>): Promise<{ result: string }> {
    console.log(`\n-- Tool Call: getCapitalCity(country='${params.country}') --`);
    const capitals: Record<string, string> = {
        'united states': 'Washington, D.C.',
        'canada': 'Ottawa',
        'france': 'Paris',
        'japan': 'Tokyo',
    };
    const result = capitals[params.country.toLowerCase()] ??
        `Sorry, I couldn't find the capital for ${params.country}.`;
    console.log(`-- Tool Result: '${result}' --`);
    return { result };
}

const getCapitalCityTool = new FunctionTool({
    name: 'get_capital_city',
    description: 'Retrieves the capital city for a given country',
    parameters: CountryInput,
    execute: getCapitalCity,
});

// --- Define the Callback Function ---
function simpleBeforeToolModifier({
  tool,
  args,
  context,
}: {
  tool: BaseTool;
  args: Record<string, any>;
  context: ToolContext;
}) {
  const agentName = context.agentName;
  const toolName = tool.name;
  console.log(`[Callback] Before tool call for tool '${toolName}' in agent '${agentName}'`);
  console.log(`[Callback] Original args: ${JSON.stringify(args)}`);

  if (
    toolName === "get_capital_city" &&
    args["country"]?.toLowerCase() === "canada"
  ) {
    console.log("[Callback] Detected 'Canada'. Modifying args to 'France'.");
    args["country"] = "France";
    console.log(`[Callback] Modified args: ${JSON.stringify(args)}`);
    return undefined;
  }

  if (
    toolName === "get_capital_city" &&
    args["country"]?.toUpperCase() === "BLOCK"
  ) {
    console.log("[Callback] Detected 'BLOCK'. Skipping tool execution.");
    return { result: "Tool execution was blocked by before_tool_callback." };
  }

  console.log("[Callback] Proceeding with original or previously modified args.");
  return;
}

// Create LlmAgent and Assign Callback
const myLlmAgent = new LlmAgent({
  name: 'ToolCallbackAgent',
  model: MODEL_NAME,
  instruction: 'You are an agent that can find capital cities. Use the get_capital_city tool.',
  description: 'An LLM agent demonstrating before_tool_callback',
  tools: [getCapitalCityTool],
  beforeToolCallback: simpleBeforeToolModifier,
});

// Agent Interaction Logic
async function callAgentAndPrint(runner: InMemoryRunner, query: string, sessionId: string) {
  console.log(`\n>>> Calling Agent for session '${sessionId}' | Query: "${query}"`);

  for await (const event of runner.runAsync({ userId: USER_ID, sessionId, newMessage: createUserContent(query) })) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const finalResponseContent = event.content.parts.map(part => part.text ?? '').join('');
      console.log(`<<< Final Output: ${finalResponseContent}`);
    }
  }
}

// Run Interactions
async function main() {
  const runner = new InMemoryRunner({ agent: myLlmAgent, appName: APP_NAME });

  // Scenario 1: Callback modifies the arguments from "Canada" to "France"
  const canadaSessionId = 'session_canada_test';
  await runner.sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: canadaSessionId });
  await callAgentAndPrint(runner, 'What is the capital of Canada?', canadaSessionId);

  // Scenario 2: Callback skips the tool call
  const blockSessionId = 'session_block_test';
  await runner.sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: blockSessionId });
  await callAgentAndPrint(runner, 'What is the capital of BLOCK?', blockSessionId);
}

main();
```

```go
package main

import (
    "context"
    "fmt"
    "log"
    "regexp"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)

// GetCapitalCityArgs defines the arguments for the getCapitalCity tool.
type GetCapitalCityArgs struct {
    Country string `json:"country" jsonschema:"The country to get the capital of."`
}

// getCapitalCity is a tool that returns the capital of a given country.
func getCapitalCity(ctx tool.Context, args *GetCapitalCityArgs) (string, error) {
    capitals := map[string]string{
        "canada":        "Ottawa",
        "france":        "Paris",
        "germany":       "Berlin",
        "united states": "Washington, D.C.",
    }
    capital, ok := capitals[strings.ToLower(args.Country)]
    if !ok {
        return "", fmt.Errorf("unknown country: %s", args.Country)
    }
    return capital, nil
}

func onBeforeTool(ctx tool.Context, t tool.Tool, args map[string]any) (map[string]any, error) {
    log.Printf("[Callback] BeforeTool triggered for tool %q in agent %q.", t.Name(), ctx.AgentName())
    log.Printf("[Callback] Original args: %v", args)

    if t.Name() == "getCapitalCity" {
        if country, ok := args["country"].(string); ok {
            if strings.ToLower(country) == "canada" {
                log.Println("[Callback] Detected 'Canada'. Modifying args to 'France'.")
                args["country"] = "France"
                return args, nil // Proceed with modified args
            } else if strings.ToUpper(country) == "BLOCK" {
                log.Println("[Callback] Detected 'BLOCK'. Skipping tool execution.")
                // Skip tool and return a custom result.
                return map[string]any{"result": "Tool execution was blocked by before_tool_callback."}, nil
            }
        }
    }
    log.Println("[Callback] Proceeding with original or previously modified args.")
    return nil, nil // Proceed with original args
}

func runBeforeToolExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("FATAL: Failed to create model: %v", err)
    }
    capitalTool, err := functiontool.New(functiontool.Config{
        Name:        "getCapitalCity",
        Description: "Retrieves the capital city of a given country.",
    }, getCapitalCity)
    if err != nil {
        log.Fatalf("FATAL: Failed to create function tool: %v", err)
    }

    llmCfg := llmagent.Config{
        Name:                "AgentWithBeforeToolCallback",
        Model:               geminiModel,
        Tools:               []tool.Tool{capitalTool},
        BeforeToolCallbacks: []llmagent.BeforeToolCallback{onBeforeTool},
        Instruction:         "You are an agent that can find capital cities. Use the getCapitalCity tool.",
    }
    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("FATAL: Failed to create agent: %v", err)
    }
    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
    if err != nil {
        log.Fatalf("FATAL: Failed to create runner: %v", err)
    }

    log.Println("--- SCENARIO 1: Args should be modified ---")
    runScenario(ctx, r, sessionService, appName, "session_tool_modify", nil, "What is the capital of Canada?")

    log.Println("--- SCENARIO 2: Tool call should be blocked ---")
    runScenario(ctx, r, sessionService, appName, "session_tool_block", nil, "capital of BLOCK")
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.InvocationContext;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.BaseTool;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;
import com.google.common.collect.ImmutableMap;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.HashMap;
import java.util.Map;

public class BeforeToolCallbackExample {

  private static final String APP_NAME = "ToolCallbackAgentApp";
  private static final String USER_ID = "user_1";
  private static final String SESSION_ID = "session_001";
  private static final String MODEL_NAME = "gemini-2.0-flash";

  public static void main(String[] args) {
    BeforeToolCallbackExample example = new BeforeToolCallbackExample();
    example.runAgent("capital of canada");
  }

  // --- Define a Simple Tool Function ---
  // The Schema is important for the callback "args" to correctly identify the input.
  public static Map<String, Object> getCapitalCity(
      @Schema(name = "country", description = "The country to find the capital of.")
          String country) {
    System.out.printf("--- Tool 'getCapitalCity' executing with country: %s ---%n", country);
    Map<String, String> countryCapitals = new HashMap<>();
    countryCapitals.put("united states", "Washington, D.C.");
    countryCapitals.put("canada", "Ottawa");
    countryCapitals.put("france", "Paris");
    countryCapitals.put("germany", "Berlin");

    String capital =
        countryCapitals.getOrDefault(country.toLowerCase(), "Capital not found for " + country);
    // FunctionTool expects a Map<String, Object> as the return type for the method it wraps.
    return ImmutableMap.of("capital", capital);
  }

  // Define the Callback function
  // The Tool callback provides all these parameters by default.
  public Maybe<Map<String, Object>> simpleBeforeToolModifier(
      InvocationContext invocationContext,
      BaseTool tool,
      Map<String, Object> args,
      ToolContext toolContext) {

    String agentName = invocationContext.agent().name();
    String toolName = tool.name();
    System.out.printf(
        "[Callback] Before tool call for tool '%s' in agent '%s'%n", toolName, agentName);
    System.out.printf("[Callback] Original args: %s%n", args);

    if ("getCapitalCity".equals(toolName)) {
      String countryArg = (String) args.get("country");
      if (countryArg != null) {
        if ("canada".equalsIgnoreCase(countryArg)) {
          System.out.println("[Callback] Detected 'Canada'. Modifying args to 'France'.");
          args.put("country", "France");
          System.out.printf("[Callback] Modified args: %s%n", args);
          // Proceed with modified args
          return Maybe.empty();
        } else if ("BLOCK".equalsIgnoreCase(countryArg)) {
          System.out.println("[Callback] Detected 'BLOCK'. Skipping tool execution.");
          // Return a map to skip the tool call and use this as the result
          return Maybe.just(
              ImmutableMap.of("result", "Tool execution was blocked by before_tool_callback."));
        }
      }
    }

    System.out.println("[Callback] Proceeding with original or previously modified args.");
    return Maybe.empty();
  }

  public void runAgent(String query) {
    // --- Wrap the function into a Tool ---
    FunctionTool capitalTool = FunctionTool.create(this.getClass(), "getCapitalCity");

    // Create LlmAgent and Assign Callback
    LlmAgent myLlmAgent =
        LlmAgent.builder()
            .name(APP_NAME)
            .model(MODEL_NAME)
            .instruction(
                "You are an agent that can find capital cities. Use the getCapitalCity tool.")
            .description("An LLM agent demonstrating before_tool_callback")
            .tools(capitalTool)
            .beforeToolCallback(this::simpleBeforeToolModifier)
            .build();

    // Session and Runner
    InMemoryRunner runner = new InMemoryRunner(myLlmAgent);
    Session session =
        runner.sessionService().createSession(APP_NAME, USER_ID, null, SESSION_ID).blockingGet();

    Content userMessage = Content.fromParts(Part.fromText(query));

    System.out.printf("%n--- Calling agent with query: \"%s\" ---%n", query);
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);
    // Stream event response
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
```

### After Tool Callback

**When:** Called just after the tool's `run_async` method completes successfully.

**Purpose:** Allows inspection and modification of the tool's result before it's sent back to the LLM (potentially after summarization). Useful for logging tool results, post-processing or formatting results, or saving specific parts of the result to the session state.

**Return Value Effect:**

1. If the callback returns `None` (or a `Maybe.empty()` object in Java), the original `tool_response` is used.
1. If a new dictionary is returned, it **replaces** the original `tool_response`. This allows modifying or filtering the result seen by the LLM.

Code

```python
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from typing import Optional
from google.genai import types 
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any
from copy import deepcopy

GEMINI_2_FLASH="gemini-2.0-flash"

# --- Define a Simple Tool Function (Same as before) ---
def get_capital_city(country: str) -> str:
    """Retrieves the capital city of a given country."""
    print(f"--- Tool 'get_capital_city' executing with country: {country} ---")
    country_capitals = {
        "united states": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "germany": "Berlin",
    }
    return {"result": country_capitals.get(country.lower(), f"Capital not found for {country}")}

# --- Wrap the function into a Tool ---
capital_tool = FunctionTool(func=get_capital_city)

# --- Define the Callback Function ---
def simple_after_tool_modifier(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """Inspects/modifies the tool result after execution."""
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[Callback] After tool call for tool '{tool_name}' in agent '{agent_name}'")
    print(f"[Callback] Args used: {args}")
    print(f"[Callback] Original tool_response: {tool_response}")

    # Default structure for function tool results is {"result": <return_value>}
    original_result_value = tool_response.get("result", "")
    # original_result_value = tool_response

    # --- Modification Example ---
    # If the tool was 'get_capital_city' and result is 'Washington, D.C.'
    if tool_name == 'get_capital_city' and original_result_value == "Washington, D.C.":
        print("[Callback] Detected 'Washington, D.C.'. Modifying tool response.")

        # IMPORTANT: Create a new dictionary or modify a copy
        modified_response = deepcopy(tool_response)
        modified_response["result"] = f"{original_result_value} (Note: This is the capital of the USA)."
        modified_response["note_added_by_callback"] = True # Add extra info if needed

        print(f"[Callback] Modified tool_response: {modified_response}")
        return modified_response # Return the modified dictionary

    print("[Callback] Passing original tool response through.")
    # Return None to use the original tool_response
    return None


# Create LlmAgent and Assign Callback
my_llm_agent = LlmAgent(
        name="AfterToolCallbackAgent",
        model=GEMINI_2_FLASH,
        instruction="You are an agent that finds capital cities using the get_capital_city tool. Report the result clearly.",
        description="An LLM agent demonstrating after_tool_callback",
        tools=[capital_tool], # Add the tool
        after_tool_callback=simple_after_tool_modifier # Assign the callback
    )

APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
await call_agent_async("united states")
```

```typescript
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
```

```go
package main

import (
    "context"
    "fmt"
    "log"
    "regexp"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)

// GetCapitalCityArgs defines the arguments for the getCapitalCity tool.
type GetCapitalCityArgs struct {
    Country string `json:"country" jsonschema:"The country to get the capital of."`
}

// getCapitalCity is a tool that returns the capital of a given country.
func getCapitalCity(ctx tool.Context, args *GetCapitalCityArgs) (string, error) {
    capitals := map[string]string{
        "canada":        "Ottawa",
        "france":        "Paris",
        "germany":       "Berlin",
        "united states": "Washington, D.C.",
    }
    capital, ok := capitals[strings.ToLower(args.Country)]
    if !ok {
        return "", fmt.Errorf("unknown country: %s", args.Country)
    }
    return capital, nil
}

func onAfterTool(ctx tool.Context, t tool.Tool, args map[string]any, result map[string]any, err error) (map[string]any, error) {
    log.Printf("[Callback] AfterTool triggered for tool %q in agent %q.", t.Name(), ctx.AgentName())
    log.Printf("[Callback] Original result: %v", result)

    if err != nil {
        log.Printf("[Callback] Tool run produced an error: %v. Passing through.", err)
        return nil, err
    }

    if t.Name() == "getCapitalCity" {
        if originalResult, ok := result["result"].(string); ok && originalResult == "Washington, D.C." {
            log.Println("[Callback] Detected 'Washington, D.C.'. Modifying tool response.")
            modifiedResult := make(map[string]any)
            for k, v := range result {
                modifiedResult[k] = v
            }
            modifiedResult["result"] = fmt.Sprintf("%s (Note: This is the capital of the USA).", originalResult)
            modifiedResult["note_added_by_callback"] = true
            return modifiedResult, nil
        }
    }

    log.Println("[Callback] Passing original tool response through.")
    return nil, nil
}

func runAfterToolExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("FATAL: Failed to create model: %v", err)
    }
    capitalTool, err := functiontool.New(functiontool.Config{
        Name:        "getCapitalCity",
        Description: "Retrieves the capital city of a given country.",
    }, getCapitalCity)
    if err != nil {
        log.Fatalf("FATAL: Failed to create function tool: %v", err)
    }

    llmCfg := llmagent.Config{
        Name:               "AgentWithAfterToolCallback",
        Model:              geminiModel,
        Tools:              []tool.Tool{capitalTool},
        AfterToolCallbacks: []llmagent.AfterToolCallback{onAfterTool},
        Instruction:        "You are an agent that finds capital cities. Use the getCapitalCity tool.",
    }
    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("FATAL: Failed to create agent: %v", err)
    }
    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
    if err != nil {
        log.Fatalf("FATAL: Failed to create runner: %v", err)
    }

    log.Println("--- SCENARIO 1: Result should be modified ---")
    runScenario(ctx, r, sessionService, appName, "session_tool_after_modify", nil, "capital of united states")
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.InvocationContext;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.BaseTool;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;
import com.google.common.collect.ImmutableMap;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.HashMap;
import java.util.Map;

public class AfterToolCallbackExample {

  private static final String APP_NAME = "AfterToolCallbackAgentApp";
  private static final String USER_ID = "user_1";
  private static final String SESSION_ID = "session_001";
  private static final String MODEL_NAME = "gemini-2.0-flash";

  public static void main(String[] args) {
    AfterToolCallbackExample example = new AfterToolCallbackExample();
    example.runAgent("What is the capital of the United States?");
  }

  // --- Define a Simple Tool Function (Same as before) ---
  @Schema(description = "Retrieves the capital city of a given country.")
  public static Map<String, Object> getCapitalCity(
      @Schema(description = "The country to find the capital of.") String country) {
    System.out.printf("--- Tool 'getCapitalCity' executing with country: %s ---%n", country);
    Map<String, String> countryCapitals = new HashMap<>();
    countryCapitals.put("united states", "Washington, D.C.");
    countryCapitals.put("canada", "Ottawa");
    countryCapitals.put("france", "Paris");
    countryCapitals.put("germany", "Berlin");

    String capital =
        countryCapitals.getOrDefault(country.toLowerCase(), "Capital not found for " + country);
    return ImmutableMap.of("result", capital);
  }

  // Define the Callback function.
  public Maybe<Map<String, Object>> simpleAfterToolModifier(
      InvocationContext invocationContext,
      BaseTool tool,
      Map<String, Object> args,
      ToolContext toolContext,
      Object toolResponse) {

    // Inspects/modifies the tool result after execution.
    String agentName = invocationContext.agent().name();
    String toolName = tool.name();
    System.out.printf(
        "[Callback] After tool call for tool '%s' in agent '%s'%n", toolName, agentName);
    System.out.printf("[Callback] Args used: %s%n", args);
    System.out.printf("[Callback] Original tool_response: %s%n", toolResponse);

    if (!(toolResponse instanceof Map)) {
      System.out.println("[Callback] toolResponse is not a Map, cannot process further.");
      // Pass through if not a map
      return Maybe.empty();
    }

    // Default structure for function tool results is {"result": <return_value>}
    @SuppressWarnings("unchecked")
    Map<String, Object> responseMap = (Map<String, Object>) toolResponse;
    Object originalResultValue = responseMap.get("result");

    // --- Modification Example ---
    // If the tool was 'get_capital_city' and result is 'Washington, D.C.'
    if ("getCapitalCity".equals(toolName) && "Washington, D.C.".equals(originalResultValue)) {
      System.out.println("[Callback] Detected 'Washington, D.C.'. Modifying tool response.");

      // IMPORTANT: Create a new mutable map or modify a copy
      Map<String, Object> modifiedResponse = new HashMap<>(responseMap);
      modifiedResponse.put(
          "result", originalResultValue + " (Note: This is the capital of the USA).");
      modifiedResponse.put("note_added_by_callback", true); // Add extra info if needed

      System.out.printf("[Callback] Modified tool_response: %s%n", modifiedResponse);
      return Maybe.just(modifiedResponse);
    }

    System.out.println("[Callback] Passing original tool response through.");
    // Return Maybe.empty() to use the original tool_response
    return Maybe.empty();
  }

  public void runAgent(String query) {
    // --- Wrap the function into a Tool ---
    FunctionTool capitalTool = FunctionTool.create(this.getClass(), "getCapitalCity");

    // Create LlmAgent and Assign Callback
    LlmAgent myLlmAgent =
        LlmAgent.builder()
            .name(APP_NAME)
            .model(MODEL_NAME)
            .instruction(
                "You are an agent that finds capital cities using the getCapitalCity tool. Report"
                    + " the result clearly.")
            .description("An LLM agent demonstrating after_tool_callback")
            .tools(capitalTool) // Add the tool
            .afterToolCallback(this::simpleAfterToolModifier) // Assign the callback
            .build();

    InMemoryRunner runner = new InMemoryRunner(myLlmAgent);

    // Session and Runner
    Session session =
        runner.sessionService().createSession(APP_NAME, USER_ID, null, SESSION_ID).blockingGet();

    Content userMessage = Content.fromParts(Part.fromText(query));

    System.out.printf("%n--- Calling agent with query: \"%s\" ---%n", query);
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);
    // Stream event response
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
```
