// Define a tool function
// Retrieves the capital city of a given country.
public static Map<String, Object> getCapitalCity(
        @Schema(name = "country", description = "The country to get capital for")
        String country) {
  // Replace with actual logic (e.g., API call, database lookup)
  Map<String, String> countryCapitals = new HashMap<>();
  countryCapitals.put("canada", "Ottawa");
  countryCapitals.put("france", "Paris");
  countryCapitals.put("japan", "Tokyo");

  String result =
          countryCapitals.getOrDefault(
                  country.toLowerCase(), "Sorry, I couldn't find the capital for " + country + ".");
  return Map.of("result", result); // Tools must return a Map
}

// Add the tool to the agent
FunctionTool capitalTool = FunctionTool.create(experiment.getClass(), "getCapitalCity");
LlmAgent capitalAgent =
    LlmAgent.builder()
        .model("gemini-flash-latest")
        .name("capital_agent")
        .description("Answers user questions about the capital city of a given country.")
        .instruction("You are an agent that provides the capital city of a country... (previous instruction text)")
        .tools(capitalTool) // Provide the function wrapped as a FunctionTool
        .build();