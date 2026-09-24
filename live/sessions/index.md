# Sessions for live agents

Supported in ADKPython v0.1.0

A live agent is a connection that stays open while the user talks, listens, interrupts, and falls silent.

Live agents use the same `Session`, `SessionService`, and state model as any ADK agent, all covered in [Conversational context](https://adk.dev/sessions/index.md). What a live session adds is a *connection*: one that can drop, time out, or outlive the model's context window. For what comes *back* out of that connection, see [Events](https://adk.dev/live/events/index.md); for the settings that shape it, see [Configuration](https://adk.dev/live/configuration/index.md).

## Set up a live application

A live application has two kinds of objects: ones you create once at startup and reuse for every session, and ones you create fresh per session.

**Create once, reuse everywhere:**

- **`Agent`**: your model, tools, and instructions. Stateless and reusable.
- **`SessionService`**: stores conversation history so sessions survive reconnects and restarts.
- **`Runner`**: the runtime that drives the agent and yields events.

```python
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search

APP_NAME = "live-agent"

agent = Agent(
    name="google_search_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
    tools=[google_search],
    instruction="You are a helpful assistant that can search the web.",
)

runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=InMemorySessionService(),
)
```

`InMemorySessionService` loses state when the process stops. For production, use `DatabaseSessionService` (SQLite, PostgreSQL, or MySQL) or `VertexAiSessionService` (managed on Google Cloud). See [Session services](https://adk.dev/sessions/index.md).

**Create per session:**

- A [`Session`](#adk-session-vs-live-api-session), fetched or created before the loop runs.
- A [`RunConfig`](https://adk.dev/live/configuration/index.md), which can differ per user (voice, transcription, limits).
- A [`LiveRequestQueue`](#liverequestqueue), the channel you send user input through.

```python
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.genai import types

# Get-or-create handles both new conversations and reconnections.
session = await session_service.get_session(
    app_name=APP_NAME, user_id=user_id, session_id=session_id
)
if not session:
    await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

run_config = RunConfig(
    response_modalities=["AUDIO"],
    session_resumption=types.SessionResumptionConfig(),
)

live_request_queue = LiveRequestQueue()
```

`user_id` and `session_id` are arbitrary strings you define; ADK generates a UUID if you pass `session_id=None`. The session must exist before you call `run_live()` with the same identifiers, or `run_live()` raises `ValueError: Session not found`.

One queue per session

Never reuse a `LiveRequestQueue` across sessions. The close signal persists in the queue and would carry over, corrupting the next session. Create a fresh queue for every `run_live()` call.

## LiveRequestQueue

`LiveRequestQueue` is your channel for sending messages to the agent. Every message is a `LiveRequest`, a single container for the different kinds of input:

Reference: <a href="../api-reference/python/google-adk.html#google.adk.agents.LiveRequestQueue">LiveRequestQueue</a>

```python
class LiveRequest(BaseModel):
    content: Optional[Content] = None            # Text and structured data
    blob: Optional[Blob] = None                  # Audio/video bytes
    activity_start: Optional[ActivityStart] = None  # Manual turn start
    activity_end: Optional[ActivityEnd] = None      # Manual turn end
    close: bool = False                          # Graceful termination
```

`content` and `blob` are mutually exclusive. Use the convenience methods rather than building `LiveRequest` objects yourself; they set the right field and keep you within that constraint.

| Method                                          | Sends                        | Mode                                |
| ----------------------------------------------- | ---------------------------- | ----------------------------------- |
| `send_content(content)`                         | Text, as a discrete turn     | Turn-by-turn; triggers a response   |
| `send_realtime(blob)`                           | Audio, image, or video bytes | Continuous streaming                |
| `send_activity_start()` / `send_activity_end()` | Manual turn boundaries       | Only when automatic VAD is disabled |
| `close()`                                       | Termination signal           | Ends the session                    |

```python
from google.genai import types

# Text turn.
live_request_queue.send_content(types.Content(parts=[types.Part(text=user_text)]))

# Audio chunk (streamed continuously).
live_request_queue.send_realtime(
    types.Blob(mime_type="audio/pcm;rate=16000", data=audio_data)
)
```

For audio, image, and video formats, see [Audio and video](https://adk.dev/live/audio-video/index.md). For manual turn control with activity signals, see [Voice activity detection](https://adk.dev/live/configuration/#voice-activity-detection-vad).

Send one text Part per call

Send a single text `Part` per `send_content()` call. Some Live models treat a multi-part `Content` as conversation seeding (priming history) rather than a turn to respond to, so one Part per call keeps behavior consistent across models.

### Concurrency and ordering

`LiveRequestQueue` wraps an `asyncio.Queue`, which has three consequences:

- **Send methods are synchronous.** They call `put_nowait()` underneath, so they never block and never need `await`.
- **Delivery is FIFO and uncoalesced.** Requests reach the model in send order, one per call.
- **The queue is unbounded.** Sending faster than the model consumes grows memory rather than applying backpressure, so cap your own send rate for high-rate audio or video.

Create the queue inside an async context so it binds to the event loop that runs `run_live()`. `asyncio.Queue` is safe for concurrent access within a single event loop thread; to feed it from another thread, use `loop.call_soon_threadsafe()`.

## The run_live() loop

`run_live()` is an async generator. It yields `Event` objects the moment they are generated, with no buffering or polling, while you send new input concurrently through the queue. That concurrency is what makes interruption work: the agent can be speaking while the user starts talking over it.

Reference: <a href="../api-reference/python/google-adk.html#google.adk.runners.Runner.run_live">Runner.run_live()</a>

```python
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config,
):
    await websocket.send_text(event.model_dump_json(exclude_none=True, by_alias=True))
```

`run_live()` opens the Live API connection when you call it, streams both directions while the loop runs, and closes the connection when you call `live_request_queue.close()`. For the event types it yields and how to handle them, see [Events](https://adk.dev/live/events/index.md).

### When run_live() exits

| Exit condition    | Trigger                                                | Graceful          |
| ----------------- | ------------------------------------------------------ | ----------------- |
| Manual close      | `live_request_queue.close()`                           | Yes               |
| Workflow complete | Last agent in a live workflow calls `task_completed()` | Yes               |
| Session timeout   | Live API duration limit reached (without compression)  | Connection closed |
| Early exit        | `end_invocation` set by a tool or callback             | Yes               |
| Error             | Connection failure or unhandled exception              | No                |

Always call `close()` when the session ends, even on error. Skipping it leaves the Live API without a graceful termination signal, which can strand "zombie" sessions that count against your [concurrent-session quota](#concurrent-sessions) until they time out.

```python
try:
    await asyncio.gather(upstream_task(), downstream_task())
except WebSocketDisconnect:
    pass  # Client disconnected normally.
finally:
    live_request_queue.close()  # Always close the queue.
```

For error handling inside the loop, see [Error events](https://adk.dev/live/events/#handling-errors). For the full upstream/downstream server pattern, see [Custom server](https://adk.dev/live/custom-server/index.md).

### What gets saved to the session

When `run_live()` exits, only some events persist to the ADK `Session`:

- **Saved:** final (non-partial) transcriptions, usage metadata, function calls and responses, and most control events. Audio files are saved only when [`save_live_blob`](https://adk.dev/live/configuration/#save_live_blob) is `True`.
- **Ephemeral:** raw audio bytes (`inline_data`) and partial transcriptions, yielded for real-time playback and display but not stored.

## ADK Session vs Live API session

Two different things share the word "session":

- **ADK `Session`** (managed by `SessionService`) is persistent conversation storage. It survives across many `run_live()` calls and application restarts.
- **Live API session** (managed by the Live API backend) is a transient streaming context that exists only while the loop runs.

When `run_live()` starts, ADK loads history from the ADK `Session`, initializes a new Live API session with it, and updates the ADK `Session` as events occur. When the loop ends, the Live API session is destroyed and the ADK `Session` persists. The next call rebuilds a Live API session from the stored history. This separation is what lets conversations continue across network drops and restarts.

At the transport layer, one more distinction matters for reliability:

- A **connection** is the WebSocket link between ADK and the Live API. It can time out.
- A **session** is the conversation context, which can span multiple connections through [session resumption](#session-resumption).

### Platform limits

Both backends cap connection duration, session duration, and concurrent sessions. The exact numbers differ by backend and change over time, so [Supported models](https://adk.dev/live/models/#platform-limits-and-quotas) tracks them in one place.

Two of those caps change how you write the code. [Context window compression](#context-window-compression) lifts the session-duration limit, and the concurrent-session ceiling is what you design against in [Concurrent sessions](#concurrent-sessions).

## Session resumption

The Live API closes each WebSocket connection after about 10 minutes. [Session resumption](https://ai.google.dev/gemini-api/docs/live-api/session-management#session-resumption) migrates the conversation across connections so it continues past that limit. Enable it and **ADK handles all reconnection for you**, caching resumption handles, detecting closures, and reconnecting in the background. Your `run_live()` loop keeps yielding events without interruption.

```python
from google.genai import types

run_config = RunConfig(session_resumption=types.SessionResumptionConfig())
```

ADK manages the ADK-to-Live-API connection only. Your application still owns its own client connections (for example, the user's WebSocket to your server) and any client-side reconnect logic.

How ADK reconnects:

1. The Live API sends `session_resumption_update` messages; ADK caches the latest handle.
1. Before the limit, the Live API may send a `go_away` warning; ADK reconnects *before* the drop, so the handover is invisible.
1. When a connection closes gracefully, ADK's loop reconnects with the cached handle and the session continues with full context.

```
sequenceDiagram
    participant App as Your Application
    participant ADK as ADK (run_live)
    participant API as Live API

    App->>ADK: run_live(run_config with session_resumption)
    ADK->>API: WebSocket connect()
    Note over ADK,API: Streaming (0-10 min)
    API-->>ADK: session_resumption_update { handle }
    ADK->>ADK: Cache handle
    Note over API: ~10 min: connection closes gracefully
    ADK->>API: reconnect(handle)
    API-->>ADK: Session resumed with full context
    Note over App,API: Loop continues, uninterrupted
```

Reconnection attempts are capped

ADK retries a maximum of **5 consecutive** reconnections ([`DEFAULT_MAX_RECONNECT_ATTEMPTS`](https://github.com/google/adk-python/blob/main/src/google/adk/flows/llm_flows/base_llm_flow.py)). The counter resets on each successful reconnect, so a long conversation is limited only to five *failures in a row*, not five reconnects total. ADK retries only when a resumption handle exists; without `session_resumption` enabled, the first drop propagates straight out of `run_live()`, and your application must handle it.

Skip resumption only for short sessions (under 10 minutes), stateless request-response interactions, or development where a fresh session per run aids debugging.

## Context window compression

Long conversations hit two limits: the session duration caps, and the model's context window (varies by model). [Context window compression](https://ai.google.dev/gemini-api/docs/live-api/session-management#context-window-compression) addresses both. It compresses older conversation history with a sliding window when the token count crosses a threshold, keeping recent turns in full. **Enabling it removes the session duration limits.** The trade-off: older context becomes a summary, not verbatim history.

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

# For a 128k-context model.
run_config = RunConfig(
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=100000,  # Start compressing near ~78% of the window.
        sliding_window=types.SlidingWindow(
            target_tokens=80000,  # Compress down to ~62%, keeping recent turns.
        ),
    )
)
```

Set `trigger_tokens` to roughly 70-80% of the model's context window for headroom, and `target_tokens` to 60-70% so each compression frees enough room for several turns. Test with your own conversation patterns. Enable compression when sessions must run longer than the platform limits or may exceed the token limit; leave it off for short sessions or when precise recall of early turns is critical.

## Concurrent sessions

Each user needs their own Live API session, and both backends cap concurrent sessions. Your concurrent-session ceiling is a hard cap on simultaneous users. For the current ceilings and how to request increases, see [Supported models](https://adk.dev/live/models/#platform-limits-and-quotas).

Design for the ceiling:

- **One session per user** is the default and correct choice while peak concurrency fits inside the quota.
- **A session pool** (a fixed set of sessions handed out through a queue) keeps you inside the quota when peak concurrency exceeds it, at the cost of wait time. Reset per-session state on release so conversations do not leak between users.

Either way, count active sessions yourself and queue or reject new connections before the platform does. A quota rejection surfaces as a connection failure, a worse experience than a visible queue position.
