# Create Agent Runtime with Gen AI SDK
client = vertexai.Client(
  api_key="YOUR_API_KEY",
)

agent_engine = client.agent_engines.create(
  config={
    "display_name": "Demo Agent Runtime",
    "description": "Agent Runtime for Session and Memory",
  })