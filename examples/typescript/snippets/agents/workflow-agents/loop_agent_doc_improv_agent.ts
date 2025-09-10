// Copyright 2025 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// --8<-- [start:init]
// Part of agent.ts --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup

import { LoopAgent, LlmAgent, SequentialAgent, InMemoryRunner, FunctionTool, ToolContext } from '@google/adk';
import { Content } from '@google/genai';
import { z } from 'zod';

// --- Constants ---
const APP_NAME = "doc_writing_app_v3"; // New App Name
const USER_ID = "dev_user_01";
const SESSION_ID_BASE = "loop_exit_tool_session"; // New Base Session ID
const GEMINI_MODEL = "gemini-2.0-flash";
const STATE_INITIAL_TOPIC = "initial_topic";

// --- State Keys ---
const STATE_CURRENT_DOC = "current_document";
const STATE_CRITICISM = "criticism";
// Define the exact phrase the Critic should use to signal completion
const COMPLETION_PHRASE = "No major issues found.";

// --- Tool Definition ---
function exitLoop(toolContext: ToolContext): Record<string, unknown> {
  /** Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end. */
  console.log(`  [Tool Call] exit_loop triggered by ${toolContext.agentName}`);
  toolContext.actions.escalate = true;
  // Return empty object as tools should typically return JSON-serializable output
  return {};
}

const exitLoopTool = new FunctionTool({
    name: 'exit_loop',
    description: 'Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end.',
    parameters: z.object({}),
    execute: exitLoop,
});

// --- Agent Definitions ---

// STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
const initialWriterAgent = new LlmAgent({
    name: "InitialWriterAgent",
    model: GEMINI_MODEL,
    includeContents: 'none',
    // MODIFIED Instruction: Ask for a slightly more developed start
    instruction: `You are a Creative Writing Assistant tasked with starting a story.
    Write the *first draft* of a short story (aim for 2-4 sentences).
    Base the content *only* on the topic provided below. Try to introduce a specific element (like a character, a setting detail, or a starting action) to make it engaging.
    Topic: {{initial_topic}}

    Output *only* the story/document text. Do not add introductions or explanations.
`,
    description: "Writes the initial document draft based on the topic, aiming for some initial substance.",
    outputKey: STATE_CURRENT_DOC
});

// STEP 2a: Critic Agent (Inside the Refinement Loop)
const criticAgentInLoop = new LlmAgent({
    name: "CriticAgent",
    model: GEMINI_MODEL,
    includeContents: 'none',
    // MODIFIED Instruction: More nuanced completion criteria, look for clear improvement paths.
    instruction: `You are a Constructive Critic AI reviewing a short document draft (typically 2-6 sentences). Your goal is balanced feedback.

    **Document to Review:**
    ```
    {{current_document}}
    ```

    **Task:**
    Review the document for clarity, engagement, and basic coherence according to the initial topic (if known).

    IF you identify 1-2 *clear and actionable* ways the document could be improved to better capture the topic or enhance reader engagement (e.g., "Needs a stronger opening sentence", "Clarify the character's goal"):
    Provide these specific suggestions concisely. Output *only* the critique text.

    ELSE IF the document is coherent, addresses the topic adequately for its length, and has no glaring errors or obvious omissions:
    Respond *exactly* with the phrase "${COMPLETION_PHRASE}" and nothing else. It doesn't need to be perfect, just functionally complete for this stage. Avoid suggesting purely subjective stylistic preferences if the core is sound.

    Do not add explanations. Output only the critique OR the exact completion phrase.
`,
    description: "Reviews the current draft, providing critique if clear improvements are needed, otherwise signals completion.",
    outputKey: STATE_CRITICISM
});


// STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
const refinerAgentInLoop = new LlmAgent({
    name: "RefinerAgent",
    model: GEMINI_MODEL,
    // Relies solely on state via placeholders
    includeContents: 'none',
    instruction: `You are a Creative Writing Assistant refining a document based on feedback OR exiting the process.
    **Current Document:**
    ```
    {{current_document}}
    ```
    **Critique/Suggestions:**
    {{criticism}}

    **Task:**
    Analyze the 'Critique/Suggestions'.
    IF the critique is *exactly* "${COMPLETION_PHRASE}":
    You MUST call the 'exit_loop' function. Do not output any text.
    ELSE (the critique contains actionable feedback):
    Carefully apply the suggestions to improve the 'Current Document'. Output *only* the refined document text.

    Do not add explanations. Either output the refined document OR call the exit_loop function.
`,
    description: "Refines the document based on critique, or calls exit_loop if critique indicates completion.",
    tools: [exitLoopTool], // Provide the exit_loop tool
    outputKey: STATE_CURRENT_DOC // Overwrites state['current_document'] with the refined version
});


// STEP 2: Refinement Loop Agent
const refinementLoop = new LoopAgent({
    name: "RefinementLoop",
    // Agent order is crucial: Critique first, then Refine/Exit
    subAgents: [
        criticAgentInLoop,
        refinerAgentInLoop,
    ],
    maxIterations: 5 // Limit loops
});

