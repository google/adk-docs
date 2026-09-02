async for event in runner.run_live(...):
    if event.interrupted:
        # Your logic to stop displaying partial text and clear typing indicators
        stop_streaming_display()

        # Your logic to show interruption in UI (optional)
        show_user_interruption_indicator()