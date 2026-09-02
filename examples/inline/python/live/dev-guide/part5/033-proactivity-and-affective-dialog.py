from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode

# Configure for empathetic customer service
run_config = RunConfig(
    response_modalities=["AUDIO"],
    streaming_mode=StreamingMode.BIDI,

    # Model can proactively offer help
    proactivity=types.ProactivityConfig(proactive_audio=True),

    # Model adapts to customer emotions
    enable_affective_dialog=True
)

# Example interaction (illustrative - actual model behavior may vary):
# Customer: "I've been waiting for my order for three weeks..."
# [Model may detect frustration in tone and adapt response]
# Model: "I'm really sorry to hear about this delay. Let me check your order
#        status right away. Can you provide your order number?"
#
# [Proactivity in action]
# Model: "I see you previously asked about shipping updates. Would you like
#        me to set up notifications for future orders?"
#
# Note: Proactive and affective behaviors are probabilistic. The model's
# emotional awareness and proactive suggestions will vary based on context,
# conversation history, and inherent model variability.