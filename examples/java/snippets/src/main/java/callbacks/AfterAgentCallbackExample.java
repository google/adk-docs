package callbacks;

// --8<-- [start:init]

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.CallbackContext;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.State;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class AfterAgentCallbackExample {

  // --- Constants ---
  private static final String APP_NAME = "after_agent_demo";
  private static final String USER_ID = "test_user_after";
  private static final String SESSION_ID_NORMAL = "session_run_normally";
  private static final String SESSION_ID_MODIFY = "session_modify_output";
  private static final String MODEL_NAME = "gemini-2.0-flash";

  public static void main(String[] args) {
    AfterAgentCallbackExample demo = new AfterAgentCallbackExample();
    demo.defineAgentAndRunScenarios();
  }

  // --- 1. Define the Callback Function ---
  /**
   * Log exit from an agent and checks 'add_concluding_note' in session state. If True, returns new
   * Content to *replace* the agent's original output. If False or not present, returns
   * Maybe.empty(), allowing the agent's original output to be used.
   */
  public Maybe<Content> modifyOutputAfterAgent(CallbackContext callbackContext) {
    String agentName = callbackContext.agentName();
    String invocationId = callbackContext.invocationId();
    State currentState = callbackContext.state();

    System.out.printf("%n[Callback] Exiting agent: %s (Inv: %s)%n", agentName, invocationId);
    System.out.printf("[Callback] Current State: %s%n", currentState.entrySet());

    Object addNoteFlag = currentState.get("add_concluding_note");

    // Example: Check state to decide whether to modify the final output
    if (Boolean.TRUE.equals(addNoteFlag)) {
      System.out.printf(
          "[Callback] State condition 'add_concluding_note=True' met: Replacing agent %s's"
              + " output.%n",
          agentName);

      // Return Content to *replace* the agent's own output
      return Maybe.just(
          Content.builder()
              .parts(
                  List.of(
                      Part.fromText(
                          "Concluding note added by after_agent_callback, replacing original output.")))
              .role("model") // Assign model role to the overriding response
              .build());

    } else {
      System.out.printf(
          "[Callback] State condition not met: Using agent %s's original output.%n", agentName);
      // Return None - the agent's output produced just before this callback will be used.
      return Maybe.empty();
    }
  }

  // --- 2. Setup Agent with Callback ---
  public void defineAgentAndRunScenarios() {
    LlmAgent llmAgentWithAfterCb =
        LlmAgent.builder()
            .name(APP_NAME)
            .model(MODEL_NAME)
            .description("An LLM agent demonstrating after_agent_callback for output modification")
            .instruction("You are a simple agent. Just say 'Processing complete!'")
            .afterAgentCallback(this::modifyOutputAfterAgent) // Assign the callback here
            .build();

    // --- 3. Setup Runner and Sessions using InMemoryRunner ---
    // Use InMemoryRunner - it includes InMemorySessionService
    InMemoryRunner runner = new InMemoryRunner(llmAgentWithAfterCb, APP_NAME);

    // --- Scenario 1: Run where callback allows agent's original output ---
    System.out.printf(
        "%n%s SCENARIO 1: Running Agent (Should Use Original Output) %s%n",
        "=".repeat(20), "=".repeat(20));
    // No initial state means 'add_concluding_note' will be false in the callback check
    runScenario(
        runner,
        llmAgentWithAfterCb.name(), // Use agent name for runner's appName consistency
        SESSION_ID_NORMAL,
        null,
        "Process this please.");

    // --- Scenario 2: Run where callback replaces the agent's output ---
    System.out.printf(
        "%n%s SCENARIO 2: Running Agent (Should Replace Output) %s%n",
        "=".repeat(20), "=".repeat(20));
    Map<String, Object> modifyState = new HashMap<>();
    modifyState.put("add_concluding_note", true); // Set the state flag here
    runScenario(
        runner,
        llmAgentWithAfterCb.name(), // Use agent name for runner's appName consistency
        SESSION_ID_MODIFY,
        new ConcurrentHashMap<>(modifyState),
        "Process this and add note.");
  }

  // --- 3. Method to Run a Single Scenario ---
  public void runScenario(
      InMemoryRunner runner,
      String appName,
      String sessionId,
      ConcurrentHashMap<String, Object> initialState,
      String userQuery) {

    // Create session using the runner's bundled session service
    runner.sessionService().createSession(appName, USER_ID, initialState, sessionId).blockingGet();

    System.out.printf(
        "Running scenario for session: %s, initial state: %s%n", sessionId, initialState);
    Content userMessage =
        Content.builder().role("user").parts(List.of(Part.fromText(userQuery))).build();

    Flowable<Event> eventStream = runner.runAsync(USER_ID, sessionId, userMessage);

    // Print final output
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse() && event.content().isPresent()) {
            String author = event.author() != null ? event.author() : "UNKNOWN";
            String text =
                event
                    .content()
                    .flatMap(Content::parts)
                    .filter(parts -> !parts.isEmpty())
                    .map(parts -> parts.get(0).text().orElse("").trim())
                    .orElse("[No text in final response]");
            System.out.printf("Final Output for %s: [%s] %s%n", sessionId, author, text);
          } else if (event.errorCode().isPresent()) {
            System.out.printf(
                "Error Event for %s: %s%n",
                sessionId, event.errorMessage().orElse("Unknown error"));
          }
        });
  }
}
// --8<-- [end:init]
