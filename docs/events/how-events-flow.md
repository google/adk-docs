
Events are created at different points and processed systematically by the framework. Understanding this flow helps clarify how actions and history are managed.

*   **Generation Sources:**
    *   **User Input:** The `Runner` typically wraps initial user messages or mid-conversation inputs into an `Event` with `author='user'`.
    *   **Agent Logic:** Agents (`BaseAgent`, `LlmAgent`) explicitly `yield Event(...)` objects (setting `author=self.name`) to communicate responses or signal actions.
    *   **LLM Responses:** The ADK model integration layer translates raw LLM output (text, function calls, errors) into `Event` objects, authored by the calling agent.
    *   **Tool Results:** After a tool executes, the framework generates an `Event` containing the `function_response`. The `author` is typically the agent that requested the tool, while the `role` inside the `content` is set to `'user'` for the LLM history.


*   **Processing Flow:**
    1.  **Yield/Return:** An event is generated and yielded (Python) or returned/emitted (Java) by its source.
    2.  **Runner Receives:** The main `Runner` executing the agent receives the event.
    3.  **SessionService Processing:** The `Runner` sends the event to the configured `SessionService`. This is a critical step:
        *   **Applies Deltas:** The service merges `event.actions.state_delta` into `session.state` and updates internal records based on `event.actions.artifact_delta`. (Note: The actual artifact *saving* usually happened earlier when `context.save_artifact` was called).
        *   **Finalizes Metadata:** Assigns a unique `event.id` if not present, may update `event.timestamp`.
        *   **Persists to History:** Appends the processed event to the `session.events` list.
    4.  **External Yield:** The `Runner` yields (Python) or returns/emits (Java) the processed event outwards to the calling application (e.g., the code that invoked `runner.run_async`).

This flow ensures that state changes and history are consistently recorded alongside the communication content of each event.


## Common Event Examples (Illustrative Patterns)

Here are concise examples of typical events you might see in the stream:

*   **User Input:**
    ```json
    {
      "author": "user",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "Book a flight to London for next Tuesday"}]}
      // actions usually empty
    }
    ```
*   **Agent Final Text Response:** (`is_final_response() == True`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "Okay, I can help with that. Could you confirm the departure city?"}]},
      "partial": false,
      "turn_complete": true
      // actions might have state delta, etc.
    }
    ```
*   **Agent Streaming Text Response:** (`is_final_response() == False`)
    ```json
    {
      "author": "SummaryAgent",
      "invocation_id": "e-abc...",
      "content": {"parts": [{"text": "The document discusses three main points:"}]},
      "partial": true,
      "turn_complete": false
    }
    // ... more partial=True events follow ...
    ```
*   **Tool Call Request (by LLM):** (`is_final_response() == False`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"function_call": {"name": "find_airports", "args": {"city": "London"}}}]}
      // actions usually empty
    }
    ```
*   **Tool Result Provided (to LLM):** (`is_final_response()` depends on `skip_summarization`)
    ```json
    {
      "author": "TravelAgent", // Author is agent that requested the call
      "invocation_id": "e-xyz...",
      "content": {
        "role": "user", // Role for LLM history
        "parts": [{"function_response": {"name": "find_airports", "response": {"result": ["LHR", "LGW", "STN"]}}}]
      }
      // actions might have skip_summarization=True
    }
    ```
*   **State/Artifact Update Only:** (`is_final_response() == False`)
    ```json
    {
      "author": "InternalUpdater",
      "invocation_id": "e-def...",
      "content": null,
      "actions": {
        "state_delta": {"user_status": "verified"},
        "artifact_delta": {"verification_doc.pdf": 2}
      }
    }
    ```
*   **Agent Transfer Signal:** (`is_final_response() == False`)
    ```json
    {
      "author": "OrchestratorAgent",
      "invocation_id": "e-789...",
      "content": {"parts": [{"function_call": {"name": "transfer_to_agent", "args": {"agent_name": "BillingAgent"}}}]},
      "actions": {"transfer_to_agent": "BillingAgent"} // Added by framework
    }
    ```
*   **Loop Escalation Signal:** (`is_final_response() == False`)
    ```json
    {
      "author": "CheckerAgent",
      "invocation_id": "e-loop...",
      "content": {"parts": [{"text": "Maximum retries reached."}]}, // Optional content
      "actions": {"escalate": true}
    }
    ```