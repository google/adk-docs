LlmAgent searchAgent =
    LlmAgent.builder()
        .model("gemini-flash-latest")
        .name("SearchAgent")
        .instruction("You're a specialist in Google Search")
        .tools(new GoogleSearchTool())
        .build();

LlmAgent codingAgent =
    LlmAgent.builder()
        .model("gemini-flash-latest")
        .name("CodeAgent")
        .instruction("You're a specialist in Code Execution")
        .tools(new BuiltInCodeExecutionTool())
        .build();


LlmAgent rootAgent =
    LlmAgent.builder()
        .name("RootAgent")
        .model("gemini-flash-latest")
        .description("Root Agent")
        .subAgents(searchAgent, codingAgent) // Not supported, as the sub agents use built in tools.
        .build();