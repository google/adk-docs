from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    # Model can initiate responses without explicit prompts
    proactivity=types.ProactivityConfig(proactive_audio=True),

    # Model adapts to user emotions
    enable_affective_dialog=True
)