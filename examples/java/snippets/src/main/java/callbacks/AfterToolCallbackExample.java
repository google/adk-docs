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

public class AfterToolCallbackExample {

  private static final String APP_NAME = "AfterToolCallbackAgentApp";
  private static final String USER_ID = "user_1";
  private static final String SESSION_ID = "session_001";
  private static final String MODEL_NAME = "gemini-2.0-flash";

  public static void main(String[] args) {
    AfterToolCallbackExample example = new AfterToolCallbackExample();
    example.runAgent("What is the capital of the United States?");
  }

  // --- Define a Simple Tool Function (Same as before) ---
  @Schema(description = "Retrieves the capital city of a given country.")
  public static Map<String, Object> getCapitalCity(
      @Schema(description = "The country to find the capital of.") String country) {
    System.out.printf("--- Tool 'getCapitalCity' executing with country: %s ---%n", country);
    Map<String, String> countryCapitals = new HashMap<>();
    countryCapitals.put("united states", "Washington, D.C.");
    countryCapitals.put("canada", "Ottawa");
    countryCapitals.put("france", "Paris");
    countryCapitals.put("germany", "Berlin");

    String capital =
        countryCapitals.getOrDefault(country.toLowerCase(), "Capital not found for " + country);
    return ImmutableMap.of("result", capital);
  }

  // Define the Callback function.
  public Maybe<Map<String, Object>> simpleAfterToolModifier(
      InvocationContext invocationContext,
      BaseTool tool,
      Map<String, Object> args,
      ToolContext toolContext,
      Object toolResponse) {

    // Inspects/modifies the tool result after execution.
    String agentName = invocationContext.agent().name();
    String toolName = tool.name();
    System.out.printf(
        "[Callback] After tool call for tool '%s' in agent '%s'%n", toolName, agentName);
    System.out.printf("[Callback] Args used: %s%n", args);
    System.out.printf("[Callback] Original tool_response: %s%n", toolResponse);

    if (!(toolResponse instanceof Map)) {
      System.out.println("[Callback] toolResponse is not a Map, cannot process further.");
      // Pass through if not a map
      return Maybe.empty();
    }

    // Default structure for function tool results is {"result": <return_value>}
    @SuppressWarnings("unchecked")
    Map<String, Object> responseMap = (Map<String, Object>) toolResponse;
    Object originalResultValue = responseMap.get("result");

    // --- Modification Example ---
    // If the tool was 'get_capital_city' and result is 'Washington, D.C.'
    if ("getCapitalCity".equals(toolName) && "Washington, D.C.".equals(originalResultValue)) {
      System.out.println("[Callback] Detected 'Washington, D.C.'. Modifying tool response.");

      // IMPORTANT: Create a new mutable map or modify a copy
      Map<String, Object> modifiedResponse = new HashMap<>(responseMap);
      modifiedResponse.put(
          "result", originalResultValue + " (Note: This is the capital of the USA).");
      modifiedResponse.put("note_added_by_callback", true); // Add extra info if needed

      System.out.printf("[Callback] Modified tool_response: %s%n", modifiedResponse);
      return Maybe.just(modifiedResponse);
    }

    System.out.println("[Callback] Passing original tool response through.");
    // Return Maybe.empty() to use the original tool_response
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
                "You are an agent that finds capital cities using the getCapitalCity tool. Report"
                    + " the result clearly.")
            .description("An LLM agent demonstrating after_tool_callback")
            .tools(capitalTool) // Add the tool
            .afterToolCallback(this::simpleAfterToolModifier) // Assign the callback
            .build();

    InMemoryRunner runner = new InMemoryRunner(myLlmAgent);

    // Session and Runner
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
