async def upstream_task(websocket: WebSocket, live_request_queue: LiveRequestQueue):
    """Receives audio and activity signals from client."""
    try:
        while True:
            # Receive JSON message from WebSocket
            message = await websocket.receive_json()

            if message.get("type") == "activity_start":
                # Client detected voice - signal the model
                live_request_queue.send_activity_start()

            elif message.get("type") == "activity_end":
                # Client detected silence - signal the model
                live_request_queue.send_activity_end()

            elif message.get("type") == "audio":
                # Stream audio chunk to the model
                import base64
                audio_data = base64.b64decode(message["data"])
                audio_blob = types.Blob(
                    mime_type="audio/pcm;rate=16000",
                    data=audio_data
                )
                live_request_queue.send_realtime(audio_blob)

    except WebSocketDisconnect:
        live_request_queue.close()