package callbacks;

// --8<-- [start:init]

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.InvocationContext;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.BaseTool;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;
import com.google.common.collect.ImmutableMap;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.HashMap;
import java.util.Map;

public class BeforeToolCallbackExample {

  private static final String APP_NAME = "ToolCallbackAgentApp";
  private static final String USER_ID = "user_1";
  private static final String SESSION_ID = "session_001";
  private static final String MODEL_NAME = "gemini-2.0-flash";

  public static void main(String[] args) {
    BeforeToolCallbackExample example = new BeforeToolCallbackExample();
    example.runAgent("capital of canada");
  }

  // --- Define a Simple Tool Function ---
  // The Schema is important for the callback "args" to correctly identify the input.
  public static Map<String, Object> getCapitalCity(
      @Schema(name = "country", description = "The country to find the capital of.")
          String country) {
    System.out.printf("--- Tool 'getCapitalCity' executing with country: %s ---%n", country);
    Map<String, String> countryCapitals = new HashMap<>();
    countryCapitals.put("united states", "Washington, D.C.");
    countryCapitals.put("canada", "Ottawa");
    countryCapitals.put("france", "Paris");
    countryCapitals.put("germany", "Berlin");

    String capital =
        countryCapitals.getOrDefault(country.toLowerCase(), "Capital not found for " + country);
    // FunctionTool expects a Map<String, Object> as the return type for the method it wraps.
    return ImmutableMap.of("capital", capital);
  }

  // Define the Callback function
  // The Tool callback provides all these parameters by default.
  public Maybe<Map<String, Object>> simpleBeforeToolModifier(
      InvocationContext invocationContext,
      BaseTool tool,
      Map<String, Object> args,
      ToolContext toolContext) {

    String agentName = invocationContext.agent().name();
    String toolName = tool.name();
    System.out.printf(
        "[Callback] Before tool call for tool '%s' in agent '%s'%n", toolName, agentName);
    System.out.printf("[Callback] Original args: %s%n", args);

    if ("getCapitalCity".equals(toolName)) {
      String countryArg = (String) args.get("country");
      if (countryArg != null) {
        if ("canada".equalsIgnoreCase(countryArg)) {
          System.out.println("[Callback] Detected 'Canada'. Modifying args to 'France'.");
          args.put("country", "France");
          System.out.printf("[Callback] Modified args: %s%n", args);
          // Proceed with modified args
          return Maybe.empty();
        } else if ("BLOCK".equalsIgnoreCase(countryArg)) {
          System.out.println("[Callback] Detected 'BLOCK'. Skipping tool execution.");
          // Return a map to skip the tool call and use this as the result
          return Maybe.just(
              ImmutableMap.of("result", "Tool execution was blocked by before_tool_callback."));
        }
      }
    }

    System.out.println("[Callback] Proceeding with original or previously modified args.");
    return Maybe.empty();
  }

  public void runAgent(String query) {
    // --- Wrap the function into a Tool ---
    FunctionTool capitalTool = FunctionTool.create(this.getClass(), "getCapitalCity");

    // Create LlmAgent and Assign Callback
    LlmAgent myLlmAgent =
        LlmAgent.builder()
            .name(APP_NAME)
            .model(MODEL_NAME)
            .instruction(
                "You are an agent that can find capital cities. Use the getCapitalCity tool.")
            .description("An LLM agent demonstrating before_tool_callback")
            .tools(capitalTool)
            .beforeToolCallback(this::simpleBeforeToolModifier)
            .build();

    // Session and Runner
    InMemoryRunner runner = new InMemoryRunner(myLlmAgent);
    Session session =
        runner.sessionService().createSession(APP_NAME, USER_ID, null, SESSION_ID).blockingGet();

    Content userMessage = Content.fromParts(Part.fromText(query));

    System.out.printf("%n--- Calling agent with query: \"%s\" ---%n", query);
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
