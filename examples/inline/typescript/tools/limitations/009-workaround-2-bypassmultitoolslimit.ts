import {Agent, BuiltInCodeExecutor} from '@google/adk';

const urlContextAgent = new Agent({
  model: 'gemini-flash-latest',
  name: 'UrlContextAgent',
  instruction: "You're a specialist in URL Context",
  tools: [myCustomTool], // Assume myCustomTool is defined
});

const codingAgent = new Agent({
  model: 'gemini-flash-latest',
  name: 'CodeAgent',
  instruction: "You're a specialist in Code Execution",
  codeExecutor: new BuiltInCodeExecutor(),
});

const rootAgent = new Agent({
  name: 'RootAgent',
  model: 'gemini-flash-latest',
  description: 'Root Agent',
  subAgents: [urlContextAgent, codingAgent], // NOT supported when sub-agents use built-in tools
});