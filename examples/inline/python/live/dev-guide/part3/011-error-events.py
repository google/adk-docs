import logging

logger = logging.getLogger(__name__)

try:
    async for event in runner.run_live(...):
        # Handle errors from the model or connection
        if event.error_code:
            logger.error(f"Model error: {event.error_code} - {event.error_message}")

            # Send error notification to client
            await websocket.send_json({
                "type": "error",
                "code": event.error_code,
                "message": event.error_message
            })

            # Decide whether to continue or break based on error severity
            if event.error_code in ["SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST"]:
                # Content policy violations - usually cannot retry
                break  # Terminal error - exit loop
            elif event.error_code == "MAX_TOKENS":
                # Token limit reached - may need to adjust configuration
                break
            # For other errors, you might continue or implement retry logic
            continue  # Transient error - keep processing

        # Normal event processing only if no error
        if event.content and event.content.parts:
            # ... handle content
            pass
finally:
    queue.close()  # Always cleanup connection