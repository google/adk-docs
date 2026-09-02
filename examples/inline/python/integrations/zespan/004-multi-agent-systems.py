handler = ZespanADKCallbackHandler()

specialist = LlmAgent(
    name="lookup_agent",
    model="gemini-flash-latest",
    tools=[lookup_tool],
    **handler.callbacks,
)

coordinator = LlmAgent(
    name="coordinator",
    model="gemini-flash-latest",
    sub_agents=[specialist],
    **handler.callbacks,
)