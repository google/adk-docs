from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Load A2A agent card from a file
a2a_app = to_a2a(root_agent, port=8001, agent_card="/path/to/your/agent-card.json")