/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
// --8<-- [start:full_example]
import {
    InMemoryMemoryService,
    InMemorySessionService,
    LOAD_MEMORY,
    LlmAgent,
    Runner
} from '@google/adk';
import { createUserContent } from '@google/genai';

// --- Constants ---
const APP_NAME = "memory_example_app";
const USER_ID = "mem_user";
const MODEL = "gemini-2.5-flash";

// --- Agent Definitions ---

// Agent 1: Simple agent to capture information
const infoCaptureAgent = new LlmAgent({
    model: MODEL,
    name: "InfoCaptureAgent",
    instruction: "Acknowledge the user's statement concisely.",
});

// Agent 2: Agent that can use memory
const memoryRecallAgent = new LlmAgent({
    model: MODEL,
    name: "MemoryRecallAgent",
    instruction: "Answer the user's question. Use the 'load_memory' tool if the answer might be in past conversations.",
    tools: [LOAD_MEMORY]
});

// Export for 'adk run' compatibility (to avoid 'No BaseAgent found' error)
export const root_agent = memoryRecallAgent;

// --- Services ---
const sessionService = new InMemorySessionService();
const memoryService = new InMemoryMemoryService();

async function runScenario() {
    // --- Turn 1: Capture some information in a session ---
    console.log("--- Turn 1: Capturing Information ---");
    const runner1 = new Runner({
        agent: infoCaptureAgent,
        appName: APP_NAME,
        sessionService,
        memoryService
    });
    
    const session1Id = "session_info";
    await sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: session1Id });
    const userInput1 = createUserContent("My favorite project is Project Alpha.");

    let finalResponseText = "(No final response)";
    for await (const event of runner1.runAsync({ userId: USER_ID, sessionId: session1Id, newMessage: userInput1 })) {
        // Capture any text response from the agent
        if (event.author === infoCaptureAgent.name && event.content?.parts) {
            const text = event.content.parts.map(p => p.text || "").join("").trim();
            if (text) finalResponseText = text;
        }
    }
    console.log(`Agent 1 Response: ${finalResponseText}`);

    // Get the completed session and add to Memory
    const completedSession1 = await sessionService.getSession({ appName: APP_NAME, userId: USER_ID, sessionId: session1Id });
    console.log("\n--- Adding Session 1 to Memory ---");
    if (completedSession1) {
        await memoryService.addSessionToMemory(completedSession1);
        console.log("Session added to memory.");
    }

    // --- Turn 2: Recall the information in a new session ---
    console.log("\n--- Turn 2: Recalling Information ---");
    const runner2 = new Runner({
        agent: memoryRecallAgent,
        appName: APP_NAME,
        sessionService,
        memoryService
    });
    
    const session2Id = "session_recall";
    await sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: session2Id });
    const userInput2 = createUserContent("What is my favorite project?");

    let finalResponseText2 = "(No final response)";
    for await (const event of runner2.runAsync({ userId: USER_ID, sessionId: session2Id, newMessage: userInput2 })) {
        // Capture any text response from the agent
        if (event.author === memoryRecallAgent.name && event.content?.parts) {
            const text = event.content.parts.map(p => p.text || "").join("").trim();
            if (text) finalResponseText2 = text;
        }
    }
    console.log(`Agent 2 Response: ${finalResponseText2}`);

    // Exit immediately to prevent the ADK CLI from starting an interactive loop
    process.exit(0);
}

// Execute the scenario
runScenario().catch(err => {
    console.error(err);
    process.exit(1);
});
// --8<-- [end:full_example]
