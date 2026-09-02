import {LlmAgent} from '@google/adk';

// --- Example #2: using a powerful Gemini Pro model with API Key in model ---
export const rootAgent = new LlmAgent({
  name: 'hello_time_agent',
  model: 'gemini-flash-latest',
  description: 'Gemini flash agent',
  instruction: `You are a fast and helpful Gemini assistant.`,
});