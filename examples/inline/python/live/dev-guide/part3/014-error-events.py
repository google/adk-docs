if event.error_code == "MAX_TOKENS":
    # Model has reached output limit
    await websocket.send_json({
        "type": "complete",
        "message": "Response reached maximum length",
        "truncated": True
    })
    break  # Model has finished - no more tokens will be generated