async for event in runner.run_live(...):
    if event.content and event.content.parts:
        if event.content.parts[0].text:
            text = event.content.parts[0].text

            if not event.partial:
                # Your logic to update streaming display
                update_streaming_display(text)