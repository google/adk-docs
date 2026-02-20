# Part 2: Sending messages with LiveRequestQueue

In Part 1, you learned the four-phase lifecycle of ADK Bidi-streaming applications. This part focuses on the upstream flow—how your application sends messages to the agent using `LiveRequestQueue`.

Unlike traditional APIs where different message types require different endpoints or channels, ADK provides a single unified interface through `LiveRequestQueue` and its `LiveRequest` message model. This part covers:

- **Message types**: Sending text via `send_content()`, streaming audio/image/video via `send_realtime()`, controlling conversation turns with activity signals, and gracefully terminating sessions with control signals
- **Concurrency patterns**: Understanding async queue management and event-loop thread safety
- **Best practices**: Creating queues in async context, ensuring proper resource cleanup, and understanding message ordering guarantees
- **Troubleshooting**: Diagnosing common issues like messages not being processed and queue lifecycle problems

Understanding `LiveRequestQueue` is essential for building responsive streaming applications that handle multimodal inputs seamlessly within async event loops.

## LiveRequestQueue and LiveRequest

The `LiveRequestQueue` is your primary interface for sending messages to the Agent in streaming conversations. Rather than managing separate channels for text, audio, and control signals, ADK provides a unified `LiveRequest` container that handles all message types through a single, elegant API:

Source reference: [live_request_queue.py](https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/agents/live_request_queue.py)

```python
class LiveRequest(BaseModel):
    content: Optional[Content] = None           # Text-based content and structured data
    blob: Optional[Blob] = None                 # Audio/video data and binary streams
    activity_start: Optional[ActivityStart] = None  # Signal start of user activity
    activity_end: Optional[ActivityEnd] = None      # Signal end of user activity
    close: bool = False                         # Graceful connection termination signal
```

This streamlined design handles every streaming scenario you'll encounter. The `content` and `blob` fields handle different data types, the `activity_start` and `activity_end` fields enable activity signaling, and the `close` flag provides graceful termination semantics.

The `content` and `blob` fields are mutually exclusive—only one can be set per LiveRequest. While ADK does not enforce this client-side and will attempt to send both if set, the Live API backend will reject this with a validation error. ADK's convenience methods `send_content()` and `send_realtime()` automatically ensure this constraint is met by setting only one field, so **using these methods (rather than manually creating `LiveRequest` objects) is the recommended approach**.

The following diagram illustrates how different message types flow from your application through `LiveRequestQueue` methods, into `LiveRequest` containers, and finally to the Live API:

```
graph LR
    subgraph "Application"
        A1[User Text Input]
        A2[Audio Stream]
        A3[Activity Signals]
        A4[Close Signal]
    end

    subgraph "LiveRequestQueue Methods"
        B1[send_content<br/>Content]
        B2[send_realtime<br/>Blob]
        B3[send_activity_start<br/>ActivityStart]
        B3b[send_activity_end<br/>ActivityEnd]
        B4[close<br/>close=True]
    end

    subgraph "LiveRequest Container"
        C1[content: Content]
        C2[blob: Blob]
        C3[activity_start/end]
        C4[close: bool]
    end

    subgraph "Gemini Live API"
        D[WebSocket Connection]
    end

    A1 --> B1 --> C1 --> D
    A2 --> B2 --> C2 --> D
    A3 --> B3 --> C3 --> D
    A3 --> B3b --> C3
    A4 --> B4 --> C4 --> D
```

## Sending Different Message Types

`LiveRequestQueue` provides convenient methods for sending different message types to the agent. This section demonstrates practical patterns for text messages, audio/video streaming, activity signals for manual turn control, and session termination.

### send_content(): Sends Text With Turn-by-Turn

The `send_content()` method sends text messages in turn-by-turn mode, where each message represents a discrete conversation turn. This signals a complete turn to the model, triggering immediate response generation.

Demo implementation: [main.py:194-199](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L194-L199)

```python
content = types.Content(parts=[types.Part(text=json_message["text"])])
live_request_queue.send_content(content)
```

**Using Content and Part with ADK Bidi-streaming:**

- **`Content`** (`google.genai.types.Content`): A container that represents a single message or turn in the conversation. It holds an array of `Part` objects that together compose the complete message.
- **`Part`** (`google.genai.types.Part`): An individual piece of content within a message. For ADK Bidi-streaming with Live API, you'll use:
- `text`: Text content (including code) that you send to the model

In practice, most messages use a single text Part for ADK Bidi-streaming. The multi-part structure is designed for scenarios like:

- Mixing text with function responses (automatically handled by ADK)
- Combining text explanations with structured data
- Future extensibility for new content types

For Live API, multimodal inputs (audio/video) use different mechanisms (see `send_realtime()` below), not multi-part Content.

Content and Part usage in ADK Bidi-streaming

While the Gemini API `Part` type supports many fields (`inline_data`, `file_data`, `function_call`, `function_response`, etc.), most are either handled automatically by ADK or use different mechanisms in Live API:

