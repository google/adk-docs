# ❌ INCORRECT: Both modalities not supported
run_config = RunConfig(
    response_modalities=["TEXT", "AUDIO"],  # ERROR: Cannot use both
    streaming_mode=StreamingMode.BIDI
)
# Error from Live API: "Only one response modality is supported per session"