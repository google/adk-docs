async for event in runner.run_live(...):
    if event.content and event.content.parts:
        if event.content.parts[0].text:
            text = event.content.parts[0].text

            if event.partial:
                # Your streaming UI update logic here
                update_streaming_display(text)
            else:
                # Your complete message display logic here
                display_complete_message(text)