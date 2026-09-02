val searchAgent = LlmAgent(
    model = Gemini(name = "gemini-flash-latest"),
    name = "SearchAgent",
    instruction = Instruction("You're a specialist in Google Search"),
    tools = listOf(GoogleSearchTool())
)

val codingAgent = LlmAgent(
    model = Gemini(name = "gemini-flash-latest"),
    name = "CodeAgent",
    instruction = Instruction("You're a specialist in Code Execution")
    // Kotlin currently doesn't have a BuiltInCodeExecutionTool in core
)


val rootAgent = LlmAgent(
    name = "RootAgent",
    model = Gemini(name = "gemini-flash-latest"),
    description = "Root Agent",
    subAgents = listOf(searchAgent, codingAgent) // Not supported when sub-agents use built-in tools
)