# Understanding and Using Events

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

As a developer, you'll primarily interact with the stream of events yielded by the `Runner`. Here's how to understand and extract information from them:

!!! Note
    The specific parameters or method names for the primitives may vary slightly by SDK language (e.g., `event.content()` in Python, `event.content().get().parts()` in Java). Refer to the language-specific API documentation for details.

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
    # Pseudocode: Basic event identification (Python)
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

=== "Go"

    ```go
      // Pseudocode: Basic event identification (Go)
    import (
      "fmt"
      "google.golang.org/adk/session"
      "google.golang.org/genai"
    )

    func hasFunctionCalls(content *genai.Content) bool {
      if content == nil {
        return false
      }
      for _, part := range content.Parts {
        if part.FunctionCall != nil {
          return true
        }
      }
      return false
    }

    func hasFunctionResponses(content *genai.Content) bool {
      if content == nil {
        return false
      }
      for _, part := range content.Parts {
        if part.FunctionResponse != nil {
          return true
        }
      }
      return false
    }

    func processEvents(events <-chan *session.Event) {
      for event := range events {
        fmt.Printf("Event from: %s\n", event.Author)

        if event.LLMResponse != nil && event.LLMResponse.Content != nil {
          if hasFunctionCalls(event.LLMResponse.Content) {
            fmt.Println("  Type: Tool Call Request")
          } else if hasFunctionResponses(event.LLMResponse.Content) {
            fmt.Println("  Type: Tool Result")
          } else if len(event.LLMResponse.Content.Parts) > 0 {
            if event.LLMResponse.Content.Parts[0].Text != "" {
              if event.LLMResponse.Partial {
                fmt.Println("  Type: Streaming Text Chunk")
              } else {
                fmt.Println("  Type: Complete Text Message")
              }
            } else {
              fmt.Println("  Type: Other Content (e.g., code result)")
            }
          }
        } else if len(event.Actions.StateDelta) > 0 {
          fmt.Println("  Type: State Update")
        } else {
          fmt.Println("  Type: Control Signal or Other")
        }
      }
    }

    ```

=== "Java"

    ```java
    // Pseudocode: Basic event identification (Java)
    // import com.google.genai.types.Content;
    // import com.google.adk.events.Event;
    // import com.google.adk.events.EventActions;

    // runner.runAsync(...).forEach(event -> { // Assuming a synchronous stream or reactive stream
    //     System.out.println("Event from: " + event.author());
    //
    //     if (event.content().isPresent()) {
    //         Content content = event.content().get();
    //         if (!event.functionCalls().isEmpty()) {
    //             System.out.println("  Type: Tool Call Request");
    //         } else if (!event.functionResponses().isEmpty()) {
    //             System.out.println("  Type: Tool Result");
    //         } else if (content.parts().isPresent() && !content.parts().get().isEmpty() &&
    //                    content.parts().get().get(0).text().isPresent()) {
    //             if (event.partial().orElse(false)) {
    //                 System.out.println("  Type: Streaming Text Chunk");
    //             } else {
    //                 System.out.println("  Type: Complete Text Message");
    //             }
    //         } else {
    //             System.out.println("  Type: Other Content (e.g., code result)");
    //         }
    //     } else if (event.actions() != null &&
    //                ((event.actions().stateDelta() != null && !event.actions().stateDelta().isEmpty()) ||
    //                 (event.actions().artifactDelta() != null && !event.actions().artifactDelta().isEmpty()))) {
    //         System.out.println("  Type: State/Artifact Update");
    //     } else {
    //         System.out.println("  Type: Control Signal or Other");
    //     }
    // });
    ```

### Extracting Key Information

Once you know the event type, access the relevant data:

*   **Text Content:**
    Always check for the presence of content and parts before accessing text. In Python its `text = event.content.parts[0].text`.

