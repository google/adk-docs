url_context_agent = Agent(
    model='gemini-flash-latest',
    name='UrlContextAgent',
    instruction="""
    You're a specialist in URL Context
    """,
    tools=[url_context],
)
coding_agent = Agent(
    model='gemini-flash-latest',
    name='CodeAgent',
    instruction="""
    You're a specialist in Code Execution
    """,
    code_executor=BuiltInCodeExecutor(),
)
root_agent = Agent(
    name="RootAgent",
    model="gemini-flash-latest",
    description="Root Agent",
    sub_agents=[
        url_context_agent,
        coding_agent
    ],
)