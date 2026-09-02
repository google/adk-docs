// Example: Defining the basic identity
LlmAgent capitalAgent =
    LlmAgent.builder()
        .model("gemini-flash-latest")
        .name("capital_agent")
        .description("Answers user questions about the capital city of a given country.")
        // instruction and tools will be added next
        .build();