*   **Function Call Details:**

    === "Python"

        ```python
        calls = event.get_function_calls()
        if calls:
            for call in calls:
                tool_name = call.name
                arguments = call.args # This is usually a dictionary
                print(f"  Tool: {tool_name}, Args: {arguments}")
                # Application might dispatch execution based on this
        ```

    === "Go"

        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
            "google.golang.org/genai"
        )

        func handleFunctionCalls(event *session.Event) {
            if event.LLMResponse == nil || event.LLMResponse.Content == nil {
                return
            }
            calls := event.Content.FunctionCalls()
            if len(calls) > 0 {
                for _, call := range calls {
                    toolName := call.Name
                    arguments := call.Args
                    fmt.Printf("  Tool: %s, Args: %v\n", toolName, arguments)
                    // Application might dispatch execution based on this
                }
            }
        }
        ```

    === "Java"

        ```java
        import com.google.genai.types.FunctionCall;
        import com.google.common.collect.ImmutableList;
        import java.util.Map;

        ImmutableList<FunctionCall> calls = event.functionCalls(); // from Event.java
        if (!calls.isEmpty()) {
          for (FunctionCall call : calls) {
            String toolName = call.name().get();
            // args is Optional<Map<String, Object>>
            Map<String, Object> arguments = call.args().get();
                   System.out.println("  Tool: " + toolName + ", Args: " + arguments);
            // Application might dispatch execution based on this
          }
        }
        ```

*   **Function Response Details:**

    === "Python"

        ```python
        responses = event.get_function_responses()
        if responses:
            for response in responses:
                tool_name = response.name
                result_dict = response.response # The dictionary returned by the tool
                print(f"  Tool Result: {tool_name} -> {result_dict}")
        ```

    === "Go"

        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
            "google.golang.org/genai"
        )

        func handleFunctionResponses(event *session.Event) {
            if event.LLMResponse == nil || event.LLMResponse.Content == nil {
                return
            }
            responses := event.Content.FunctionResponses()
            if len(responses) > 0 {
                for _, response := range responses {
                    toolName := response.Name
                    result := response.Response
                    fmt.Printf("  Tool Result: %s -> %v\n", toolName, result)
                }
            }
        }
        ```

    === "Java"

        ```java
        import com.google.genai.types.FunctionResponse;
        import com.google.common.collect.ImmutableList;
        import java.util.Map;

        ImmutableList<FunctionResponse> responses = event.functionResponses(); // from Event.java
        if (!responses.isEmpty()) {
            for (FunctionResponse response : responses) {
                String toolName = response.name().get();
                Map<String, String> result= response.response().get(); // Check before getting the response
                System.out.println("  Tool Result: " + toolName + " -> " + result);
            }
        }
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
        if event.actions and event.actions.state_delta:
            print(f"  State changes: {event.actions.state_delta}")
            # Update local UI or application state if necessary
        ```
    === "Go"
        `delta := event.Actions.StateDelta` (a `map[string]any`)
        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
        )

        func handleStateChanges(event *session.Event) {
            if len(event.Actions.StateDelta) > 0 {
                fmt.Printf("  State changes: %v\n", event.Actions.StateDelta)
                // Update local UI or application state if necessary
            }
        }
        ```

    === "Java"
        `ConcurrentMap<String, Object> delta = event.actions().stateDelta();`

        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // Assuming event.actions() is not null
        if (actions != null && actions.stateDelta() != null && !actions.stateDelta().isEmpty()) {
            ConcurrentMap<String, Object> stateChanges = actions.stateDelta();
            System.out.println("  State changes: " + stateChanges);
            // Update local UI or application state if necessary
        }
        ```

