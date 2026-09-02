from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

remote_agent = RemoteA2aAgent(
    name="remote_agent",
    agent_card="http://localhost:8000/a2a/remote_agent/.well-known/agent-card.json",
    use_legacy=False,
)