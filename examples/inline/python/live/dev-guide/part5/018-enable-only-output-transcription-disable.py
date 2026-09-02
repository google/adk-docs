from google.adk.runners import Runner

# ... runner setup code ...

async for event in runner.run_live(...):
    # User's speech transcription (from input audio)
    if event.input_transcription:  # First check: transcription object exists
        # Access the transcription text and status
        user_text = event.input_transcription.text
        is_finished = event.input_transcription.finished

        # Second check: text is not None or empty
        # This handles cases where transcription is in progress or empty
        if user_text and user_text.strip():
            print(f"User said: {user_text} (finished: {is_finished})")

            # Your caption update logic
            update_caption(user_text, is_user=True, is_final=is_finished)

    # Model's speech transcription (from output audio)
    if event.output_transcription:  # First check: transcription object exists
        model_text = event.output_transcription.text
        is_finished = event.output_transcription.finished

        # Second check: text is not None or empty
        # This handles cases where transcription is in progress or empty
        if model_text and model_text.strip():
            print(f"Model said: {model_text} (finished: {is_finished})")

            # Your caption update logic
            update_caption(model_text, is_user=False, is_final=is_finished)