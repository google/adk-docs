from google.genai import types
from google.adk.agents.run_config import RunConfig

# Default behavior: Audio transcription is ENABLED by default
# Both input and output transcription are automatically configured
run_config = RunConfig(
    response_modalities=["AUDIO"]
    # input_audio_transcription defaults to AudioTranscriptionConfig()
    # output_audio_transcription defaults to AudioTranscriptionConfig()
)

# To disable transcription explicitly:
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,   # Explicitly disable user input transcription
    output_audio_transcription=None   # Explicitly disable model output transcription
)

# Enable only input transcription (disable output):
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=types.AudioTranscriptionConfig(),  # Explicitly enable (redundant with default)
    output_audio_transcription=None  # Explicitly disable
)

# Enable only output transcription (disable input):
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,  # Explicitly disable
    output_audio_transcription=types.AudioTranscriptionConfig()  # Explicitly enable (redundant with default)
)