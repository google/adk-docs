package callbacks;

// --8<-- [start:init]

import com.google.adk.agents.CallbackContext;
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.models.LlmRequest;
import com.google.adk.models.LlmResponse;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.genai.types.Content;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class BeforeModelGuardrailExample {

  private static final String MODEL_ID = "gemini-2.0-flash";
  private static final String APP_NAME = "guardrail_app";
  private static final String USER_ID = "user_1";

  public static void main(String[] args) {
    BeforeModelGuardrailExample example = new BeforeModelGuardrailExample();
    example.defineAgentAndRun("Tell me about quantum computing. This is a test.");
  }

  // --- Define your callback logic ---
  // Looks for the word "BLOCK" in the user prompt and blocks the call to LLM if found.
  // Otherwise the LLM call proceeds as usual.
  public Optional<LlmResponse> simpleBeforeModelModifier(
      CallbackContext callbackContext, LlmRequest llmRequest) {
    System.out.println("[Callback] Before model call for agent: " + callbackContext.agentName());

    // Inspect the last user message in the request contents
    String lastUserMessageText = "";
    List<Content> requestContents = llmRequest.contents();
    if (requestContents != null && !requestContents.isEmpty()) {
      Content lastContent = requestContents.get(requestContents.size() - 1);
      if (lastContent.role().isPresent() && "user".equals(lastContent.role().get())) {
        lastUserMessageText =
            lastContent.parts().orElse(List.of()).stream()
                .flatMap(part -> part.text().stream())
                .collect(Collectors.joining(" ")); // Concatenate text from all parts
      }
    }
    System.out.println("[Callback] Inspecting last user message: '" + lastUserMessageText + "'");

    String prefix = "[Modified by Callback] ";
    GenerateContentConfig currentConfig =
        llmRequest.config().orElse(GenerateContentConfig.builder().build());
    Optional<Content> optOriginalSystemInstruction = currentConfig.systemInstruction();

    Content conceptualModifiedSystemInstruction;
    if (optOriginalSystemInstruction.isPresent()) {
      Content originalSystemInstruction = optOriginalSystemInstruction.get();
      List<Part> originalParts =
          new ArrayList<>(originalSystemInstruction.parts().orElse(List.of()));
      String originalText = "";

      if (!originalParts.isEmpty()) {
        Part firstPart = originalParts.get(0);
        if (firstPart.text().isPresent()) {
          originalText = firstPart.text().get();
        }
        originalParts.set(0, Part.fromText(prefix + originalText));
      } else {
        originalParts.add(Part.fromText(prefix));
      }
      conceptualModifiedSystemInstruction =
          originalSystemInstruction.toBuilder().parts(originalParts).build();
    } else {
      conceptualModifiedSystemInstruction =
          Content.builder()
              .role("system")
              .parts(List.of(Part.fromText(prefix)))
              .build();
    }

    // This demonstrates building a new LlmRequest with the modified config.
    llmRequest =
        llmRequest.toBuilder()
            .config(
                currentConfig.toBuilder()
                    .systemInstruction(conceptualModifiedSystemInstruction)
                    .build())
            .build();

    System.out.println(
        "[Callback] Conceptually modified system instruction is: '"
            + llmRequest.config().get().systemInstruction().get().parts().get().get(0).text().get());

    // --- Skip Example ---
    // Check if the last user message contains "BLOCK"
    if (lastUserMessageText.toUpperCase().contains("BLOCK")) {
      System.out.println("[Callback] 'BLOCK' keyword found. Skipping LLM call.");
      LlmResponse skipResponse =
          LlmResponse.builder()
              .content(
                  Content.builder()
                      .role("model")
                      .parts(
                          List.of(
                              Part.builder()
                                  .text("LLM call was blocked by before_model_callback.")
                                  .build()))
                      .build())
              .build();
      return Optional.of(skipResponse);
    }
    System.out.println("[Callback] Proceeding with LLM call.");
    // Return Optional.empty() to allow the (modified) request to go to the LLM
    return Optional.empty();
  }

  public void defineAgentAndRun(String prompt) {
    // --- Create LlmAgent and Assign Callback ---
    LlmAgent myLlmAgent =
        LlmAgent.builder()
            .name("ModelCallbackAgent")
            .model(MODEL_ID)
            .instruction("You are a helpful assistant.") // Base instruction
            .description("An LLM agent demonstrating before_model_callback")
            .beforeModelCallbackSync(this::simpleBeforeModelModifier) // Assign the callback here
            .build();

    // Session and Runner
    InMemoryRunner runner = new InMemoryRunner(myLlmAgent, APP_NAME);
    // InMemoryRunner automatically creates a session service. Create a session using the service
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();
    Content userMessage =
        Content.fromParts(Part.fromText(prompt));

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
