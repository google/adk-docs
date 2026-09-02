<...code truncated...>

from google.adk.a2a.agent import A2aRemoteAgentConfig
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

prime_agent = RemoteA2aAgent(
    name="prime_agent",
    description="Agent that handles checking if numbers are prime.",
    agent_card=(
        f"http://localhost:8001/a2a/check_prime_agent{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
    use_legacy=False,
    config=A2aRemoteAgentConfig(
        a2a_message_converter=my_a2a_message_converter,
        request_interceptors=[my_request_interceptor],
    ),
)

<...code truncated>