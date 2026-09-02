async def upstream_task() -> None:
    """Receives messages from WebSocket and sends to LiveRequestQueue."""
    try:
        while True:
            data: str = await websocket.receive_text()
            content = types.Content(parts=[types.Part(text=data)])
            live_request_queue.send_content(content)
    except WebSocketDisconnect:
        pass  # Client disconnected