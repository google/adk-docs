// Before (ADK TypeScript 1.x)
const name = ctx.agent.name;

// After (ADK TypeScript 2.0), inside an agent's own execution
const name = requireAgent(ctx).name;

// After (ADK TypeScript 2.0), outside an agent's own execution
const name = ctx.agent?.name;