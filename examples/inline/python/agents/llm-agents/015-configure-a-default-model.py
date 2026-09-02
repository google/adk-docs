from google.adk.agents import LlmAgent

# Set a new default model for all agents
LlmAgent.set_default_model("gemini-flash-latest")

# This agent will now use "gemini-flash-latest" by default
agent_with_default_model = LlmAgent(
    name="default_model_agent",
    instruction="You are a helpful assistant."
)

# You can still override the default for specific agents
specific_agent = LlmAgent(
    name="specific_model_agent",
    model="gemini-pro-latest",
    instruction="You are a creative writer."
)