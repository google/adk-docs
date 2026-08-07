# Build a custom server

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">Experimental</span>
</div>

`adk web` is enough to develop and test a live agent, but shipping one means running your
own server: a WebSocket endpoint that bridges browser clients to `run_live()`, with the
runner and session service initialized once at startup and one `LiveRequestQueue` per
connected user.

This page walks through a complete FastAPI implementation of that bridge. It assumes you
have read [Sessions](sessions.md), which covers the lifecycle this example puts into
practice.

## FastAPI application example

Here's a complete FastAPI WebSocket application showing all four phases integrated with proper Bidi-streaming. The key pattern is **upstream/downstream tasks**: the upstream task receives messages from WebSocket and sends them to `LiveRequestQueue`, while the downstream task receives `Event` objects from `run_live()` and sends them to WebSocket.

!!! note "Complete Demo Implementation"

    For the production-ready implementation with multimodal support (text, audio, image), see the complete [`main.py`](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py) file.

**Complete Implementation:**

```python
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google_search_agent.agent import agent

# ========================================
# Phase 1: Application Initialization (once at startup)
# ========================================

APP_NAME = "bidi-demo"

app = FastAPI()

# Define your session service
session_service = InMemorySessionService()

# Define your runner
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service
)

# ========================================
# WebSocket Endpoint
# ========================================

@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str) -> None:
    await websocket.accept()

    # ========================================
    # Phase 2: Session Initialization (once per streaming session)
    # ========================================

    # Create RunConfig
    response_modalities = ["AUDIO"]
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=response_modalities,
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        session_resumption=types.SessionResumptionConfig()
    )

    # Get or create session
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

    # Create LiveRequestQueue
    live_request_queue = LiveRequestQueue()

    # ========================================
    # Phase 3: Active Session (concurrent bidirectional communication)
    # ========================================

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
        # ========================================
        # Phase 4: Session Termination
        # ========================================

        # Always close the queue, even if exceptions occurred
        live_request_queue.close()
```

!!! note "Async Context Required"

    All ADK bidirectional streaming applications **must run in an async context**. This requirement comes from multiple components:

    - **`run_live()`**: ADK's streaming method is an async generator with no synchronous wrapper (unlike `run()`)
    - **Session operations**: `get_session()` and `create_session()` are async methods
    - **WebSocket operations**: FastAPI's `websocket.accept()`, `receive_text()`, and `send_text()` are all async
    - **Concurrent tasks**: The upstream/downstream pattern requires `asyncio.gather()` for concurrent execution

    All code examples in this guide assume you're running in an async context (e.g., within an async function or coroutine). For consistency with ADK's official documentation patterns, examples show the core logic without boilerplate wrapper functions.

## Key concepts

**Upstream Task (WebSocket → LiveRequestQueue)**

The upstream task continuously receives messages from the WebSocket client and forwards them to the `LiveRequestQueue`. This enables the user to send messages to the agent at any time, even while the agent is generating a response.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L169-L217" target="_blank">main.py:169-217</a>'
async def upstream_task() -> None:
    """Receives messages from WebSocket and sends to LiveRequestQueue."""
    try:
        while True:
            data: str = await websocket.receive_text()
            content = types.Content(parts=[types.Part(text=data)])
            live_request_queue.send_content(content)
    except WebSocketDisconnect:
        pass  # Client disconnected
```

**Downstream Task (run_live() → WebSocket)**

The downstream task continuously receives `Event` objects from `run_live()` and sends them to the WebSocket client. This streams the agent's responses, tool executions, transcriptions, and other events to the user in real-time.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L219-L234" target="_blank">main.py:219-234</a>'
async def downstream_task() -> None:
    """Receives Events from run_live() and sends to WebSocket."""
    async for event in runner.run_live(
        user_id=user_id,
        session_id=session_id,
        live_request_queue=live_request_queue,
        run_config=run_config
    ):
        await websocket.send_text(
            event.model_dump_json(exclude_none=True, by_alias=True)
        )
```

**Concurrent Execution with Cleanup**

Both tasks run concurrently using `asyncio.gather()`, enabling true Bidi-streaming. The `try/finally` block ensures `LiveRequestQueue.close()` is called even if exceptions occur, minimizing the session resource usage.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L238-L253" target="_blank">main.py:238-253</a>'
try:
    await asyncio.gather(
        upstream_task(),
        downstream_task(),
        return_exceptions=True
    )
finally:
    live_request_queue.close()  # Always cleanup
```

This pattern—concurrent upstream/downstream tasks with guaranteed cleanup—is the foundation of production-ready streaming applications. The lifecycle pattern (initialize once, stream many times) enables efficient resource usage and clean separation of concerns, with application components remaining stateless and reusable while session-specific state is isolated in `LiveRequestQueue`, `RunConfig`, and session records.

### Production considerations

This example shows the core pattern. For production applications, consider:

- **Error handling (ADK)**: Add proper error handling for ADK streaming events. For details on error event handling, see [Part 3: Error Events](part3.md#error-events).
    - Handle task cancellation gracefully by catching `asyncio.CancelledError` during shutdown
    - Check exceptions from `asyncio.gather()` with `return_exceptions=True` - exceptions don't propagate automatically
- **Error handling (Web)**: Handle web application-specific errors in upstream/downstream tasks. For example, with FastAPI you would need to:
    - Catch `WebSocketDisconnect` (client disconnected), `ConnectionClosedError` (connection lost), and `RuntimeError` (sending to closed connection)
    - Validate WebSocket connection state before sending with `websocket.client_state` to prevent errors when the connection is closed
- **Authentication and authorization**: Implement authentication and authorization for your endpoints
- **Rate limiting and quotas**: Add rate limiting and timeout controls. For guidance on concurrent sessions and quota management, see [Part 4: Concurrent Live API Sessions and Quota Management](part4.md#concurrent-live-api-sessions-and-quota-management).
- **Structured logging**: Use structured logging for debugging.
- **Persistent session services**: Consider using persistent session services (`DatabaseSessionService` or `VertexAiSessionService`). See the [ADK Session Services documentation](/sessions/) for more details.

