from vertexai.agent_engines import AdkApp

adk_app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)