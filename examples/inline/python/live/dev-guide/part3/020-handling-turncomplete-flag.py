async for event in runner.run_live(...):
    # Handle streaming text
    if event.content and event.content.parts and event.content.parts[0].text:
        if event.partial:
            # Your logic to show typing indicator and update partial text
            update_streaming_text(event.content.parts[0].text)
        else:
            # Your logic to display complete text chunk
            display_text(event.content.parts[0].text)

    # Handle interruption
    if event.interrupted:
        # Your logic to stop audio playback and clear indicators
        stop_audio_playback()
        clear_streaming_indicators()

    # Handle turn completion
    if event.turn_complete:
        # Your logic to enable user input
        show_input_ready_state()
        enable_microphone()