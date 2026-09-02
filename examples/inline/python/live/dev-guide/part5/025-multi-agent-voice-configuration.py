from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.agents.run_config import RunConfig

# Customer service agent with a friendly voice
customer_service_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Aoede"  # Friendly, warm voice
            )
        )
    )
)

customer_service_agent = Agent(
    name="customer_service",
    model=customer_service_llm,
    instruction="You are a friendly customer service representative."
)

# Technical support agent with a professional voice
technical_support_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Charon"  # Professional, authoritative voice
            )
        )
    )
)

technical_support_agent = Agent(
    name="technical_support",
    model=technical_support_llm,
    instruction="You are a technical support specialist."
)

# Root agent that coordinates the workflow
root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    instruction="Coordinate customer service and technical support.",
    sub_agents=[customer_service_agent, technical_support_agent]
)

# RunConfig without speech_config - each agent uses its own voice
run_config = RunConfig(
    response_modalities=["AUDIO"]
)