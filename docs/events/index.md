# Events

Events are the fundamental units of information flow within the Agent Development Kit (ADK). They represent every significant occurrence during an agent's interaction lifecycle, from initial user input to the final response and all the steps in between. Understanding events is crucial because they are the primary way components communicate, state is managed, and control flow is directed.

## What Events Are and Why They Matter

An `Event` in ADK is an immutable record representing a specific point in the agent's execution. It captures user messages, agent replies, requests to use tools (function calls), tool results, state changes, control signals, and errors. Technically, it's an instance of the `google.adk.events.Event` class, which builds upon the basic `LlmResponse` structure by adding essential ADK-specific metadata and an `actions` payload.

```python
# Conceptual Structure of an Event
# from google.adk.events import Event, EventActions
# from google.genai import types

# class Event(LlmResponse): # Simplified view
#     # --- LlmResponse fields ---
#     content: Optional[types.Content]
#     partial: Optional[bool]
#     # ... other response fields ...

#     # --- ADK specific additions ---
#     author: str          # 'user' or agent name
#     invocation_id: str   # ID for the whole interaction run
#     id: str              # Unique ID for this specific event
#     timestamp: float     # Creation time
#     actions: EventActions # Important for side-effects & control
#     branch: Optional[str] # Hierarchy path
#     # ...
```

Events are central to ADK's operation for several key reasons:

1.  **Communication:** They serve as the standard message format between the user interface, the `Runner`, agents, the LLM, and tools. Everything flows as an `Event`.
2.  **Signaling State & Artifact Changes:** Events carry instructions for state modifications via `event.actions.state_delta` and track artifact updates via `event.actions.artifact_delta`. The `SessionService` uses these signals to ensure persistence.
3.  **Control Flow:** Specific fields like `event.actions.transfer_to_agent` or `event.actions.escalate` act as signals that direct the framework, determining which agent runs next or if a loop should terminate.
4.  **History & Observability:** The sequence of events recorded in `session.events` provides a complete, chronological history of an interaction, invaluable for debugging, auditing, and understanding agent behavior step-by-step.

In essence, the entire process, from a user's query to the agent's final answer, is orchestrated through the generation, interpretation, and processing of `Event` objects.

## Understanding and Using Events

As a developer, you'll primarily interact with the stream of events yielded by the `Runner`. Here's how to understand and extract information from them:

### Identifying Event Origin and Type

Quickly determine what an event represents by checking:

*   **Who sent it? (`event.author`)**
    *   `'user'`: Indicates input directly from the end-user.
    *   `'AgentName'`: Indicates output or action from a specific agent (e.g., `'WeatherAgent'`, `'SummarizerAgent'`).
*   **What's the main payload? (`event.content` and `event.content.parts`)**
    *   **Text:** If `event.content.parts[0].text` exists, it's likely a conversational message.
    *   **Tool Call Request:** Check `event.get_function_calls()`. If not empty, the LLM is asking to execute one or more tools. Each item in the list has `.name` and `.args`.
    *   **Tool Result:** Check `event.get_function_responses()`. If not empty, this event carries the result(s) from tool execution(s). Each item has `.name` and `.response` (the dictionary returned by the tool). *Note:* For history structuring, the `role` inside the `content` is often `'user'`, but the event `author` is typically the agent that requested the tool call.
*   **Is it streaming output? (`event.partial`)**
    *   `True`: This is an incomplete chunk of text from the LLM; more will follow.
    *   `False` or `None`: This part of the content is complete (though the overall turn might not be finished if `turn_complete` is also false).

```python
# Pseudocode: Basic event identification
# async for event in runner.run_async(...):
#     print(f"Event from: {event.author}")
#
#     if event.content and event.content.parts:
#         if event.get_function_calls():
#             print("  Type: Tool Call Request")
#         elif event.get_function_responses():
#             print("  Type: Tool Result")
#         elif event.content.parts[0].text:
#             if event.partial:
#                 print("  Type: Streaming Text Chunk")
#             else:
#                 print("  Type: Complete Text Message")
#         else:
#             print("  Type: Other Content (e.g., code result)")
#     elif event.actions and (event.actions.state_delta or event.actions.artifact_delta):
#         print("  Type: State/Artifact Update")
#     else:
#         print("  Type: Control Signal or Other")

```

