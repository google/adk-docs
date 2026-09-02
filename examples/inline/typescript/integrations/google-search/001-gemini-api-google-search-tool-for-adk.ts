import {GOOGLE_SEARCH, LlmAgent} from '@google/adk';

export const rootAgent = new LlmAgent({
  model: 'gemini-flash-latest',
  name: 'root_agent',
  description:
      'an agent whose job it is to perform Google search queries and answer questions about the results.',
  instruction:
      'You are an agent whose job is to perform Google search queries and answer questions about the results.',
  tools: [GOOGLE_SEARCH],
});