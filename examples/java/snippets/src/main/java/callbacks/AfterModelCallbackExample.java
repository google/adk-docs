package callbacks;

// --8<-- [start:init]

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.CallbackContext;
import com.google.adk.events.Event;
import com.google.adk.models.LlmResponse;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class AfterModelCallbackExample {

  // --- Define Constants ---
  private static final String AGENT_NAME = "AfterModelCallbackAgent";
  private static final String MODEL_NAME = "gemini-2.0-flash";
  private static final String AGENT_INSTRUCTION = "You are a helpful assistant.";
  private static final String AGENT_DESCRIPTION = "An LLM agent demonstrating after_model_callback";

  // For session and runner
  private static final String APP_NAME = "AfterModelCallbackAgentApp";
  private static final String USER_ID = "user_1";

  // For text replacement
  private static final String SEARCH_TERM = "joke";
  private static final String REPLACE_TERM = "funny story";
  private static final Pattern SEARCH_PATTERN =
      Pattern.compile("\\b" + Pattern.quote(SEARCH_TERM) + "\\b", Pattern.CASE_INSENSITIVE);

  public static void main(String[] args) {
    AfterModelCallbackExample example = new AfterModelCallbackExample();
    example.defineAgentAndRun();
  }

  // --- Define the Callback Function ---
  // Inspects/modifies the LLM response after it's received.
  public Maybe<LlmResponse> simpleAfterModelModifier(
      CallbackContext callbackContext, LlmResponse llmResponse) {
    String agentName = callbackContext.agentName();
    System.out.printf("%n[Callback] After model call for agent: %s%n", agentName);

    // --- Inspection Phase ---
    if (llmResponse.errorMessage().isPresent()) {
      System.out.printf(
          "[Callback] Response has error: '%s'. No modification.%n",
          llmResponse.errorMessage().get());
      return Maybe.empty(); // Pass through errors
    }

    Optional<Part> firstTextPartOpt =
        llmResponse
            .content()
            .flatMap(Content::parts)
            .filter(parts -> !parts.isEmpty() && parts.get(0).text().isPresent())
            .map(parts -> parts.get(0));

    if (!firstTextPartOpt.isPresent()) {
      // Could be a function call, empty content, or no text in the first part
      llmResponse
          .content()
          .flatMap(Content::parts)
          .filter(parts -> !parts.isEmpty() && parts.get(0).functionCall().isPresent())
          .ifPresent(
              parts ->
                  System.out.printf(
                      "[Callback] Response is a function call ('%s'). No text modification.%n",
                      parts.get(0).functionCall().get().name().orElse("N/A")));
      if (!llmResponse.content().isPresent()
          || !llmResponse.content().flatMap(Content::parts).isPresent()
          || llmResponse.content().flatMap(Content::parts).get().isEmpty()) {
        System.out.println(
            "[Callback] Response content is empty or has no parts. No modification.");
      } else if (!firstTextPartOpt.isPresent()) { // Already checked for function call
        System.out.println("[Callback] First part has no text content. No modification.");
      }
      return Maybe.empty(); // Pass through non-text or unsuitable responses
    }

    String originalText = firstTextPartOpt.get().text().get();
    System.out.printf("[Callback] Inspected original text: '%.100s...'%n", originalText);

    // --- Modification Phase ---
    Matcher matcher = SEARCH_PATTERN.matcher(originalText);
    if (!matcher.find()) {
      System.out.printf(
          "[Callback] '%s' not found. Passing original response through.%n", SEARCH_TERM);
      return Maybe.empty();
    }

    System.out.printf("[Callback] Found '%s'. Modifying response.%n", SEARCH_TERM);

    // Perform the replacement, respecting original capitalization of the found term's first letter
    String foundTerm = matcher.group(0); // The actual term found (e.g., "joke" or "Joke")
    String actualReplaceTerm = REPLACE_TERM;
    if (Character.isUpperCase(foundTerm.charAt(0)) && REPLACE_TERM.length() > 0) {
      actualReplaceTerm = Character.toUpperCase(REPLACE_TERM.charAt(0)) + REPLACE_TERM.substring(1);
    }
    String modifiedText = matcher.replaceFirst(Matcher.quoteReplacement(actualReplaceTerm));

    // Create a new LlmResponse with the modified content
    Content originalContent = llmResponse.content().get();
    List<Part> originalParts = originalContent.parts().orElse(ImmutableList.of());

    List<Part> modifiedPartsList = new ArrayList<>(originalParts.size());
    if (!originalParts.isEmpty()) {
      modifiedPartsList.add(Part.fromText(modifiedText)); // Replace first part's text
      // Add remaining parts as they were (shallow copy)
      for (int i = 1; i < originalParts.size(); i++) {
        modifiedPartsList.add(originalParts.get(i));
      }
    } else { // Should not happen if firstTextPartOpt was present
      modifiedPartsList.add(Part.fromText(modifiedText));
    }

    LlmResponse.Builder newResponseBuilder =
        LlmResponse.builder()
            .content(
                originalContent.toBuilder().parts(ImmutableList.copyOf(modifiedPartsList)).build())
            .groundingMetadata(llmResponse.groundingMetadata());

    System.out.println("[Callback] Returning modified response.");
    return Maybe.just(newResponseBuilder.build());
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
            .afterModelCallback(this::simpleAfterModelModifier)
            .build();

    // Create an InMemoryRunner
    InMemoryRunner runner = new InMemoryRunner(myLlmAgent, APP_NAME);
    // InMemoryRunner automatically creates a session service. Create a session using the service
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();
    Content userMessage =
        Content.fromParts(
            Part.fromText(
                "Tell me a joke about quantum computing. Include the word 'joke' in your response"));

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
