import {Gemini, LlmAgent, LlmSummarizer, TokenBasedContextCompactor} from '@google/adk';

const agent = new LlmAgent({
  name: 'my-agent',
  model: 'gemini-flash-latest',
  contextCompactors: [
    new TokenBasedContextCompactor({
      tokenThreshold: 1000, // Trigger compaction when session exceeds 1000 tokens.
      eventRetentionSize: 1, // Keep at least 1 raw event (overlap).
      summarizer: new LlmSummarizer({
        llm: new Gemini({model: 'gemini-flash-latest'}),
      }),
    }),
  ],
});