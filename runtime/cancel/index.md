# Cancel agent runs

Supported in ADKTypeScript v1.0.0

When an agent run takes too long, encounters changing conditions, or is no longer needed, you may want to cancel it without losing the work already completed. Cancellation in ADK is non-destructive: events already committed to the session remain persisted.

ADK supports graceful cancellation using `AbortController` and `AbortSignal`. Pass an `AbortSignal` to `runner.runAsync()` to cancel the entire invocation at any point in the execution stack, including agent execution, LLM generation, tool execution, and plugin callbacks.

## Get started

Create an `AbortController`, pass its `signal` to `runner.runAsync()`, and call `controller.abort()` when you want to cancel execution:

```typescript
import { Runner, InMemorySessionService, LlmAgent, FunctionTool } from '@google/adk';
import { z } from 'zod';

const getInfo = new FunctionTool({
  name: 'get_info',
  description: 'Gets information about a topic.',
  parameters: z.object({ topic: z.string() }),
  execute: (args) => ({ result: `Info about ${args.topic}` }),
});

const agent = new LlmAgent({
  name: 'my_agent',
  model: 'gemini-flash-latest',
  instruction: 'Always use the get_info tool before answering.',
  tools: [getInfo],
});

const sessionService = new InMemorySessionService();
const runner = new Runner({ agent, appName: 'my_app', sessionService });
const session = await sessionService.createSession({ appName: 'my_app', userId: 'user_1' });

const controller = new AbortController();
const run = runner.runAsync({
  userId: session.userId,
  sessionId: session.id,
  newMessage: { role: 'user', parts: [{ text: 'Tell me about quantum computing.' }] },
  abortSignal: controller.signal,
});

let count = 0;
for await (const event of run) {
  count++;
  console.log('Event:', event.author);
  controller.abort(); // Without this, 3+ events; with it, only 1.
}
console.log(`Done. Received ${count} event(s).`);
```

## How cancellation propagates

When you abort the signal, cancellation propagates down through the entire execution stack. Each component checks `abortSignal.aborted` at critical lifecycle points and terminates early when it detects cancellation:

| Component           | What happens on abort                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Runner**          | Stops before session fetch, after plugin callbacks, and within the event streaming loop.                                 |
| **LlmAgent**        | Stops between execution steps, before/after model callbacks, and within response streaming.                              |
| **LoopAgent**       | Stops between loop iterations and between sub-agent executions.                                                          |
| **ParallelAgent**   | Stops when merging results from concurrent sub-agent runs.                                                               |
| **Models (Gemini)** | The signal is passed to the underlying Google GenAI SDK via `config.abortSignal`, cancelling the in-flight HTTP request. |
| **AgentTool**       | Passes the signal to the sub-agent runner and checks for abort after session creation.                                   |
| **MCPTool**         | Passes the signal to the MCP client's `callTool` method.                                                                 |

The `InvocationContext` also registers a listener on the signal that automatically sets `endInvocation = true` when triggered, signaling all components to wind down.

### Behavior on cancellation

When an `AbortSignal` is triggered, the following applies:

- **Graceful termination:** The async generator returned by `runner.runAsync()` completes (stops yielding events) without throwing an error.
- **Committed events persist:** Any events that were already yielded and processed by the Runner before the abort remain committed to the session history.
- **No partial events:** Events that were in progress but not yet yielded are discarded.
- **Resource cleanup:** In-flight LLM requests to the Gemini API are cancelled through the SDK's native `AbortSignal` support, freeing network resources.

## Advanced examples

The following examples show additional cancellation patterns beyond the basic `AbortController` usage.

### Cancellation with a timeout

Use `AbortSignal.timeout()` to automatically cancel an agent run after a specified duration. This is useful for enforcing time limits on agent execution.

Using the same agent and runner setup from the get started example, replace everything from `const controller` onwards with:

```typescript
const run = runner.runAsync({
  userId: session.userId,
  sessionId: session.id,
  newMessage: { role: 'user', parts: [{ text: 'Tell me about quantum computing.' }] },
  abortSignal: AbortSignal.timeout(2_000), // Cancel after 2 seconds
});

let count = 0;
for await (const event of run) {
  count++;
  console.log('Event:', event.author);
}
console.log(`Done. Received ${count} event(s).`);
```

You can also combine a timeout with programmatic cancellation using `AbortSignal.any()`. Using the same setup, replace everything from `const controller` onwards with:

```typescript
const controller = new AbortController();

// Cancel on timeout OR programmatically via controller.abort()
// e.g.: cancelButton.addEventListener('click', () => controller.abort());
const combinedSignal = AbortSignal.any([
  controller.signal,
  AbortSignal.timeout(60_000),
]);

const run = runner.runAsync({
  userId: session.userId,
  sessionId: session.id,
  newMessage: { role: 'user', parts: [{ text: 'Tell me about quantum computing.' }] },
  abortSignal: combinedSignal,
});
```

### AbortSignal in custom tools

When you pass an `AbortSignal` to `runner.runAsync()`, it is available on `toolContext.abortSignal` inside your custom tools. The following example shows the pattern for checking the abort signal inside a custom tool:

```typescript
import { FunctionTool } from '@google/adk';
import { z } from 'zod';

const fetchItems = async (id: string) => ['item1', 'item2', 'item3'];
const processItem = async (item: string) => ({ processed: item });

const longRunningTool = new FunctionTool({
  name: 'process_data',
  description: 'Processes data in multiple steps.',
  parameters: z.object({
    dataId: z.string(),
  }),
  execute: async (args, toolContext) => {
    const items = await fetchItems(args.dataId);

    const results = [];
    for (const item of items) {
      // Check the abort signal before each step
      if (toolContext?.abortSignal?.aborted) {
        return { status: 'cancelled', processed: results.length };
      }

      results.push(await processItem(item));
    }

    return { status: 'complete', processed: results.length };
  },
});
```
