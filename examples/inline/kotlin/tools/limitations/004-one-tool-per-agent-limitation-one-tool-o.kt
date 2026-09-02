val searchAgent = LlmAgent(
    name = "SearchAgent",
    model = Gemini(name = "gemini-flash-latest"),
    instruction = Instruction("You're a specialist in Google Search"),
    tools = listOf(GoogleSearchTool(), YourCustomTool()) // <-- NOT supported
)