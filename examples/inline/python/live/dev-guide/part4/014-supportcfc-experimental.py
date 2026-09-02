# Even with SSE mode, ADK routes through Live API when CFC is enabled
run_config = RunConfig(
    support_cfc=True,
    streaming_mode=StreamingMode.SSE  # ADK uses Live API internally
)