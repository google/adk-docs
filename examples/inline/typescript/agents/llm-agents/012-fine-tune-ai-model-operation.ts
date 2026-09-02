import { GenerateContentConfig } from '@google/genai';

const generateContentConfig: GenerateContentConfig = {
    temperature: 0.2, // More deterministic output
    maxOutputTokens: 250,
};

const agent = new LlmAgent({
    // ... other params
    generateContentConfig,
});