# Custom server for live agents

Supported in ADKPython v0.1.0

The `adk web` tool runs a live agent for development purposes. It ships a browser client that captures the microphone and camera, plays model audio, and renders transcripts, so you can talk to your agent with no code of your own. Shipping to production means replacing that: running your own server that bridges clients to `run_live()`, with the runner and session service initialized once at startup and one `LiveRequestQueue` per connected user.

What follows is a complete FastAPI implementation of that bridge, and what a client needs to know to talk to it. It assumes you have read [Sessions](https://adk.dev/live/sessions/index.md), which covers the lifecycle this example puts into practice.

## FastAPI application example

This FastAPI application implements the bridge. It runs two concurrent tasks: an upstream task that forwards WebSocket messages into `LiveRequestQueue`, and a downstream task that forwards `run_live()` events back out.

```python
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google_search_agent.agent import agent

# Application setup (once at startup)
APP_NAME = "live-agent"

app = FastAPI()

# Define your session service
session_service = InMemorySessionService()

# Define your runner
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service
)

@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str) -> None:
    await websocket.accept()

    # Per-session setup: RunConfig, session, queue.
    response_modalities = ["AUDIO"]
    run_config = RunConfig(
        response_modalities=response_modalities,
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        session_resumption=types.SessionResumptionConfig()
    )

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

    live_request_queue = LiveRequestQueue()

    async def upstream_task() -> None:
        """Receives messages from WebSocket and sends to LiveRequestQueue."""
        try:
            while True:
                # Receive text message from WebSocket
                data: str = await websocket.receive_text()

                # Send to LiveRequestQueue
                content = types.Content(parts=[types.Part(text=data)])
                live_request_queue.send_content(content)
        except WebSocketDisconnect:
            # Client disconnected - signal queue to close
            pass

    async def downstream_task() -> None:
        """Receives Events from run_live() and sends to WebSocket."""
        async for event in runner.run_live(
            user_id=user_id,
            session_id=session_id,
            live_request_queue=live_request_queue,
            run_config=run_config
        ):
            # Send event as JSON to WebSocket
            await websocket.send_text(
                event.model_dump_json(exclude_none=True, by_alias=True)
            )

    # Run both tasks concurrently
    try:
        await asyncio.gather(
            upstream_task(),
            downstream_task(),
            return_exceptions=True
        )
    finally:
        live_request_queue.close()  # Always close, even on error.
```

Async Context Required

All ADK bidirectional streaming applications **must run in an async context**. This requirement comes from multiple components:

- **`run_live()`**: ADK's streaming method is an async generator with no synchronous wrapper (unlike `run()`)
- **Session operations**: `get_session()` and `create_session()` are async methods
- **WebSocket operations**: FastAPI's `websocket.accept()`, `receive_text()`, and `send_text()` are all async
- **Concurrent tasks**: The upstream/downstream pattern requires `asyncio.gather()` for concurrent execution

All code examples assume an async context (within an `async def` or coroutine). They show the core logic without boilerplate wrapper functions.

## Why two tasks

The bridge is two loops running at once, and that is what makes it bidirectional:

- **Upstream** reads from the WebSocket and pushes into the `LiveRequestQueue`, so the user can send input at any moment, including while the agent is mid-sentence.
- **Downstream** reads events from `run_live()` and writes them to the WebSocket, streaming responses, transcriptions, and tool activity out as they happen.

Run them sequentially and you lose interruption: the server would be blocked reading the agent's output while the user is trying to talk over it. `asyncio.gather()` is what keeps both directions live simultaneously.

`live_request_queue.close()` must run on every exit path, including exceptions. An unclosed queue leaves the Live API without a termination signal and can strand a session against your [concurrent-session quota](https://adk.dev/live/sessions/#concurrent-sessions) until it times out, which is what the `try/finally` is for.

`gather(..., return_exceptions=True)` collects exceptions rather than raising them, so check the returned values if you need to distinguish a clean disconnect from a failure.

### Production considerations

This example shows the core pattern. For production applications, consider:

- **Error handling (ADK)**: Add proper error handling for ADK streaming events. For details on error event handling, see [Error events](https://adk.dev/live/events/#handling-errors).
  - Handle task cancellation gracefully by catching `asyncio.CancelledError` during shutdown
  - Check exceptions from `asyncio.gather()` with `return_exceptions=True` - exceptions don't propagate automatically
- **Error handling (Web)**: Handle web application-specific errors in upstream/downstream tasks. For example, with FastAPI you would need to:
  - Catch `WebSocketDisconnect` (client disconnected), `ConnectionClosedError` (connection lost), and `RuntimeError` (sending to closed connection)
  - Validate WebSocket connection state before sending with `websocket.client_state` to prevent errors when the connection is closed
- **Authentication and authorization**: Implement authentication and authorization for your endpoints
- **Rate limiting and quotas**: Add rate limiting and timeout controls. For guidance on concurrent sessions and quota management, see [Concurrent sessions](https://adk.dev/live/sessions/#concurrent-sessions).
- **Structured logging**: Use structured logging for debugging.
- **Persistent session services**: Consider using persistent session services (`DatabaseSessionService` or `VertexAiSessionService`). See the [ADK Session Services documentation](https://adk.dev/sessions/index.md) for more details.

## Connect a client

Your server exposes a WebSocket; something has to talk to it. During development that is `adk web`. In production it is a client you write: a browser app, a mobile app, or a telephony or WebRTC bridge. Whatever you build inherits the same contract, so it is worth knowing exactly what `adk web` does and where it stops.

**What `adk web` handles for you:**

| Capability    | What the built-in client does                                                 |
| ------------- | ----------------------------------------------------------------------------- |
| Microphone    | Captures and resamples to 16 kHz mono PCM, streamed as `audio/pcm;rate=16000` |
| Playback      | Plays model audio as 24 kHz mono PCM, gapless                                 |
| Camera        | Sends JPEG frames at ~1 fps as `image/jpeg`                                   |
| Transcription | Renders both user and model transcripts, merging partial fragments            |
| Barge-in      | Stops playback when an event arrives with `interrupted` set                   |

**What it does not do**, and a production client may need:

- No screen sharing, and no video without an active audio call.
- No modality choice; responses are always `AUDIO`.
- No UI for proactivity, affective dialog, session resumption, `save_live_blob`, or explicit VAD signals. Those are set on the server through [`RunConfig`](https://adk.dev/live/configuration/index.md).
- No manual [VAD](https://adk.dev/live/configuration/#voice-activity-detection-vad); it relies on the server-side automatic detection that is on by default.

`adk web` and `adk api_server` both serve the same `/run_live` WebSocket; `adk api_server` does not ship the browser client unless you pass `--with_ui`. You can therefore develop against `adk web` and point a custom client at either.

### Wire protocol and data format

The `/run_live` endpoint speaks **JSON text frames only**. Your client sends serialized [`LiveRequest`](https://adk.dev/live/sessions/#liverequestqueue) objects and receives serialized [`Event`](https://adk.dev/live/events/index.md) objects. Binary data (audio and image bytes) is base64-encoded *inside* the JSON, not sent as binary WebSocket frames.

On the client, branch on the same event fields you would in Python, in camelCase:

```javascript
websocket.onmessage = (message) => {
    const adkEvent = JSON.parse(message.data);
    if (adkEvent.interrupted) {
        stopAudioPlayback();   // user barged in; drop queued audio
        finishCurrentBubble();
        return;
    }
    if (adkEvent.turnComplete) {
        finishCurrentBubble();
        return;
    }
    for (const part of adkEvent.content?.parts ?? []) {
        if (part.text) appendText(part.text);
        if (part.inlineData) enqueueAudio(part.inlineData.data);
    }
};
```

The media formats your client must produce and consume (sample rates, encodings, chunk sizes) are in [Audio and video](https://adk.dev/live/audio-video/index.md). The streaming flags it branches on (`partial`, `turnComplete`, `interrupted`) and how transcriptions fragment are in [Events](https://adk.dev/live/events/index.md).

## Serializing events

The `/run_live` endpoint between ADK and the Live API is JSON-text-only, but the transport between *your* server and *your* client is yours to design, and there you can send audio as binary frames to avoid base64 overhead.

`Event` is a Pydantic model, so `model_dump_json()` converts it to a JSON string for a WebSocket or SSE transport. Use `by_alias=True` for camelCase field names on the client and `exclude_none=True` to drop empty fields:

```python
async for event in runner.run_live(...):
    await websocket.send_text(event.model_dump_json(exclude_none=True, by_alias=True))
```

Binary audio in `inline_data` is base64-encoded in JSON, which inflates the payload by about 33%. For audio-heavy streams, send audio as binary frames and metadata as JSON:

```python
async for event in runner.run_live(...):
    parts = event.content.parts if event.content else []
    audio_parts = [p for p in parts if p.inline_data]
    if audio_parts:
        for part in audio_parts:
            await websocket.send_bytes(part.inline_data.data)
        # Metadata without the audio bytes.
        await websocket.send_text(event.model_dump_json(
            exclude={"content": {"parts": {"__all__": {"inline_data"}}}},
            by_alias=True,
        ))
    else:
        await websocket.send_text(event.model_dump_json(exclude_none=True, by_alias=True))
```
