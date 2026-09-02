from adk_perseus_context import perseus_before_model_callback
from google.adk.agents import Agent

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Help the user.",
    before_model_callback=perseus_before_model_callback("context.perseus"),
)