from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard

# Define A2A agent card
my_agent_card = AgentCard(
    name="file_agent",
    url="http://example.com",
    description="Test agent from file",
    version="1.0.0",
    capabilities={},
    skills=[],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    supports_authenticated_extended_card=False,
)
a2a_app = to_a2a(root_agent, port=8001, agent_card=my_agent_card)