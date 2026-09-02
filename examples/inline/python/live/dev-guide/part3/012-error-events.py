if event.error_code in ["SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST"]:
    # Model has stopped generating - continuation is impossible
    await websocket.send_json({
        "type": "error",
        "message": "I can't help with that request. Please ask something else."
    })
    break  # Exit loop - model won't send more events for this turn