from google.adk.agents.run_config import RunConfig, StreamingMode

# Configure for audio output
run_config = RunConfig(
    response_modalities=["AUDIO"],  # Required for audio responses
    streaming_mode=StreamingMode.BIDI
)

# Process audio output from the model
async for event in runner.run_live(
    user_id="user_123",
    session_id="session_456",
    live_request_queue=live_request_queue,
    run_config=run_config
):
    # Events may contain multiple parts (text, audio, etc.)
    if event.content and event.content.parts:
        for part in event.content.parts:
            # Audio data arrives as inline_data with audio/pcm MIME type
            if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                # The data is already decoded to raw bytes (24kHz, 16-bit PCM, mono)
                audio_bytes = part.inline_data.data

                # Your logic to stream audio to client
                await stream_audio_to_client(audio_bytes)

                # Or save to file
                # with open("output.pcm", "ab") as f:
                #     f.write(audio_bytes)