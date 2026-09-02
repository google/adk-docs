# Configure RunConfig for audio responses
run_config = RunConfig(
    response_modalities=["AUDIO"],
    streaming_mode=StreamingMode.BIDI
)

# Audio arrives as inline_data in event.content.parts
async for event in runner.run_live(..., run_config=run_config):
    if event.content and event.content.parts:
        part = event.content.parts[0]
        if part.inline_data:
            # Audio event structure:
            # part.inline_data.data: bytes (raw PCM audio)
            # part.inline_data.mime_type: str (e.g., "audio/pcm")
            audio_data = part.inline_data.data
            mime_type = part.inline_data.mime_type

            print(f"Received {len(audio_data)} bytes of {mime_type}")
            # Your logic to play audio
            await play_audio(audio_data)