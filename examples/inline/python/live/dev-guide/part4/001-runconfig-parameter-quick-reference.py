from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode

# Configuration types are accessed via types module
run_config = RunConfig(
    session_resumption=types.SessionResumptionConfig(),
    context_window_compression=types.ContextWindowCompressionConfig(...),
    speech_config=types.SpeechConfig(...),
    # etc.
)