- **Function calls**: ADK automatically handles the function calling loop - receiving function calls from the model, executing your registered functions, and sending responses back. You don't manually construct these.
- **Images/Video**: Do NOT use `send_content()` with `inline_data`. Instead, use `send_realtime(Blob(mime_type="image/jpeg", data=...))` for continuous streaming. See [Part 5: How to Use Image and Video](https://google.github.io/adk-docs/streaming/dev-guide/part5/#how-to-use-image-and-video).

### send_realtime(): Sends Audio, Image and Video in Real-Time

The `send_realtime()` method sends binary data streams—primarily audio, image and video—flow through the `Blob` type, which handles transmission in realtime mode. Unlike text content that gets processed in turn-by-turn mode, blobs are designed for continuous streaming scenarios where data arrives in chunks. You provide raw bytes, and Pydantic automatically handles base64 encoding during JSON serialization for safe network transmission (configured in `LiveRequest.model_config`). The MIME type helps the model understand the content format.

Demo implementation: [main.py:181-184](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L181-L184)

```python
audio_blob = types.Blob(
    mime_type="audio/pcm;rate=16000",
    data=audio_data
)
live_request_queue.send_realtime(audio_blob)
```

Learn More

For complete details on audio, image and video specifications, formats, and best practices, see [Part 5: How to Use Audio, Image and Video](https://google.github.io/adk-docs/streaming/dev-guide/part5/index.md).

### Activity Signals

Activity signals (`ActivityStart`/`ActivityEnd`) can **ONLY** be sent when automatic (server-side) Voice Activity Detection is **explicitly disabled** in your `RunConfig`. Use them when your application requires manual voice activity control, such as:

- **Push-to-talk interfaces**: User explicitly controls when they're speaking (e.g., holding a button)
- **Noisy environments**: Background noise makes automatic VAD unreliable, so you use client-side VAD or manual control
- **Client-side VAD**: You implement your own VAD algorithm on the client to reduce network overhead by only sending audio when speech is detected
- **Custom interaction patterns**: Non-speech scenarios like gesture-triggered interactions or timed audio segments

**What activity signals tell the model:**

- `ActivityStart`: "The user is now speaking - start accumulating audio for processing"
- `ActivityEnd`: "The user has finished speaking - process the accumulated audio and generate a response"

Without these signals (when VAD is disabled), the model doesn't know when to start/stop listening for speech, so you must explicitly mark turn boundaries.

**Sending Activity Signals:**

```python
from google.genai import types

# Manual activity signal pattern (e.g., push-to-talk)
live_request_queue.send_activity_start()  # Signal: user started speaking

# Stream audio chunks while user holds the talk button
while user_is_holding_button:
    audio_blob = types.Blob(mime_type="audio/pcm;rate=16000", data=audio_chunk)
    live_request_queue.send_realtime(audio_blob)

live_request_queue.send_activity_end()  # Signal: user stopped speaking
```

**Default behavior (automatic VAD):** If you don't send activity signals, Live API's built-in VAD automatically detects speech boundaries in the audio stream you send via `send_realtime()`. This is the recommended approach for most applications.

Learn More

For detailed comparison of automatic VAD vs manual activity signals, including when to disable VAD and best practices, see [Part 5: Voice Activity Detection](https://google.github.io/adk-docs/streaming/dev-guide/part5/#voice-activity-detection-vad).

### Control Signals

The `close` signal provides graceful termination semantics for streaming sessions. It signals the system to cleanly close the model connection and end the Bidi-stream. In ADK Bidi-streaming, your application is responsible for sending the `close` signal explicitly:

**Manual closure in BIDI mode:** When using `StreamingMode.BIDI` (Bidi-streaming), your application should manually call `close()` when the session terminates or when errors occur. This practice minimizes session resource usage.

**Automatic closure in SSE mode:** When using the legacy `StreamingMode.SSE` (not Bidi-streaming), ADK automatically calls `close()` on the queue when it receives a `turn_complete=True` event from the model (see [`base_llm_flow.py:781`](https://github.com/google/adk-python/blob/fd2c0f556b786417a9f6add744827b07e7a06b7d/src/google/adk/flows/llm_flows/base_llm_flow.py#L780)).

See [Part 4: Understanding RunConfig](https://google.github.io/adk-docs/streaming/dev-guide/part4/#streamingmode-bidi-or-sse) for detailed comparison and when to use each mode.

Demo implementation: [main.py:238-253](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L238-L253)

```python
try:
    logger.debug("Starting asyncio.gather for upstream and downstream tasks")
    await asyncio.gather(
        upstream_task(),
        downstream_task()
    )
    logger.debug("asyncio.gather completed normally")
except WebSocketDisconnect:
    logger.debug("Client disconnected normally")
except Exception as e:
    logger.error(f"Unexpected error in streaming tasks: {e}", exc_info=True)
finally:
    # Always close the queue, even if exceptions occurred
    logger.debug("Closing live_request_queue")
    live_request_queue.close()
```

**What happens if you don't call close()?**

Although ADK cleans up local resources automatically, failing to call `close()` in BIDI mode prevents sending a graceful termination signal to the Live API, which will then receive an abrupt disconnection after certain timeout period. This can lead to "zombie" Live API sessions that remain open on the cloud service, even though your application has finished with them. These stranded sessions may significantly decrease the number of concurrent sessions your application can handle, as they continue to count against your quota limits until they eventually timeout.

Learn More

For comprehensive error handling patterns during streaming, including when to use `break` vs `continue` and handling different error types, see [Part 3: Error Events](https://google.github.io/adk-docs/streaming/dev-guide/part3/#error-events).

## Concurrency and Thread Safety

Understanding how `LiveRequestQueue` handles concurrency is essential for building reliable streaming applications. The queue is built on `asyncio.Queue`, which means it's safe for concurrent access **within the same event loop thread** (the common case), but requires special handling when called from **different threads** (the advanced case). This section explains the design choices behind `LiveRequestQueue`'s API, when you can safely use it without extra precautions, and when you need thread-safety mechanisms like `loop.call_soon_threadsafe()`.

### Async Queue Management

`LiveRequestQueue` uses synchronous methods (`send_content()`, `send_realtime()`) instead of async methods, even though the underlying queue is consumed asynchronously. This design choice uses `asyncio.Queue.put_nowait()` - a non-blocking operation that doesn't require `await`.

**Why synchronous send methods?** Convenience and simplicity. You can call them from anywhere in your async code without `await`:

Demo implementation: [main.py:169-199](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L169-L199)

```python
async def upstream_task() -> None:
    """Receives messages from WebSocket and sends to LiveRequestQueue."""
    while True:
        message = await websocket.receive()

        if "bytes" in message:
            audio_data = message["bytes"]
            audio_blob = types.Blob(
                mime_type="audio/pcm;rate=16000",
                data=audio_data
            )
            live_request_queue.send_realtime(audio_blob)

        elif "text" in message:
            text_data = message["text"]
            json_message = json.loads(text_data)

            if json_message.get("type") == "text":
                content = types.Content(parts=[types.Part(text=json_message["text"])])
                live_request_queue.send_content(content)
```

This pattern mixes async I/O operations with sync CPU operations naturally. The send methods return immediately without blocking, allowing your application to stay responsive.

#### Best Practice: Create Queue in Async Context

Always create `LiveRequestQueue` within an async context (async function or coroutine) to ensure it uses the correct event loop:

```python
# ✅ Recommended - Create in async context
async def main():
    queue = LiveRequestQueue()  # Uses existing event loop from async context
    # This is the preferred pattern - ensures queue uses the correct event loop
    # that will run your streaming operations

# ❌ Not recommended - Creates event loop automatically
queue = LiveRequestQueue()  # Works but ADK auto-creates new loop
# This works due to ADK's safety mechanism, but may cause issues with
# loop coordination in complex applications or multi-threaded scenarios
```

**Why this matters:** `LiveRequestQueue` requires an event loop to exist when instantiated. ADK includes a safety mechanism that auto-creates a loop if none exists, but relying on this can cause unexpected behavior in multi-threaded scenarios or with custom event loop configurations.

## Message Ordering Guarantees

`LiveRequestQueue` provides predictable message delivery behavior:

| Guarantee                | Description                                                                 | Impact                                                                                                                                                                |
| ------------------------ | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FIFO ordering**        | Messages processed in send order (guaranteed by underlying `asyncio.Queue`) | Maintains conversation context and interaction consistency                                                                                                            |
| **No coalescing**        | Each message delivered independently                                        | No automatic batching—each send operation creates one request                                                                                                         |
| **Unbounded by default** | Queue accepts unlimited messages without blocking                           | **Benefit**: Simplifies client code (no blocking on send) **Risk**: Memory growth if sending faster than processing **Mitigation**: Monitor queue depth in production |

> **Production Tip**: For high-throughput audio/video streaming, monitor `live_request_queue._queue.qsize()` to detect backpressure. If the queue depth grows continuously, slow down your send rate or implement batching. Note: `_queue` is an internal attribute and may change in future releases; use with caution.

## Summary

In this part, you learned how `LiveRequestQueue` provides a unified interface for sending messages to ADK streaming agents within an async event loop. We covered the `LiveRequest` message model and explored how to send different message types: text content via `send_content()`, audio/video blobs via `send_realtime()`, activity signals for manual turn control, and control signals for graceful termination via `close()`. You also learned best practices for async queue management, creating queues in async context, resource cleanup, and message ordering. You now understand how to use `LiveRequestQueue` as the upstream communication channel in your Bidi-streaming applications, enabling users to send messages concurrently while receiving agent responses. Next, you'll learn how to handle the downstream flow—processing the events that agents generate in response to these messages.

______________________________________________________________________

← [Previous: Part 1: Introduction to ADK Bidi-streaming](https://google.github.io/adk-docs/streaming/dev-guide/part1/index.md) | [Next: Part 3: Event Handling with run_live()](https://google.github.io/adk-docs/streaming/dev-guide/part3/index.md) →
