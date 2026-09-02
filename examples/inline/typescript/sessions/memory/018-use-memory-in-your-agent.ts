import { LlmAgent, PRELOAD_MEMORY, SingleAgentCallback } from '@google/adk';

const autoSaveSessionToMemoryCallback: SingleAgentCallback = async (callbackContext) => {
    if (callbackContext.invocationContext.memoryService) {
        await callbackContext.invocationContext.memoryService.addSessionToMemory(
            callbackContext.invocationContext.session
        );
    }
};

const agent = new LlmAgent({
    model: MODEL,
    name: "Generic_QA_Agent",
    instruction: "Answer the user's questions",
    tools: [PRELOAD_MEMORY],
    afterAgentCallback: autoSaveSessionToMemoryCallback,
});