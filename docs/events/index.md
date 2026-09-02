# Events

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

Events are the fundamental units of information flow within the Agent Development Kit (ADK). They represent every significant occurrence during an agent's interaction lifecycle, from initial user input to the final response and all the steps in between. Understanding events is crucial because they are the primary way components communicate, state is managed, and control flow is directed.

## What Events Are and Why They Matter

An `Event` in ADK is a record representing a specific point in the agent's execution. It captures user messages, agent replies, requests to use tools (function calls), tool results, state changes, control signals, and errors.

=== "Python"
    Technically, it's an instance of the `google.adk.events.Event` class, which builds upon the basic `LlmResponse` structure by adding essential ADK-specific metadata and an `actions` payload.

    ```python
    --8<-- "examples/inline/python/events/index/001-what-events-are-and-why-they-matter.py"
    ```

=== "TypeScript"
    In TypeScript, this is an interface of type `Event`.

    ```typescript
    --8<-- "examples/inline/typescript/events/index/002-what-events-are-and-why-they-matter.ts"
    ```

=== "Go"
    In Go, this is a struct of type `google.golang.org/adk/v2/session.Event`.

    ```go
    --8<-- "examples/inline/go/events/index/003-what-events-are-and-why-they-matter.go.txt"
    ```

=== "Java"
    In Java, this is an instance of the `com.google.adk.events.Event` class. It also builds upon a basic response structure by adding essential ADK-specific metadata and an `actions` payload.

    ```java
    --8<-- "examples/inline/java/events/index/004-what-events-are-and-why-they-matter.java"
    ```

=== "Kotlin"
    In Kotlin, this is an instance of the `com.google.adk.kt.events.Event` class.

    ```kotlin
    --8<-- "examples/inline/kotlin/events/index/005-what-events-are-and-why-they-matter.kt"
    ```



Events are central to ADK's operation for several key reasons:

1.  **Communication:** They serve as the standard message format between the user interface, the `Runner`, agents, the LLM, and tools. Everything flows as an `Event`.

2.  **Signaling State & Artifact Changes:** Events carry instructions for state modifications and track artifact updates. The `SessionService` uses these signals to ensure persistence. In Python changes are signaled via `event.actions.state_delta` and `event.actions.artifact_delta`.

3.  **Control Flow:** Specific fields like `event.actions.transfer_to_agent` or `event.actions.escalate` act as signals that direct the framework, determining which agent runs next or if a loop should terminate.

4.  **History & Observability:** The sequence of events recorded in `session.events` provides a complete, chronological history of an interaction, invaluable for debugging, auditing, and understanding agent behavior step-by-step.

In essence, the entire process, from a user's query to the agent's final answer, is orchestrated through the generation, interpretation, and processing of `Event` objects.


## Understanding and Using Events

As a developer, you'll primarily interact with the stream of events yielded by the `Runner`. Here's how to understand and extract information from them:

!!! Note
    The specific parameters or method names for the primitives may vary slightly by SDK language, for example the `event.content` attribute in Python and `event.content().get().parts()` in Java. Refer to the language-specific API documentation for details.

### Identifying Event Origin and Type

Quickly determine what an event represents by checking:

*   **Who sent it? (`event.author`)**
    *   `'user'`: Indicates input directly from the end-user.
    *   `'AgentName'`: Indicates output or action from a specific agent (e.g., `'WeatherAgent'`, `'SummarizerAgent'`).
*   **What's the main payload? (`event.content` and `event.content.parts`)**
    *   **Text:** Indicates a conversational message. For Python, check if `event.content.parts[0].text` exists. For Java, check if `event.content()` is present, its `parts()` are present and not empty, and the first part's `text()` is present.
    *   **Tool Call Request:** Check `event.get_function_calls()`. If not empty, the LLM is asking to execute one or more tools. Each item in the list has `.name` and `.args`.
    *   **Tool Result:** Check `event.get_function_responses()`. If not empty, this event carries the result(s) from tool execution(s). Each item has `.name` and `.response` (the dictionary returned by the tool). *Note:* For history structuring, the `role` inside the `content` is often `'user'`, but the event `author` is typically the agent that requested the tool call.

