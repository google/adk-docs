from google.adk.agents import LlmAgent
from aidefense_google_adk import make_aidefense_callbacks

cbs = make_aidefense_callbacks(mode="enforce")

agent = LlmAgent(
    model="gemini-flash-latest",
    name="assistant",
    instruction="You are a helpful assistant.",
)
cbs.apply_to(agent)  # wires all 4 callbacks