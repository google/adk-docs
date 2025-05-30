package agents.capitalagent;

// --8<-- [start:full_code]

import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import java.util.HashMap;
import java.util.Map;

public class CapitalAgent {

  // --- Define Constants ---
  private static final String MODEL_NAME = "gemini-2.0-flash";

  // The Agent should be exposed as a "public static" argument.
  public static BaseAgent ROOT_AGENT = initAgent();

  // Initialize the Agent in a static class method.
  public static BaseAgent initAgent() {
    FunctionTool capitalTool = FunctionTool.create(CapitalAgent.class, "getCapitalCity");

    return LlmAgent.builder()
        .model(MODEL_NAME)
        .name("CapitalAgent")
        .description("Retrieves the capital city using a specific tool.")
        .instruction(
            """
                You are a helpful agent that provides the capital city of a country using a tool.
                1. Extract the country name.
                2. Use the `getCapitalCity` tool to find the capital.
                3. Respond clearly to the user, stating the capital city found by the tool.
                """)
        .tools(capitalTool)
        .outputKey("capital_tool_result") // Store final text response
        .build();
  }

  // --- Define the Tool ---
  // Retrieves the capital city of a given country.
  public static Map<String, Object> getCapitalCity(
      @Schema(name = "country", description = "The country to get capital for") String country) {
    System.out.printf("%n-- Tool Call: getCapitalCity(country='%s') --%n", country);
    Map<String, String> countryCapitals = new HashMap<>();
    countryCapitals.put("united states", "Washington, D.C.");
    countryCapitals.put("canada", "Ottawa");
    countryCapitals.put("france", "Paris");
    countryCapitals.put("japan", "Tokyo");

    String result =
        countryCapitals.getOrDefault(
            country.toLowerCase(), "Sorry, I couldn't find the capital for " + country + ".");
    System.out.printf("-- Tool Result: '%s' --%n", result);
    return Map.of("result", result); // Tools must return a Map
  }
}
// --8<-- [end:full_code]