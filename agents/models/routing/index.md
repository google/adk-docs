# Route between models

Supported in ADKTypeScript v1.0.0Experimental

Experimental

Model routing is experimental and may change in future releases. We welcome your [feedback](https://github.com/google/adk-js/issues/new?template=feature_request.md)!

An `LlmAgent` uses a single model by default. When you need to dynamically select between different models for each request, you can define a routing function that chooses which model to use. `RoutedLlm` provides this capability, enabling model fallback on error, A/B testing between models, and auto-routing by input complexity. If the selected model fails before producing any output, the routing function is called again with error context so it can select a different model.

Pass a `RoutedLlm` as an `LlmAgent`'s `model` parameter. Use `RoutedLlm` when only the model varies between routes. If you also need to switch instructions, tools, or sub-agents, use [`RoutedAgent`](https://adk.dev/agents/routing/index.md) instead.

## How routing works

The `LlmRouter` function receives the map of available models and the current `LlmRequest`, and returns the key of the model to use:

```typescript
type LlmRouter = (
  models: Readonly<Record<string, BaseLlm>>,
  request: LlmRequest,
  errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
) => Promise<string | undefined> | string | undefined;
```

The `models` parameter accepts either a `Record<string, BaseLlm>` with explicit keys, or an array of `BaseLlm` instances. If an array is provided, each model's name is used as its key.

Failover follows the same rules as [`RoutedAgent`](https://adk.dev/agents/routing/#how-routing-works): the router is re-called with `errorContext` only if the selected model fails before yielding any response. After yielding, errors propagate without retry. The router can return `undefined` to stop retrying and propagate the last error.

**Live connections:** `RoutedLlm.connect()` selects the model at connection time. Once a live connection is established, the model cannot be switched mid-stream.

## Basic usage

The following example creates a `RoutedLlm` that tries a primary model first and falls back to a secondary model if the primary fails. The router checks `errorContext.failedKeys` to avoid re-selecting the failed model:

```typescript
import {
  BaseLlm,
  Gemini,
  LlmRequest,
  LlmAgent,
  RoutedLlm,
  InMemoryRunner,
} from '@google/adk';

const primaryModel = new Gemini({ model: 'gemini-flash-latest' });
const fallbackModel = new Gemini({ model: 'gemini-pro-latest' });

const router = (
  models: Readonly<Record<string, BaseLlm>>,
  request: LlmRequest,
  // errorContext is provided when a previously selected model fails
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

const routedLlm = new RoutedLlm({
  models: { primary: primaryModel, fallback: fallbackModel },
  router,
});

// Use RoutedLlm as the model for an LlmAgent
const agent = new LlmAgent({
  name: 'my_agent',
  model: routedLlm,
  instruction: 'You are a helpful assistant.',
});

const runner = new InMemoryRunner({ agent, appName: 'my_app' });

const session = await runner.sessionService.createSession({
  appName: 'my_app',
  userId: 'user_1',
});

const run = runner.runAsync({
  userId: 'user_1',
  sessionId: session.id,
  newMessage: { role: 'user', parts: [{ text: 'Hello!' }] },
});

for await (const event of run) {
  if (event.content?.parts?.[0]?.text) {
    console.log(event.content.parts[0].text);
  }
}
```