### Extracting Key Information

Once you know the event type, access the relevant data:

*   **Text Content:** `text = event.content.parts[0].text` (Always check `event.content` and `event.content.parts` first).
*   **Function Call Details:**
    ```python
    calls = event.get_function_calls()
    if calls:
        for call in calls:
            tool_name = call.name
            arguments = call.args # This is usually a dictionary
            print(f"  Tool: {tool_name}, Args: {arguments}")
            # Application might dispatch execution based on this
    ```
*   **Function Response Details:**
    ```python
    responses = event.get_function_responses()
    if responses:
        for response in responses:
            tool_name = response.name
            result_dict = response.response # The dictionary returned by the tool
            print(f"  Tool Result: {tool_name} -> {result_dict}")
    ```
*   **Identifiers:**
    *   `event.id`: Unique ID for this specific event instance.
    *   `event.invocation_id`: ID for the entire user-request-to-final-response cycle this event belongs to. Useful for logging and tracing.

### Detecting Actions and Side Effects

The `event.actions` object signals changes that occurred or should occur. Always check if `event.actions` exists before accessing its fields.

*   **State Changes:** `delta = event.actions.state_delta` gives you a dictionary of `{key: value}` pairs that were modified in the session state during the step that produced this event.
    ```python
    if event.actions and event.actions.state_delta:
        print(f"  State changes: {event.actions.state_delta}")
        # Update local UI or application state if necessary
    ```
*   **Artifact Saves:** `artifact_changes = event.actions.artifact_delta` gives you a dictionary of `{filename: version}` indicating which artifacts were saved and their new version number.
    ```python
    if event.actions and event.actions.artifact_delta:
        print(f"  Artifacts saved: {event.actions.artifact_delta}")
        # UI might refresh an artifact list
    ```
*   **Control Flow Signals:** Check boolean flags or string values:
    *   `event.actions.transfer_to_agent` (string): Control should pass to the named agent.
    *   `event.actions.escalate` (bool): A loop should terminate.
    *   `event.actions.skip_summarization` (bool): A tool result should not be summarized by the LLM.
    ```python
    if event.actions:
        if event.actions.transfer_to_agent:
            print(f"  Signal: Transfer to {event.actions.transfer_to_agent}")
        if event.actions.escalate:
            print("  Signal: Escalate (terminate loop)")
        if event.actions.skip_summarization:
            print("  Signal: Skip summarization for tool result")
    ```

### Determining if an Event is a "Final" Response

Use the built-in helper method `event.is_final_response()` to identify events suitable for display as the agent's complete output for a turn.

*   **Purpose:** Filters out intermediate steps (like tool calls, partial streaming text, internal state updates) from the final user-facing message(s).
*   **When `True`?**
    1.  The event contains a tool result (`function_response`) and `skip_summarization` is `True`.
    2.  The event contains a tool call (`function_call`) for a tool marked as `is_long_running=True`.
    3.  OR, **all** of the following are met:
        *   No function calls (`get_function_calls()` is empty).
        *   No function responses (`get_function_responses()` is empty).
        *   Not a partial stream chunk (`partial` is not `True`).
        *   Doesn't end with a code execution result that might need further processing/display.
*   **Usage:** Filter the event stream in your application logic.

    ```python
    # Pseudocode: Handling final responses in application
    # full_response_text = ""
    # async for event in runner.run_async(...):
    #     # Accumulate streaming text if needed...
    #     if event.partial and event.content and event.content.parts and event.content.parts[0].text:
    #         full_response_text += event.content.parts[0].text
    #
    #     # Check if it's a final, displayable event
    #     if event.is_final_response():
    #         print("\n--- Final Output Detected ---")
    #         if event.content and event.content.parts and event.content.parts[0].text:
    #              # If it's the final part of a stream, use accumulated text
    #              final_text = full_response_text + (event.content.parts[0].text if not event.partial else "")
    #              print(f"Display to user: {final_text.strip()}")
    #              full_response_text = "" # Reset accumulator
    #         elif event.actions.skip_summarization:
    #              # Handle displaying the raw tool result if needed
    #              response_data = event.get_function_responses()[0].response
    #              print(f"Display raw tool result: {response_data}")
    #         elif event.long_running_tool_ids:
    #              print("Display message: Tool is running in background...")
    #         else:
    #              # Handle other types of final responses if applicable
    #              print("Display: Final non-textual response or signal.")

    ```

