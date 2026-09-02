import {Agent, BuiltInCodeExecutor} from '@google/adk';

const rootAgent = new Agent({
  name: 'RootAgent',
  model: 'gemini-flash-latest',
  description: 'Code Agent',
  tools: [myCustomTool], // Assume myCustomTool is defined
  codeExecutor: new BuiltInCodeExecutor(), // <-- NOT supported when used with tools
});