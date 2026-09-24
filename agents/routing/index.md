# Route between agents

Supported in ADKTypeScript v1.0.0Experimental

Experimental

Agent routing is experimental and may change in future releases. We welcome your [feedback](https://github.com/google/adk-js/issues/new?template=feature_request.md)!

When building agents for different tasks, you can define a routing function that selects which one handles each invocation at runtime. `RoutedAgent` provides this capability, enabling agent fallback on error, A/B testing, planning modes, and auto-routing by input complexity. If the selected agent fails before producing any output, the routing function is called again with error context so it can select a fallback.

`RoutedAgent` is different from [workflow agents](https://adk.dev/agents/workflow-agents/index.md) like `SequentialAgent` or `ParallelAgent`, which orchestrate multiple agents in a fixed pattern, and from [LLM-driven delegation](/agents/custom-agents/#delegation), where the LLM decides which agent to hand off to. With `RoutedAgent`, you write an explicit routing function that selects **one** agent per invocation. For model-level routing, see [Model routing](https://adk.dev/agents/models/routing/index.md).

## How routing works

Both `RoutedAgent` and [`RoutedLlm`](https://adk.dev/agents/models/routing/index.md) are powered by a shared routing utility that handles selection and failover.

The router function receives the map of available agents and the current context, and returns the key of the agent to run. It can be synchronous or async:

```typescript
type AgentRouter = (
  agents: Readonly<Record<string, BaseAgent>>,
  context: InvocationContext,
  errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
) => Promise<string | undefined> | string | undefined;
```

**The `agents` parameter** accepts either a `Record<string, BaseAgent>` with explicit keys, or an array of agents. If an array is provided, each agent's `name` property is used as its key.

**Failover behavior:**

- The router is first called without `errorContext` to make the initial selection.
- If the selected agent throws an error **before yielding any events**, the router is called again with `errorContext` containing `failedKeys` and `lastError`.
- If the selected agent throws an error **after yielding events**, the error propagates directly without retry, because partial results have already been emitted.
- A key that has already been tried cannot be re-selected. If the router returns a previously failed key, the error propagates.
- If the router returns `undefined`, routing stops and the last error is thrown.

## Basic usage

Create multiple agents, define a router function that returns a key, and wrap them in a `RoutedAgent`. The following example routes between two agents based on an external configuration value that can change between invocations:

```typescript
import { LlmAgent, RoutedAgent, InMemoryRunner } from '@google/adk';

const agentA = new LlmAgent({
  name: 'agent_a',
  model: 'gemini-flash-latest',
  instruction: 'You are Agent A. Always identify yourself as Agent A.',
});

const agentB = new LlmAgent({
  name: 'agent_b',
  model: 'gemini-flash-latest',
  instruction: 'You are Agent B. Always identify yourself as Agent B.',
});

// External configuration that can change at runtime
const config = { selectedAgent: 'agent_a' };

const routedAgent = new RoutedAgent({
  name: 'my_routed_agent',
  agents: { agent_a: agentA, agent_b: agentB },
  router: () => config.selectedAgent,
});

const runner = new InMemoryRunner({
  agent: routedAgent,
  appName: 'my_app',
});

const session = await runner.sessionService.createSession({
  appName: 'my_app',
  userId: 'user_1',
});

const run = runner.runAsync({
  userId: 'user_1',
  sessionId: session.id,
  newMessage: { role: 'user', parts: [{ text: 'Who are you?' }] },
});

for await (const event of run) {
  if (event.content?.parts?.[0]?.text) {
    console.log(event.content.parts[0].text);
  }
}
```

Change `config.selectedAgent` to `'agent_b'` before the next invocation to route to a different agent.

## Fallback on error

When an agent fails, the router is called again with `errorContext` so it can select a fallback. Failover only applies if the agent fails before yielding any events (see [How routing works](#how-routing-works)). The following example checks `errorContext.failedKeys` to avoid re-selecting the failed agent:

```typescript
import {
  BaseAgent,
  InvocationContext,
  LlmAgent,
  RoutedAgent,
} from '@google/adk';

const primaryAgent = new LlmAgent({
  name: 'primary',
  model: 'gemini-flash-latest',
  instruction: 'You are the primary agent.',
});

const fallbackAgent = new LlmAgent({
  name: 'fallback',
  model: 'gemini-pro-latest',
  instruction: 'You are the fallback agent.',
});

const router = (
  agents: Readonly<Record<string, BaseAgent>>,
  context: InvocationContext,
  // errorContext is provided when a previously selected agent fails
  errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
) => {
  if (!errorContext) {
    return 'primary'; // Try primary first
  }
  if (errorContext.failedKeys.has('primary')) {
    return 'fallback'; // Fall back if primary failed
  }
  return undefined; // No more options, propagate the error
};

const routedAgent = new RoutedAgent({
  name: 'my_routed_agent',
  agents: { primary: primaryAgent, fallback: fallbackAgent },
  router,
});
```

## Planning mode

A router can read any external state to select between agents with different instructions, models, and tools. This lets you implement a planning mode where the agent switches behavior dynamically. For example, a basic agent might have read and write tools, while a planning agent is restricted to read-only access and uses a more powerful model for analysis.

The following example shows a different `RoutedAgent` configuration. See [basic usage](#basic-usage) for the full runner setup.

```typescript
import {
  FunctionTool,
  LlmAgent,
  RoutedAgent,
} from '@google/adk';
import { z } from 'zod';

const readFileTool = new FunctionTool({
  name: 'read_file',
  description: 'Reads content from a file.',
  parameters: z.object({ filePath: z.string() }),
  execute: (args) => ({ content: `Contents of ${args.filePath}` }),
});

const writeFileTool = new FunctionTool({
  name: 'write_file',
  description: 'Writes content to a file.',
  parameters: z.object({ filePath: z.string(), content: z.string() }),
  execute: (args) => ({ result: `Wrote to ${args.filePath}` }),
});

const basicAgent = new LlmAgent({
  name: 'basic',
  model: 'gemini-flash-latest',
  instruction: 'You are a basic assistant. Use tools to help the user.',
  tools: [readFileTool, writeFileTool],
});

const planningAgent = new LlmAgent({
  name: 'planning',
  model: 'gemini-flash-latest',
  instruction: 'You are a planning expert. Analyze carefully. You can only read files.',
  tools: [readFileTool],
});

// Toggle this to switch between basic and planning agents
let planningMode = false;

const routedAgent = new RoutedAgent({
  name: 'my_routed_agent',
  agents: { basic: basicAgent, planning: planningAgent },
  router: () => (planningMode ? 'planning' : 'basic'),
});
```

Set `planningMode = true` before an invocation to route to the planning agent with its restricted tool set and different instructions.

## Auto-routing by complexity

The router function can call a lightweight classifier model to categorize input and route to different agents accordingly. Because the router can be async, you can make LLM calls inside it before selecting an agent.

The following example shows a different `RoutedAgent` configuration. See [basic usage](#basic-usage) for the full runner setup.

```typescript
import {
  BaseAgent,
  Gemini,
  InvocationContext,
  LlmAgent,
  RoutedAgent,
} from '@google/adk';

const simpleAgent = new LlmAgent({
  name: 'simple',
  model: 'gemini-flash-latest',
  instruction: 'You are a simple assistant for basic questions.',
});

const complexAgent = new LlmAgent({
  name: 'complex',
  model: 'gemini-pro-latest',
  instruction: 'You are an expert assistant for complex analysis.',
});

// Lightweight model to classify input complexity
const classifierModel = new Gemini({ model: 'gemini-flash-latest' });

const router = async (
  agents: Readonly<Record<string, BaseAgent>>,
  context: InvocationContext,
) => {
  // Extract the user's input text
  const text = context.userContent?.parts?.[0]?.text || '';
  if (!text) return 'simple';

  const prompt =
    `Classify this request as 'simple' or 'complex'. ` +
    `Reply with ONLY that word.\nRequest: "${text}"`;

  const generator = classifierModel.generateContentAsync({
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    toolsDict: {},
    liveConnectConfig: {},
  });

  let classification = '';
  for await (const resp of generator) {
    if (resp.content?.parts?.[0]?.text) {
      classification += resp.content.parts[0].text;
    }
  }

  return classification.toLowerCase().includes('complex')
    ? 'complex'
    : 'simple';
};

const routedAgent = new RoutedAgent({
  name: 'my_routed_agent',
  agents: { simple: simpleAgent, complex: complexAgent },
  router,
});
```
