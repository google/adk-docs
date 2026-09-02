from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- Example Agent using Meta's Llama 4 Scout ---
agent_llama_vertexai = LlmAgent(
    model=LiteLlm(model="vertex_ai/meta/llama-4-scout-17b-16e-instruct-maas"), # LiteLLM model string format
    name="llama4_agent",
    instruction="You are a helpful assistant powered by Llama 4 Scout.",
    # ... other agent parameters
)