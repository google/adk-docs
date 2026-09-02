import {Gemini, LlmAgent, LlmSummarizer, TokenBasedContextCompactor} from '@google/adk';

// Define the AI model to be used for summarization:
const summarizationLlm = new Gemini({model: 'gemini-flash-latest'});

// Create the summarizer with the custom model:
const mySummarizer = new LlmSummarizer({llm: summarizationLlm});

// Configure the agent with the custom summarizer and compaction settings:
const agent = new LlmAgent({
  name: 'my-agent',
  model: 'gemini-flash-latest',
  contextCompactors: [
    new TokenBasedContextCompactor({
      tokenThreshold: 1000,
      eventRetentionSize: 1,
      summarizer: mySummarizer,
    }),
  ],
});