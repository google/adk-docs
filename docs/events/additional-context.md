
Beyond the core concepts, here are a few specific details about context and events that are important for certain use cases:

1.  **`ToolContext.function_call_id` (Linking Tool Actions):**
    *   When an LLM requests a tool (FunctionCall), that request has an ID. The `ToolContext` provided to your tool function includes this `function_call_id`.
    *   **Importance:** This ID is crucial for linking actions like authentication back to the specific tool request that initiated them, especially if multiple tools are called in one turn. The framework uses this ID internally.

2.  **How State/Artifact Changes are Recorded:**
    *   When you modify state or save an artifact using `CallbackContext` or `ToolContext`, these changes aren't immediately written to persistent storage.
    *   Instead, they populate the `state_delta` and `artifact_delta` fields within the `EventActions` object.
    *   This `EventActions` object is attached to the *next event* generated after the change (e.g., the agent's response or a tool result event).
    *   The `SessionService.append_event` method reads these deltas from the incoming event and applies them to the session's persistent state and artifact records. This ensures changes are tied chronologically to the event stream.

3.  **State Scope Prefixes (`app:`, `user:`, `temp:`):**
    *   When managing state via `context.state`, you can optionally use prefixes:
        *   `app:my_setting`: Suggests state relevant to the entire application (requires a persistent `SessionService`).
        *   `user:user_preference`: Suggests state relevant to the specific user across sessions (requires a persistent `SessionService`).
        *   `temp:intermediate_result` or no prefix: Typically session-specific or temporary state for the current invocation.
    *   The underlying `SessionService` determines how these prefixes are handled for persistence.

4.  **Error Events:**
    *   An `Event` can represent an error. Check the `event.error_code` and `event.error_message` fields (inherited from `LlmResponse`).
    *   Errors might originate from the LLM (e.g., safety filters, resource limits) or potentially be packaged by the framework if a tool fails critically. Check tool `FunctionResponse` content for typical tool-specific errors.
    ```json
    // Example Error Event (conceptual)
    {
      "author": "LLMAgent",
      "invocation_id": "e-err...",
      "content": null,
      "error_code": "SAFETY_FILTER_TRIGGERED",
      "error_message": "Response blocked due to safety settings.",
      "actions": {}
    }
    ```

These details provide a more complete picture for advanced use cases involving tool authentication, state persistence scope, and error handling within the event stream.

## Best Practices for Working with Events

To use events effectively in your ADK applications:

*   **Clear Authorship:** When building custom agents, ensure correct attribution for agent actions in the history. The framework generally handles authorship correctly for LLM/tool events.

    === "Python"
        Use `yield Event(author=self.name, ...)` in `BaseAgent` subclasses.

    === "Go"
        In custom agent `Run` methods, the framework typically handles authorship. If creating an event manually, set the author: `yield(&session.Event{Author: a.name, ...}, nil)`

    === "Java"
        When constructing an `Event` in your custom agent logic, set the author, for example: `Event.builder().author(this.getAgentName()) // ... .build();`

*   **Semantic Content & Actions:** Use `event.content` for the core message/data (text, function call/response). Use `event.actions` specifically for signaling side effects (state/artifact deltas) or control flow (`transfer`, `escalate`, `skip_summarization`).
*   **Idempotency Awareness:** Understand that the `SessionService` is responsible for applying the state/artifact changes signaled in `event.actions`. While ADK services aim for consistency, consider potential downstream effects if your application logic re-processes events.
*   **Use `is_final_response()`:** Rely on this helper method in your application/UI layer to identify complete, user-facing text responses. Avoid manually replicating its logic.
*   **Leverage History:** The session's event list is your primary debugging tool. Examine the sequence of authors, content, and actions to trace execution and diagnose issues.
*   **Use Metadata:** Use `invocation_id` to correlate all events within a single user interaction. Use `event.id` to reference specific, unique occurrences.

Treating events as structured messages with clear purposes for their content and actions is key to building, debugging, and managing complex agent behaviors in ADK.
