root_agent = Agent(
    name="RootAgent",
    model="gemini-flash-latest",
    description="Code Agent",
    tools=[custom_function],
    code_executor=BuiltInCodeExecutor() # <-- NOT supported when used with tools
)