*   **Artifact Saves:** Gives you a collection indicating which artifacts were saved and their new version number (or relevant `Part` information).

    === "Python"
        `artifact_changes = event.actions.artifact_delta` (a dictionary of `{filename: version}`).
        ```python
        if event.actions and event.actions.artifact_delta:
            print(f"  Artifacts saved: {event.actions.artifact_delta}")
            # UI might refresh an artifact list
        ```

    === "Go"
        `artifactChanges := event.Actions.ArtifactDelta` (a `map[string]artifact.Artifact`)
        ```go
        import (
            "fmt"
            "google.golang.org/adk/artifact"
            "google.golang.org/adk/session"
        )

        func handleArtifactChanges(event *session.Event) {
            if len(event.Actions.ArtifactDelta) > 0 {
                fmt.Printf("  Artifacts saved: %v\n", event.Actions.ArtifactDelta)
                // UI might refresh an artifact list
                // Iterate through event.Actions.ArtifactDelta to get filename and artifact.Artifact details
                for filename, art := range event.Actions.ArtifactDelta {
                    fmt.Printf("    Filename: %s, Version: %d, MIMEType: %s\n", filename, art.Version, art.MIMEType)
                }
            }
        }
        ```

    === "Java"
        `ConcurrentMap<String, Part> artifactChanges = event.actions().artifactDelta();`

        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.genai.types.Part;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // Assuming event.actions() is not null
        if (actions != null && actions.artifactDelta() != null && !actions.artifactDelta().isEmpty()) {
            ConcurrentMap<String, Part> artifactChanges = actions.artifactDelta();
            System.out.println("  Artifacts saved: " + artifactChanges);
            // UI might refresh an artifact list
            // Iterate through artifactChanges.entrySet() to get filename and Part details
        }
        ```

*   **Control Flow Signals:** Check boolean flags or string values:

    === "Python"
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

    === "Go"
        *   `event.Actions.TransferToAgent` (string): Control should pass to the named agent.
        *   `event.Actions.Escalate` (bool): A loop should terminate.
        *   `event.Actions.SkipSummarization` (bool): A tool result should not be summarized by the LLM.
        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
        )

        func handleControlFlow(event *session.Event) {
            if event.Actions.TransferToAgent != "" {
                fmt.Printf("  Signal: Transfer to %s\n", event.Actions.TransferToAgent)
            }
            if event.Actions.Escalate {
                fmt.Println("  Signal: Escalate (terminate loop)")
            }
            if event.Actions.SkipSummarization {
                fmt.Println("  Signal: Skip summarization for tool result")
            }
        }
        ```

    === "Java"
        *   `event.actions().transferToAgent()` (returns `Optional<String>`): Control should pass to the named agent.
        *   `event.actions().escalate()` (returns `Optional<Boolean>`): A loop should terminate.
        *   `event.actions().skipSummarization()` (returns `Optional<Boolean>`): A tool result should not be summarized by the LLM.

        ```java
        import com.google.adk.events.EventActions;
        import java.util.Optional;

        EventActions actions = event.actions(); // Assuming event.actions() is not null
        if (actions != null) {
            Optional<String> transferAgent = actions.transferToAgent();
            if (transferAgent.isPresent()) {
                System.out.println("  Signal: Transfer to " + transferAgent.get());
            }

            Optional<Boolean> escalate = actions.escalate();
            if (escalate.orElse(false)) { // or escalate.isPresent() && escalate.get()
                System.out.println("  Signal: Escalate (terminate loop)");
            }

            Optional<Boolean> skipSummarization = actions.skipSummarization();
            if (skipSummarization.orElse(false)) { // or skipSummarization.isPresent() && skipSummarization.get()
                System.out.println("  Signal: Skip summarization for tool result");
            }
        }
        ```

### Determining if an Event is a "Final" Response

Use the built-in helper method `event.is_final_response()` to identify events suitable for display as the agent's complete output for a turn.

*   **Purpose:** Filters out intermediate steps (like tool calls, partial streaming text, internal state updates) from the final user-facing message(s).
*   **When `True`?**
    1.  The event contains a tool result (`function_response`) and `skip_summarization` is `True`.
    2.  The event contains a tool call (`function_call`) for a tool marked as `is_long_running=True`. In Java, check if the `longRunningToolIds` list is empty:
        *   `event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()` is `true`.
    3.  OR, **all** of the following are met:
        *   No function calls (`get_function_calls()` is empty).
        *   No function responses (`get_function_responses()` is empty).
        *   Not a partial stream chunk (`partial` is not `True`).
        *   Doesn't end with a code execution result that might need further processing/display.
