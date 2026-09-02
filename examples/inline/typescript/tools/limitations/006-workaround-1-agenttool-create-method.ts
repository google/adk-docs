import {Agent, AgentTool, BuiltInCodeExecutor, GOOGLE_SEARCH} from '@google/adk';

const searchAgent = new Agent({
  model: 'gemini-flash-latest',
  name: 'SearchAgent',
  instruction: "You're a specialist in Google Search",
  tools: [GOOGLE_SEARCH],
});

const codingAgent = new Agent({
  model: 'gemini-flash-latest', // Built-in code execution requires Gemini 2.0+ in ADK JS
  name: 'CodeAgent',
  instruction: "You're a specialist in Code Execution",
  codeExecutor: new BuiltInCodeExecutor(),
});

const rootAgent = new Agent({
  name: 'RootAgent',
  model: 'gemini-flash-latest',
  description: 'Root Agent',
  tools: [new AgentTool({agent: searchAgent}), new AgentTool({agent: codingAgent})],
});