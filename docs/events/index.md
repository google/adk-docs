# Events

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Events are the fundamental units of information flow within the Agent Development Kit (ADK). They represent every significant occurrence during an agent's interaction lifecycle, from initial user input to the final response and all the steps in between. Understanding events is crucial because they are the primary way components communicate, state is managed, and control flow is directed.

## What Events Are and Why They Matter

An `Event` in ADK is an immutable record representing a specific point in the agent's execution. It captures user messages, agent replies, requests to use tools (function calls), tool results, state changes, control signals, and errors.

=== "Python"
    Technically, it's an instance of the `google.adk.events.Event` class, which builds upon the basic `LlmResponse` structure by adding essential ADK-specific metadata and an `actions` payload.

    ```python
    # Conceptual Structure of an Event (Python)
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

=== "Go"
    In Go, this is a struct of type `google.golang.org/adk/session.Event`.

    ```go
    // Conceptual Structure of an Event (Go - See session/session.go)
    // Simplified view based on the session.Event struct
    type Event struct {
        // --- Fields from embedded model.LLMResponse ---
        model.LLMResponse

        // --- ADK specific additions ---
        Author       string         // 'user' or agent name
        InvocationID string         // ID for the whole interaction run
        ID           string         // Unique ID for this specific event
        Timestamp    time.Time      // Creation time
        Actions      EventActions   // Important for side-effects & control
        Branch       string         // Hierarchy path
        // ... other fields
    }

    // model.LLMResponse contains the Content field
    type LLMResponse struct {
        Content *genai.Content
        // ... other fields
    }
    ```

=== "Java"
    In Java, this is an instance of the `com.google.adk.events.Event` class. It also builds upon a basic response structure by adding essential ADK-specific metadata and an `actions` payload.

    ```java
    // Conceptual Structure of an Event (Java - See com.google.adk.events.Event.java)
    // Simplified view based on the provided com.google.adk.events.Event.java
    // public class Event extends JsonBaseModel {
    //     // --- Fields analogous to LlmResponse ---
    //     private Optional<Content> content;
    //     private Optional<Boolean> partial;
    //     // ... other response fields like errorCode, errorMessage ...

    //     // --- ADK specific additions ---
    //     private String author;         // 'user' or agent name
    //     private String invocationId;   // ID for the whole interaction run
    //     private String id;             // Unique ID for this specific event
    //     private long timestamp;        // Creation time (epoch milliseconds)
    //     private EventActions actions;  // Important for side-effects & control
    //     private Optional<String> branch; // Hierarchy path
    //     // ... other fields like turnComplete, longRunningToolIds etc.
    // }
    ```

Events are central to ADK's operation for several key reasons:

1.  **Communication:** They serve as the standard message format between the user interface, the `Runner`, agents, the LLM, and tools. Everything flows as an `Event`.

2.  **Signaling State & Artifact Changes:** Events carry instructions for state modifications and track artifact updates. The `SessionService` uses these signals to ensure persistence. In Python changes are signaled via `event.actions.state_delta` and `event.actions.artifact_delta`.

3.  **Control Flow:** Specific fields like `event.actions.transfer_to_agent` or `event.actions.escalate` act as signals that direct the framework, determining which agent runs next or if a loop should terminate.

4.  **History & Observability:** The sequence of events recorded in `session.events` provides a complete, chronological history of an interaction, invaluable for debugging, auditing, and understanding agent behavior step-by-step.

In essence, the entire process, from a user's query to the agent's final answer, is orchestrated through the generation, interpretation, and processing of `Event` objects.