*   **Is it streaming output? (`event.partial`)**
    Indicates whether this is an incomplete chunk of text from the LLM.
    *   `True`: More text will follow.
    *   `False` or `None`/`Optional.empty()`: This part of the content is complete (though the overall turn might not be finished if `turn_complete` is also false).

=== "Python"

    ```python
    --8<-- "examples/inline/python/events/index/006-identifying-event-origin-and-type.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/events/index/007-identifying-event-origin-and-type.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/events/index/008-identifying-event-origin-and-type.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/events/index/009-identifying-event-origin-and-type.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/inline/kotlin/events/index/010-identifying-event-origin-and-type.kt"
    ```

### Extracting Key Information

Once you know the event type, access the relevant data:

*   **Text Content:**
    Always check for the presence of content and parts before accessing text. In Python its `text = event.content.parts[0].text`.

*   **Function Call Details:**

    === "Python"

        ```python
        --8<-- "examples/inline/python/events/index/011-extracting-key-information.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/events/index/012-extracting-key-information.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/events/index/013-extracting-key-information.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/events/index/014-extracting-key-information.java"
        ```

*   **Function Response Details:**

    === "Python"

        ```python
        --8<-- "examples/inline/python/events/index/015-extracting-key-information.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/events/index/016-extracting-key-information.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/events/index/017-extracting-key-information.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/events/index/018-extracting-key-information.java"
        ```

*   **Identifiers:**
    *   `event.id`: Unique ID for this specific event instance.
    *   `event.invocation_id`: ID for the entire user-request-to-final-response cycle this event belongs to. Useful for logging and tracing.

### Detecting Actions and Side Effects

The `event.actions` object signals changes that occurred or should occur. Always check if `event.actions` and it's fields/ methods exists before accessing them.

*   **State Changes:** Gives you a collection of key-value pairs that were modified in the session state during the step that produced this event.

    === "Python"
        `delta = event.actions.state_delta` (a dictionary of `{key: value}` pairs).
        ```python
        --8<-- "examples/inline/python/events/index/019-detecting-actions-and-side-effects.py"
        ```

    === "TypeScript"
        `delta = event.actions.stateDelta` (an object of `{key: value}` pairs).
        ```typescript
        --8<-- "examples/inline/typescript/events/index/020-detecting-actions-and-side-effects.ts"
        ```

    === "Go"
        `delta := event.Actions.StateDelta` (a `map[string]any`)
        ```go
        --8<-- "examples/inline/go/events/index/021-detecting-actions-and-side-effects.go.txt"
        ```

    === "Java"
        `ConcurrentMap<String, Object> delta = event.actions().stateDelta();`

        ```java
        --8<-- "examples/inline/java/events/index/022-detecting-actions-and-side-effects.java"
        ```

*   **Artifact Saves:** Gives you a collection indicating which artifacts were saved and their new version number (or relevant `Part` information).

    === "Python"
        `artifact_changes = event.actions.artifact_delta` (a dictionary of `{filename: version}`).
        ```python
        --8<-- "examples/inline/python/events/index/023-detecting-actions-and-side-effects.py"
        ```

    === "TypeScript"
        `artifact_changes = event.actions.artifactDelta` (an object of `{filename: version}`).
        ```typescript
        --8<-- "examples/inline/typescript/events/index/024-detecting-actions-and-side-effects.ts"
        ```

    === "Go"
        `artifactChanges := event.Actions.ArtifactDelta` (a `map[string]int64`)
        ```go
        --8<-- "examples/inline/go/events/index/025-detecting-actions-and-side-effects.go.txt"
        ```

    === "Java"
        `ConcurrentMap<String, Part> artifactChanges = event.actions().artifactDelta();`

        ```java
        --8<-- "examples/inline/java/events/index/026-detecting-actions-and-side-effects.java"
        ```

