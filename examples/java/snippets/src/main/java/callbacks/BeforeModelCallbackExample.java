package callbacks;

// --8<-- [start:init]

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.CallbackContext;
import com.google.adk.events.Event;
import com.google.adk.models.LlmRequest;
import com.google.adk.models.LlmResponse;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterables;
import com.google.genai.types.Content;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.ArrayList;
import java.util.List;

public class BeforeModelCallbackExample {

  // --- Define Constants ---
  private static final String AGENT_NAME = "ModelCallbackAgent";
  private static final String MODEL_NAME = "gemini-2.0-flash";
  private static final String AGENT_INSTRUCTION = "You are a helpful assistant.";
  private static final String AGENT_DESCRIPTION =
      "An LLM agent demonstrating before_model_callback";

  // For session and runner
  private static final String APP_NAME = "guardrail_app_java";
  private static final String USER_ID = "user_1_java";

  public static void main(String[] args) {
    BeforeModelCallbackExample demo = new BeforeModelCallbackExample();
    demo.defineAgentAndRun();
  }

  // --- 1. Define the Callback Function ---
  // Inspects/modifies the LLM request or skips the actual LLM call.
  public Maybe<LlmResponse> simpleBeforeModelModifier(
      CallbackContext callbackContext, LlmRequest llmRequest) {
    String agentName = callbackContext.agentName();
    System.out.printf("%n[Callback] Before model call for agent: %s%n", agentName);
    
    String lastUserMessage = "";
    if (llmRequest.contents() != null && !llmRequest.contents().isEmpty()) {
      Content lastContentItem = Iterables.getLast(llmRequest.contents());
      if ("user".equals(lastContentItem.role().orElse(null))
          && lastContentItem.parts().isPresent()
          && !lastContentItem.parts().get().isEmpty()) {
        lastUserMessage = lastContentItem.parts().get().get(0).text().orElse("");
      }
    }
    System.out.printf("[Callback] Inspecting last user message: '%s'%n", lastUserMessage);

    // --- Modification Example ---
    // Add a prefix to the system instruction
    Content systemInstructionFromRequest = Content.builder().parts(ImmutableList.of()).build();
    // Ensure system_instruction is Content and parts list exists
    if (llmRequest.config().isPresent()) {
      systemInstructionFromRequest =
          llmRequest
              .config()
              .get()
              .systemInstruction()
              .orElseGet(() -> Content.builder().role("system").parts(ImmutableList.of()).build());
    }
    List<Part> currentSystemParts =
        new ArrayList<>(systemInstructionFromRequest.parts().orElse(ImmutableList.of()));
    // Ensure a part exists for modification
    if (currentSystemParts.isEmpty()) {
      currentSystemParts.add(Part.fromText(""));
    }
    // Modify the text of the first part
    String prefix = "[Modified by Callback] ";
    String conceptuallyModifiedText = prefix + currentSystemParts.get(0).text().orElse("");
    llmRequest =
        llmRequest.toBuilder()
            .config(
                GenerateContentConfig.builder()
                    .systemInstruction(
                        Content.builder()
                            .parts(List.of(Part.fromText(conceptuallyModifiedText)))
                            .build())
                    .build())
            .build();
    System.out.printf(
        "Modified System Instruction %s", llmRequest.config().get().systemInstruction());

    // --- Skip Example ---
    // Check if the last user message contains "BLOCK"
    if (lastUserMessage.toUpperCase().contains("BLOCK")) {
      System.out.println("[Callback] 'BLOCK' keyword found. Skipping LLM call.");
      // Return an LlmResponse to skip the actual LLM call
      return Maybe.just(
          LlmResponse.builder()
              .content(
                  Content.builder()
                      .role("model")
                      .parts(
                          ImmutableList.of(
                              Part.fromText("LLM call was blocked by before_model_callback.")))
                      .build())
              .build());
    }

    // Return Empty response to allow the (modified) request to go to the LLM
    System.out.println("[Callback] Proceeding with LLM call (using the original LlmRequest).");
    return Maybe.empty();
  }

  // --- 2. Define Agent and Run Scenarios ---
  public void defineAgentAndRun() {
    // Setup Agent with Callback
    LlmAgent myLlmAgent =
        LlmAgent.builder()
            .name(AGENT_NAME)
            .model(MODEL_NAME)
            .instruction(AGENT_INSTRUCTION)
            .description(AGENT_DESCRIPTION)
            .beforeModelCallback(this::simpleBeforeModelModifier)
            .build();

    // Create an InMemoryRunner
    InMemoryRunner runner = new InMemoryRunner(myLlmAgent, APP_NAME);
    // InMemoryRunner automatically creates a session service. Create a session using the service
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();
    Content userMessage =
        Content.fromParts(
            Part.fromText("Tell me about quantum computing. This is a test. So BLOCK."));

    // Run the agent
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    // Stream event response
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
// --8<-- [end:init]
