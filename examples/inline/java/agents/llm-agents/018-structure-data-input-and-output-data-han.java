private static final Schema CAPITAL_OUTPUT =
    Schema.builder()
        .type("OBJECT")
        .description("Schema for capital city information.")
        .properties(
            Map.of(
                "capital",
                Schema.builder()
                    .type("STRING")
                    .description("The capital city of the country.")
                    .build()))
        .build();

LlmAgent structuredCapitalAgent =
    LlmAgent.builder()
        // ... name, model, description
        .instruction(
                "You are a Capital Information Agent. Given a country, respond ONLY with a JSON object containing the capital. Format: {\"capital\": \"capital_name\"}")
        .outputSchema(CAPITAL_OUTPUT) // Enforce JSON output
        .outputKey("found_capital") // Store result in state.get("found_capital")
        // Cannot use tools(getCapitalCity) effectively here
        .build();