*   **Usage:** Filter the event stream in your application logic.

    === "Python"
        ```python
        # Pseudocode: Handling final responses in application (Python)
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
        #         elif event.actions and event.actions.skip_summarization and event.get_function_responses():
        #              # Handle displaying the raw tool result if needed
        #              response_data = event.get_function_responses()[0].response
        #              print(f"Display raw tool result: {response_data}")
        #         elif hasattr(event, 'long_running_tool_ids') and event.long_running_tool_ids:
        #              print("Display message: Tool is running in background...")
        #         else:
        #              # Handle other types of final responses if applicable
        #              print("Display: Final non-textual response or signal.")
        ```

    === "Go"

        ```go
        // Pseudocode: Handling final responses in application (Go)
        import (
            "fmt"
            "strings"
            "google.golang.org/adk/session"
            "google.golang.org/genai"
        )

        // isFinalResponse checks if an event is a final response suitable for display.
        func isFinalResponse(event *session.Event) bool {
            if event.LLMResponse != nil {
                // Condition 1: Tool result with skip summarization.
                if event.LLMResponse.Content != nil && len(event.LLMResponse.Content.FunctionResponses()) > 0 && event.Actions.SkipSummarization {
                    return true
                }
                // Condition 2: Long-running tool call.
                if len(event.LongRunningToolIDs) > 0 {
                    return true
                }
                // Condition 3: A complete message without tool calls or responses.
                if (event.LLMResponse.Content == nil ||
                    (len(event.LLMResponse.Content.FunctionCalls()) == 0 && len(event.LLMResponse.Content.FunctionResponses()) == 0)) &&
                    !event.LLMResponse.Partial {
                    return true
                }
            }
            return false
        }

        func handleFinalResponses() {
            var fullResponseText strings.Builder
            // for event := range runner.Run(...) { // Example loop
            // 	// Accumulate streaming text if needed...
            // 	if event.LLMResponse != nil && event.LLMResponse.Partial && event.LLMResponse.Content != nil {
            // 		if len(event.LLMResponse.Content.Parts) > 0 && event.LLMResponse.Content.Parts[0].Text != "" {
            // 			fullResponseText.WriteString(event.LLMResponse.Content.Parts[0].Text)
            // 		}
            // 	}
            //
            // 	// Check if it's a final, displayable event
            // 	if isFinalResponse(event) {
            // 		fmt.Println("\n--- Final Output Detected ---")
            // 		if event.LLMResponse != nil && event.LLMResponse.Content != nil {
            // 			if len(event.LLMResponse.Content.Parts) > 0 && event.LLMResponse.Content.Parts[0].Text != "" {
            // 				// If it's the final part of a stream, use accumulated text
            // 				finalText := fullResponseText.String()
            // 				if !event.LLMResponse.Partial {
            // 					finalText += event.LLMResponse.Content.Parts[0].Text
            // 				}
            // 				fmt.Printf("Display to user: %s\n", strings.TrimSpace(finalText))
            // 				fullResponseText.Reset() // Reset accumulator
            // 			}
            // 		} else if event.Actions.SkipSummarization && event.LLMResponse.Content != nil && len(event.LLMResponse.Content.FunctionResponses()) > 0 {
            // 			// Handle displaying the raw tool result if needed
            // 			responseData := event.LLMResponse.Content.FunctionResponses()[0].Response
            // 			fmt.Printf("Display raw tool result: %v\n", responseData)
            // 		} else if len(event.LongRunningToolIDs) > 0 {
            // 			fmt.Println("Display message: Tool is running in background...")
            // 		} else {
            // 			// Handle other types of final responses if applicable
            // 			fmt.Println("Display: Final non-textual response or signal.")
            // 		}
            // 	}
            // }
        }
        ```

    === "Java"
        ```java
        // Pseudocode: Handling final responses in application (Java)
        import com.google.adk.events.Event;
        import com.google.genai.types.Content;
        import com.google.genai.types.FunctionResponse;
        import java.util.Map;

        StringBuilder fullResponseText = new StringBuilder();
        runner.run(...).forEach(event -> { // Assuming a stream of events
             // Accumulate streaming text if needed...
             if (event.partial().orElse(false) && event.content().isPresent()) {
                 event.content().flatMap(Content::parts).ifPresent(parts -> {
                     if (!parts.isEmpty() && parts.get(0).text().isPresent()) {
                         fullResponseText.append(parts.get(0).text().get());
                    }
                 });
             }

             // Check if it's a final, displayable event
             if (event.finalResponse()) { // Using the method from Event.java
                 System.out.println("\n--- Final Output Detected ---");
                 if (event.content().isPresent() &&
                     event.content().flatMap(Content::parts).map(parts -> !parts.isEmpty() && parts.get(0).text().isPresent()).orElse(false)) {
                     // If it's the final part of a stream, use accumulated text
                     String eventText = event.content().get().parts().get().get(0).text().get();
                     String finalText = fullResponseText.toString() + (event.partial().orElse(false) ? "" : eventText);
                     System.out.println("Display to user: " + finalText.trim());
                     fullResponseText.setLength(0); // Reset accumulator
                 } else if (event.actions() != null && event.actions().skipSummarization().orElse(false)
                            && !event.functionResponses().isEmpty()) {
                     // Handle displaying the raw tool result if needed,
                     // especially if finalResponse() was true due to other conditions
                     // or if you want to display skipped summarization results regardless of finalResponse()
                     Map<String, Object> responseData = event.functionResponses().get(0).response().get();
                     System.out.println("Display raw tool result: " + responseData);
                 } else if (event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()) {
                     // This case is covered by event.finalResponse()
                     System.out.println("Display message: Tool is running in background...");
                 } else {
                     // Handle other types of final responses if applicable
                     System.out.println("Display: Final non-textual response or signal.");
                 }
             }
         });
        ```

By carefully examining these aspects of an event, you can build robust applications that react appropriately to the rich information flowing through the ADK system.