By carefully examining these aspects of an event, you can build robust applications that react appropriately to the rich information flowing through the ADK system.

## How Events Flow: Generation and Processing 

Events are created at different points and processed systematically by the framework. Understanding this flow helps clarify how actions and history are managed.

*   **Generation Sources:**
    *   **User Input:** The `Runner` typically wraps initial user messages or mid-conversation inputs into an `Event` with `author='user'`.
    *   **Agent Logic:** Agents (`BaseAgent`, `LlmAgent`) explicitly `yield Event(...)` objects (setting `author=self.name`) to communicate responses or signal actions.
    *   **LLM Responses:** The ADK model integration layer (e.g., `google_llm.py`) translates raw LLM output (text, function calls, errors) into `Event` objects, authored by the calling agent.
    *   **Tool Results:** After a tool executes, the framework generates an `Event` containing the `function_response`. The `author` is typically the agent that requested the tool, while the `role` inside the `content` is set to `'user'` for the LLM history.

*   **Processing Flow:**
    1.  **Yield:** An event is generated and yielded by its source.
    2.  **Runner Receives:** The main `Runner` executing the agent receives the event.
    3.  **SessionService Processing (`append_event`):** The `Runner` sends the event to the configured `SessionService`. This is a critical step:
        *   **Applies Deltas:** The service merges `event.actions.state_delta` into `session.state` and updates internal records based on `event.actions.artifact_delta`. (Note: The actual artifact *saving* usually happened earlier when `context.save_artifact` was called).
        *   **Finalizes Metadata:** Assigns a unique `event.id` if not present, may update `event.timestamp`.
        *   **Persists to History:** Appends the processed event to the `session.events` list.
    4.  **External Yield:** The `Runner` yields the processed event outwards to the calling application (e.g., the code that invoked `runner.run_async`).

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


## Additional Context and Event Details

Beyond the core concepts, here are a few specific details about context and events that are important for certain use cases:

1.  **`ToolContext.function_call_id` (Linking Tool Actions):**
    *   When an LLM requests a tool (`FunctionCall`), that request has an ID. The `ToolContext` provided to your tool function includes this `function_call_id`.
    *   **Importance:** This ID is crucial for linking actions like authentication (`request_credential`, `get_auth_response`) back to the specific tool request that initiated them, especially if multiple tools are called in one turn. The framework uses this ID internally.

2.  **How State/Artifact Changes are Recorded:**
    *   When you modify state (`context.state['key'] = value`) or save an artifact (`context.save_artifact(...)`) using `CallbackContext` or `ToolContext`, these changes aren't immediately written to persistent storage.
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

*   **Clear Authorship:** When building custom agents (`BaseAgent`), ensure `yield Event(author=self.name, ...)` to correctly attribute agent actions in the history. The framework generally handles authorship correctly for LLM/tool events.
*   **Semantic Content & Actions:** Use `event.content` for the core message/data (text, function call/response). Use `event.actions` specifically for signaling side effects (state/artifact deltas) or control flow (`transfer`, `escalate`, `skip_summarization`).
*   **Idempotency Awareness:** Understand that the `SessionService` is responsible for applying the state/artifact changes signaled in `event.actions`. While ADK services aim for consistency, consider potential downstream effects if your application logic re-processes events.
*   **Use `is_final_response()`:** Rely on this helper method in your application/UI layer to identify complete, user-facing text responses. Avoid manually replicating its logic.
*   **Leverage History:** The `session.events` list is your primary debugging tool. Examine the sequence of authors, content, and actions to trace execution and diagnose issues.
*   **Use Metadata:** Use `invocation_id` to correlate all events within a single user interaction. Use `event.id` to reference specific, unique occurrences.

Treating events as structured messages with clear purposes for their content and actions is key to building, debugging, and managing complex agent behaviors in ADK.