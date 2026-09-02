# Phase 2: Session initialization - RunConfig determines streaming behavior

# Default behavior: ADK automatically sets response_modalities to ["AUDIO"]
# when not specified (required by native audio models)
run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI  # Bidirectional WebSocket communication
)

# The above is equivalent to:
run_config = RunConfig(
    response_modalities=["AUDIO"],  # Automatically set by ADK in run_live()
    streaming_mode=StreamingMode.BIDI  # Bidirectional WebSocket communication
)

# ✅ CORRECT: Text-only responses
run_config = RunConfig(
    response_modalities=["TEXT"],  # Model responds with text only
    streaming_mode=StreamingMode.BIDI  # Still uses bidirectional streaming
)

# ✅ CORRECT: Audio-only responses (explicit)
run_config = RunConfig(
    response_modalities=["AUDIO"],  # Model responds with audio only
    streaming_mode=StreamingMode.BIDI  # Bidirectional WebSocket communication
)