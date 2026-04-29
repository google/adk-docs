# Model routing

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-typescript">TypeScript v1.0.0</span><span class="lst-preview">Experimental</span>
</div>

`RoutedLlm` wraps multiple LLM instances and uses a router function to
dynamically select which model handles each request. Pass a `RoutedLlm` as an
`LlmAgent`'s `model` parameter to get dynamic model selection. This enables
model fallback on error, A/B testing between models, and auto-routing by input
complexity. If the selected model fails before producing any output, the router
is called again with error context so it can select a different model.

Use `RoutedLlm` when only the model varies between routes. If you also need to
switch instructions, tools, or sub-agents, use
[`RoutedAgent`](../agent-routing.md) instead, which routes between entire agent
configurations.

## How routing works

The `LlmRouter` function receives the map of available models and the current
`LlmRequest`, and returns the key of the model to use:

=== "TypeScript"

    ```typescript
    type LlmRouter = (
      models: Readonly<Record<string, BaseLlm>>,
      request: LlmRequest,
      errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
    ) => Promise<string | undefined> | string | undefined;
    ```

The `models` parameter accepts either a `Record<string, BaseLlm>` with
explicit keys, or an array of `BaseLlm` instances. If an array is provided,
each model's name is used as its key.

Failover follows the same rules as
[`RoutedAgent`](../agent-routing.md#how-routing-works): the router is re-called
with `errorContext` only if the selected model fails before yielding any
response. After yielding, errors propagate without retry. The router can return
`undefined` to stop retrying and propagate the last error.

**Live connections:** `RoutedLlm.connect()` selects the model at connection
time. Once a live connection is established, the model cannot be switched
mid-stream.

## Basic usage

The following example creates a `RoutedLlm` that tries a primary model first
and falls back to a secondary model if the primary fails. The router checks
`errorContext.failedKeys` to avoid re-selecting the failed model:

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/model-routing/basic_usage.ts:full"
    ```
