import { LlmAgent, PRELOAD_MEMORY } from '@google/adk';

const agent = new LlmAgent({
    model: MODEL_ID,
    name: 'weather_sentiment_agent',
    instruction: "...",
    tools: [PRELOAD_MEMORY]
});