*   **Control Flow Signals:** Check boolean flags or string values:

    === "Python"
        *   `event.actions.transfer_to_agent` (string): Control should pass to the named agent.
        *   `event.actions.escalate` (bool): A loop should terminate.
        *   `event.actions.skip_summarization` (bool): A tool result should not be summarized by the LLM.
        ```python
        --8<-- "examples/inline/python/events/index/027-detecting-actions-and-side-effects.py"
        ```

    === "TypeScript"
        *   `event.actions.transferToAgent` (string): Control should pass to the named agent.
        *   `event.actions.escalate` (boolean): A loop should terminate.
        *   `event.actions.skipSummarization` (boolean): A tool result should not be summarized by the LLM.
        ```typescript
        --8<-- "examples/inline/typescript/events/index/028-detecting-actions-and-side-effects.ts"
        ```

    === "Go"
        *   `event.Actions.TransferToAgent` (string): Control should pass to the named agent.
        *   `event.Actions.Escalate` (bool): A loop should terminate.
        *   `event.Actions.SkipSummarization` (bool): A tool result should not be summarized by the LLM.
        ```go
        --8<-- "examples/inline/go/events/index/029-detecting-actions-and-side-effects.go.txt"
        ```

    === "Java"
        *   `event.actions().transferToAgent()` (returns `Optional<String>`): Control should pass to the named agent.
        *   `event.actions().escalate()` (returns `Optional<Boolean>`): A loop should terminate.
        *   `event.actions().skipSummarization()` (returns `Optional<Boolean>`): A tool result should not be summarized by the LLM.

        ```java
        --8<-- "examples/inline/java/events/index/030-detecting-actions-and-side-effects.java"
        ```

### Determining if an Event is a "Final" Response

Use the built-in helper method `event.is_final_response()` to identify events suitable for display as the agent's complete output for a turn.

*   **Purpose:** Filters out intermediate steps, such as tool calls and partial streaming text, from the final user-facing message(s).
*   **When `True`?**
    1.  The `skip_summarization` action is `True`. In Python this flag alone is enough, and the event does not need to carry a `function_response` tool result.
    2.  The event's `long_running_tool_ids` is non-empty, meaning a tool marked as `is_long_running=True` was called. In Python this list alone is enough, and the event does not need to carry the `function_call` itself. In Java, check if the `longRunningToolIds` list is empty:
        *   `event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()` is `true`.
    3.  OR, **all** of the following are met:
        *   No function calls (`get_function_calls()` is empty).
        *   No function responses (`get_function_responses()` is empty).
        *   Not a partial stream chunk (`partial` is not `True`).
        *   Doesn't end with a code execution result that might need further processing/display.
*   **Usage:** Filter the event stream in your application logic.

    === "Python"
        ```python
        --8<-- "examples/inline/python/events/index/031-determining-if-an-event-is-a-final-respo.py"
        ```

    === "TypeScript"
        ```typescript
        --8<-- "examples/inline/typescript/events/index/032-determining-if-an-event-is-a-final-respo.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/events/index/033-determining-if-an-event-is-a-final-respo.go.txt"
        ```

    === "Java"
        ```java
        --8<-- "examples/inline/java/events/index/034-determining-if-an-event-is-a-final-respo.java"
        ```

By carefully examining these aspects of an event, you can build robust applications that react appropriately to the rich information flowing through the ADK system.

## How Events Flow: Generation and Processing

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
        *   **Event Metadata:** In Python, the `Event` object already carries an `id` and a `timestamp` from the moment it is constructed, so the service does not assign them and records the event as it received it.
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
*   **State/Artifact Update Only:** (`is_final_response() == True`)
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
*   **Loop Escalation Signal:** (`is_final_response() == True`)
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

    === "TypeScript"
        When constructing an `Event` in your custom agent logic, set the author, for example: `createEvent({ author: this.name, ... })`

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
