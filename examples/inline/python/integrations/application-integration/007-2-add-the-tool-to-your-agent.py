    from google.adk.agents.llm_agent import LlmAgent
    from .tools import integration_tool, connector_tool

    root_agent = LlmAgent(
        model='gemini-flash-latest',
        name='integration_agent',
        instruction="Help user, leverage the tools you have access to",
        tools=[integration_tool],
    )