// STEP 3: Overall Sequential Pipeline
// For ADK tools compatibility, the root agent must be named `root_agent`
const rootAgent = new SequentialAgent({
    name: "IterativeWritingPipeline",
    subAgents: [
        initialWriterAgent, // Run first to create initial doc
        refinementLoop       // Then run the critique/refine loop
    ],
    description: "Writes an initial document and then iteratively refines it with critique using an exit tool."
});
// --8<-- [end:init]


// --- Running the Agent on Notebooks/Scripts ---
// const runner = new InMemoryRunner({agent: rootAgent, appName: APP_NAME});
// console.log(`InMemoryRunner created for agent '${rootAgent.name}'.`);


// // Interaction function (Modified to show agent names and flow)
// async function callPipelineAsync(initialTopic: string, userId: string, sessionId: string) {
//     console.log(`
--- Starting Iterative Writing Pipeline (Exit Tool) for topic: '${initialTopic}' ---`);
//     const sessionService = runner.sessionService;
//     const initialState = {[STATE_INITIAL_TOPIC]: initialTopic};
//     // Explicitly create/check session BEFORE run
//     let session = await sessionService.getSession({appName: APP_NAME, userId, sessionId});
//     if (!session) {
//         console.log(`  Session '${sessionId}' not found, creating with initial state...`);
//         session = await sessionService.createSession({appName: APP_NAME, userId, sessionId, state: initialState});
//         console.log(`  Session '${sessionId}' created.`);
//     } else {
//         console.log(`  Session '${sessionId}' exists. Resetting state for new run.`);
//         // In a real app, you might have a more robust way to update state
//         session.state = initialState;
//         await sessionService.updateSession(session);
//     }

//     const initialMessage: Content = {role: 'user', parts: [{text: "Start the writing pipeline."}]};
//     let loopIteration = 0;
//     let pipelineFinishedViaExit = false;
//     let lastKnownDoc = "No document generated."; // Store the last document output

//     try {
//         for await (const event of runner.run({userId, sessionId, newMessage: initialMessage})) {
//             const authorName = event.author || "System";
//             const isFinal = event.isFinalResponse;
//             console.log(`  [Event] From: ${authorName}, Final: ${isFinal}`);

//             // Display output from each main agent when it finishes
//             if (isFinal && event.content && event.content.parts) {
//                 const outputText = event.content.parts[0].text!.trim();

//                 if (authorName === initialWriterAgent.name) {
//                     console.log(`
[Initial Draft] By ${authorName} (${STATE_CURRENT_DOC}):`);
//                     console.log(outputText);
//                     lastKnownDoc = outputText;
//                 } else if (authorName === criticAgentInLoop.name) {
//                     loopIteration++;
//                     console.log(`
[Loop Iteration ${loopIteration}] Critique by ${authorName} (${STATE_CRITICISM}):`);
//                     console.log(outputText);
//                     console.log(`  (Saving to state key '${STATE_CRITICISM}')`);
//                 } else if (authorName === refinerAgentInLoop.name) {
//                     // Only print if it actually refined (didn't call exit_loop)
//                     if (!event.actions?.escalate) { // Check if exit wasn't triggered in *this* event's actions
//                         console.log(`[Loop Iteration ${loopIteration}] Refinement by ${authorName} (${STATE_CURRENT_DOC}):`);
//                         console.log(outputText);
//                         lastKnownDoc = outputText;
//                         console.log(`  (Overwriting state key '${STATE_CURRENT_DOC}')`);
//                     }
//                 }
//             }

//             if (event.actions?.escalate) {
//                  console.log(`
--- Refinement Loop terminated (Escalation detected) ---`);
//                  pipelineFinishedViaExit = true;
//                  break;
//             } else if (event.errorMessage) {
//                  console.log(`  -> Error from ${authorName}: ${event.errorMessage}`);
//                  break; // Stop on error
//             }
//         }
//     } catch (e) {
//         console.log(`
❌ An error occurred during agent execution: ${e}`);
//     }

//     if (pipelineFinishedViaExit) {
//         console.log(`
--- Pipeline Finished (Terminated by exit_loop) ---`);
//     } else {
//         console.log(`
--- Pipeline Finished (Max iterations ${refinementLoop.maxIterations} reached or error) ---`);
//     }

//     console.log(`Final Document Output:
${lastKnownDoc}`);

//     // Final state retrieval
//     const finalSessionObject = await runner.sessionService.getSession({appName: APP_NAME, userId, sessionId});
//     console.log("\n--- Final Session State ---");
//     if (finalSessionObject) {
//         console.log(finalSessionObject.state);
//     } else {
//         console.log("State not found (Final session object could not be retrieved).");
//     }
//     console.log("-".repeat(30));
// }


// const topic = "a robot developing unexpected emotions";
// // const topic = "the challenges of communicating with a plant-based alien species";

// // A simple hash function for demonstration
// const simpleHash = (s: string) => s.split('').reduce((a,b)=>{a=((a<<5)-a)+b.charCodeAt(0);return a&a},0);
// const sessionId = `${SESSION_ID_BASE}_${Math.abs(simpleHash(topic)) % 1000}`; // Unique session ID

// await callPipelineAsync(topic, USER_ID, sessionId);
