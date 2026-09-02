async def handle_sequential_workflow():
    """Recommended pattern for SequentialAgent with BIDI streaming."""

    # 1. Single queue shared across all agents in the sequence
    queue = LiveRequestQueue()

    # 2. Background task captures user input continuously
    async def capture_user_input():
        while True:
            # Your logic to read audio from microphone
            audio_chunk = await microphone.read()
            queue.send_realtime(
                blob=types.Blob(data=audio_chunk, mime_type="audio/pcm")
            )

    input_task = asyncio.create_task(capture_user_input())

    try:
        # 3. Single event loop handles ALL agents seamlessly
        async for event in runner.run_live(
            user_id="user_123",
            session_id="session_456",
            live_request_queue=queue,
        ):
            # Events flow seamlessly across agent transitions
            current_agent = event.author

            # Handle audio and text output
            if event.content and event.content.parts:
                for part in event.content.parts:
                    # Check for audio data
                    if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                        # Your logic to play audio
            await play_audio(part.inline_data.data)

                    # Check for text data
                    if part.text:
                        await display_text(f"[{current_agent}] {part.text}")

            # No special transition handling needed!

    finally:
        input_task.cancel()
        queue.close()