# Cancel agent runs

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-typescript">TypeScript v1.0.0</span>
</div>

Long-running agent invocations can be gracefully cancelled using
`AbortController` and `AbortSignal`. Pass an `AbortSignal` to
`runner.runAsync()` to cancel operations at any point in the execution stack,
including agent execution, LLM generation, tool execution, and plugin callbacks.

## Basic usage

Create an `AbortController`, pass its `signal` to `runner.runAsync()`, and call
`controller.abort()` when you want to cancel execution:

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel-agent-runs/basic-usage.ts:full"
    ```

## Cancellation with a timeout

Use `AbortSignal.timeout()` to automatically cancel an agent run after a
specified duration. This is useful for enforcing time limits on agent execution.

Using the same agent and runner setup from the basic usage example, replace
everything from `const controller` onwards with:

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel-agent-runs/timeout.ts:run"
    ```

You can also combine a timeout with programmatic cancellation using
`AbortSignal.any()`. Using the same setup, replace everything from `const
controller` onwards with:

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel-agent-runs/combined-signal.ts:run"
    ```

## How cancellation propagates

When you abort the signal, cancellation propagates down through the entire
execution stack. Each component checks `abortSignal.aborted` at critical
lifecycle points and terminates early when it detects cancellation:

| Component | What happens on abort |
| :--- | :--- |
| **Runner** | Stops before session fetch, after plugin callbacks, and within the event streaming loop. |
| **LlmAgent** | Stops between execution steps, before/after model callbacks, and within response streaming. |
| **LoopAgent** | Stops between loop iterations and between sub-agent executions. |
| **ParallelAgent** | Stops when merging results from concurrent sub-agent runs. |
| **Models (Gemini)** | The signal is passed to the underlying Google GenAI SDK via `config.abortSignal`, cancelling the in-flight HTTP request. |
| **AgentTool** | Passes the signal to the sub-agent runner and checks for abort after session creation. |
| **MCPTool** | Passes the signal to the MCP client's `callTool` method. |

The `InvocationContext` also registers a listener on the signal that
automatically sets `endInvocation = true` when triggered, signaling all
components to wind down.

## AbortSignal in custom tools

When you pass an `AbortSignal` to `runner.runAsync()`, it is available on
`toolContext.abortSignal` inside your custom tools. The following example shows
the pattern for checking the abort signal inside a custom tool:

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel-agent-runs/custom-tool.ts:tool"
    ```

## Behavior on cancellation

When an `AbortSignal` is triggered, the following applies:

- **Graceful termination:** The async generator returned by `runner.runAsync()`
  completes (stops yielding events) without throwing an error.
- **Committed events persist:** Any events that were already yielded and
  processed by the Runner before the abort remain committed to the session
  history.
- **No partial events:** Events that were in progress but not yet yielded are
  discarded.
- **Resource cleanup:** In-flight LLM requests to the Gemini API are cancelled
  through the SDK's native `AbortSignal` support, freeing network resources.
