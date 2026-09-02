if event.error_code == "UNAVAILABLE":
    # Temporary network issue
    logger.warning(f"Network hiccup: {event.error_message}")
    # Don't notify user for brief transient issues that may self-resolve
    continue  # Keep listening - model may recover and continue