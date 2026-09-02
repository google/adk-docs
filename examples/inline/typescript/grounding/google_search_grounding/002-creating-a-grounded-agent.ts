import { LlmAgent, GOOGLE_SEARCH } from '@google/adk';

const rootAgent = new LlmAgent({
    name: "google_search_agent",
    model: "gemini-flash-latest",
    instruction: "Answer questions using Google Search when needed. Always cite sources.",
    description: "Professional search assistant with Google Search capabilities",
    tools: [GOOGLE_SEARCH],
});