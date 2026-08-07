# Sessions

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">Experimental</span>
</div>

A live agent is not a request and a response. It is a connection that stays open while
the user talks, listens, interrupts, and falls silent. This page covers the machinery
that keeps that connection alive: the lifecycle of a live application, the queue you
push user input into, the `run_live()` loop you read from, and what happens when a
connection drops or a conversation outgrows the model's context window.

Read this page when you are wiring up a live agent for the first time, or when you need
sessions to survive network failures and long conversations. For what comes *back* out
of the loop, see [Events](events.md). For the knobs that shape a session's behavior, see
[Configuration](configuration.md).

## Application lifecycle

ADK Gemini Live API Toolkit integrates Live API session into the ADK framework's application lifecycle. This integration creates a four-phase lifecycle that combines ADK's agent management with Live API's real-time streaming capabilities:

- **Phase 1: Application Initialization** (Once at Startup)
  - ADK Application initialization
    - Create an [Agent](/agents/): for interacting with users, utilize external tools, and coordinate with other agents.
    - Create a [SessionService](/sessions/session/#managing-sessions-with-a-sessionservice): for getting or creating ADK `Session`
    - Create a [Runner](/runtime/): for providing a runtime for the Agent

- **Phase 2: Session Initialization** (Once per User Session)
  - ADK `Session` initialization:
    - Get or Create an ADK `Session` using the `SessionService`
  - ADK Gemini Live API Toolkit initialization:
    - Create a [RunConfig](configuration.md) for configuring ADK Gemini Live API Toolkit
    - Create a [LiveRequestQueue](#liverequestqueue-and-liverequest) for sending user messages to the `Agent`
    - Start a [run_live()](#how-run_live-works) event loop

- **Phase 3: Bidi-streaming with `run_live()` event loop** (One or More Times per User Session)
  - Upstream: User sends message to the agent with `LiveRequestQueue`
  - Downstream: Agent responds to the user with `Event`

- **Phase 4: Terminate Live API session** (One or More Times per User Session)
  - `LiveRequestQueue.close()`

**Lifecycle Flow Overview:**

```mermaid
graph TD
    A[Phase 1: Application Init<br/>Once at Startup] --> B[Phase 2: Session Init<br/>Per User Connection]
    B --> C[Phase 3: Bidi-streaming<br/>Active Communication]
    C --> D[Phase 4: Terminate<br/>Close Session]
    D -.New Connection.-> B

    style A fill:#e3f2fd
    style B fill:#e8f5e9
    style C fill:#fff3e0
    style D fill:#ffebee
```

This flowchart shows the high-level lifecycle phases and how they connect. The detailed sequence diagram below illustrates the specific components and interactions within each phase.

```mermaid
sequenceDiagram
    participant Client
    participant App as Application Server
    participant Queue as LiveRequestQueue
    participant Runner
    participant Agent
    participant API as Live API

    rect rgb(230, 240, 255)
        Note over App: Phase 1: Application Initialization (Once at Startup)
        App->>Agent: 1. Create Agent(model, tools, instruction)
        App->>App: 2. Create SessionService()
        App->>Runner: 3. Create Runner(app_name, agent, session_service)
    end

    rect rgb(240, 255, 240)
        Note over Client,API: Phase 2: Session Initialization (Every Time a User Connected)
        Client->>App: 1. WebSocket connect(user_id, session_id)
        App->>App: 2. get_or_create_session(app_name, user_id, session_id)
        App->>App: 3. Create RunConfig(streaming_mode, modalities)
        App->>Queue: 4. Create LiveRequestQueue()
        App->>Runner: 5. Start run_live(user_id, session_id, queue, config)
        Runner->>API: Connect to Live API session
    end

    rect rgb(255, 250, 240)
        Note over Client,API: Phase 3: Bidi-streaming with run_live() Event Loop

        par Upstream: User sends messages via LiveRequestQueue
            Client->>App: User message (text/audio/video)
            App->>Queue: send_content() / send_realtime()
            Queue->>Runner: Buffered request
            Runner->>Agent: Process request
            Agent->>API: Stream to Live API
        and Downstream: Agent responds via Events
            API->>Agent: Streaming response
            Agent->>Runner: Process response
            Runner->>App: yield Event (text/audio/tool/turn)
            App->>Client: Forward Event via WebSocket
        end

        Note over Client,API: (Event loop continues until close signal)
    end

    rect rgb(255, 240, 240)
        Note over Client,API: Phase 4: Terminate Live API session
        Client->>App: WebSocket disconnect
        App->>Queue: close()
        Queue->>Runner: Close signal
        Runner->>API: Disconnect from Live API
        Runner->>App: run_live() exits
    end
```

In the following sections, you'll see each phase detailed, showing exactly when to create each component and how they work together. Understanding this lifecycle pattern is essential for building robust streaming applications that can handle multiple concurrent sessions efficiently.


### Phase 1: Application Initialization

These components are created once when your application starts and shared across all streaming sessions. They define your agent's capabilities, manage conversation history, and orchestrate the streaming execution.

#### Define Your Agent

The `Agent` is the core of your streaming application—it defines what your AI can do, how it should behave, and which AI model powers it. You configure your agent with a specific model, tools it can use (like Google Search or custom APIs), and instructions that shape its personality and behavior.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/google_search_agent/agent.py#L10-L15" target="_blank">agent.py:10-15</a>'
"""Google Search Agent definition for ADK Gemini Live API Toolkit demo."""

import os
from google.adk.agents import Agent
from google.adk.tools import google_search

# Default models for Live API with native audio support:
# - Gemini Live API: gemini-2.5-flash-native-audio-preview-12-2025
# - Gemini Live API (Agent Platform): gemini-live-2.5-flash-native-audio
agent = Agent(
    name="google_search_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[google_search],
    instruction="You are a helpful assistant that can search the web."
)
```

The agent instance is **stateless and reusable**—you create it once and use it for all streaming sessions. Agent configuration is covered in the [ADK Agent documentation](/agents/).

!!! note "Model Availability"

    For the latest supported models and their capabilities, see [Supported models](models.md).

!!! note "Agent vs LlmAgent"

    `Agent` is the recommended shorthand for `LlmAgent` (both are imported from `google.adk.agents`). They are identical - use whichever you prefer. This guide uses `Agent` for brevity, but you may see `LlmAgent` in other ADK documentation and examples.

#### Define Your SessionService

The ADK [Session](/sessions/session/) manages conversation state and history across streaming sessions. It stores and retrieves session data, enabling features like conversation resumption and context persistence.

To create a `Session`, or get an existing one for a specified `session_id`, every ADK application needs to have a [SessionService](/sessions/session/#managing-sessions-with-a-sessionservice). For development purpose, ADK provides a simple `InMemorySessionService` that will lose the `Session` state when the application shuts down.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L37" target="_blank">main.py:37</a>'
from google.adk.sessions import InMemorySessionService

# Define your session service
session_service = InMemorySessionService()
```

For production applications, choose a persistent session service based on your infrastructure:

**Use `DatabaseSessionService` if:**

- You need persistent storage with SQLite, PostgreSQL, or MySQL
- You're building single-server apps (SQLite) or multi-server deployments (PostgreSQL/MySQL)
- You want full control over data storage and backups
- Examples:
    - SQLite: `DatabaseSessionService(db_url="sqlite:///./sessions.db")`
    - PostgreSQL: `DatabaseSessionService(db_url="postgresql://user:pass@host/db")`

**Use `VertexAiSessionService` if:**

- You're already using Google Cloud Platform
- You want managed storage with built-in scalability
- You need tight integration with Agent Platform features
- Example: `VertexAiSessionService(project="my-project")`

Both provide session persistence capabilities—choose based on your infrastructure and scale requirements. With persistent session services, the state of the `Session` will be preserved even after application shutdown. See the [ADK Session Management documentation](/sessions/) for more details.

#### Define Your Runner

The [Runner](/runtime/) provides the runtime for the `Agent`. It manages the conversation flow, coordinates tool execution, handles events, and integrates with session storage. You create one runner instance at application startup and reuse it for all streaming sessions.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L50" target="_blank">main.py:50,53</a>'
from google.adk.runners import Runner

APP_NAME = "bidi-demo"

# Define your runner
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service
)
```

The `app_name` parameter is required and identifies your application in session storage. All sessions for your application are organized under this name.

### Phase 2: Session Initialization

#### Get or Create Session

ADK `Session` provides a "conversation thread" of the ADK Gemini Live API Toolkit application. Just like you wouldn't start every text message from scratch, agents need context regarding the ongoing interaction. `Session` is the ADK object designed specifically to track and manage these individual conversation threads.

##### ADK `Session` vs Live API session

ADK `Session` (managed by SessionService) provides **persistent conversation storage** across multiple Bidi-streaming sessions (can spans hours, days or even months), while Live API session (managed by Live API backend) is **a transient streaming context** that exists only during single Bidi-streaming event loop (spans minutes or hours typically) that we will discuss later. When the loop starts, ADK initializes the Live API session with history from the ADK `Session`, then updates the ADK `Session` as new events occur.

!!! note "Learn More"

    For a detailed comparison with sequence diagrams, see [ADK `Session` vs Live API session](#adk-session-vs-live-api-session).

##### Session Identifiers Are Application-Defined

Sessions are identified by three parameters: `app_name`, `user_id`, and `session_id`. This three-level hierarchy enables multi-tenant applications where each user can have multiple concurrent sessions.

Both `user_id` and `session_id` are **arbitrary string identifiers** that you define based on your application's needs. ADK performs no format validation beyond `.strip()` on `session_id`—you can use any string values that make sense for your application:

- **`user_id` examples**: User UUIDs (`"550e8400-e29b-41d4-a716-446655440000"`), email addresses (`"alice@example.com"`), database IDs (`"user_12345"`), or simple identifiers (`"demo-user"`)
- **`session_id` examples**: Custom session tokens, UUIDs, timestamp-based IDs (`"session_2025-01-27_143022"`), or simple identifiers (`"demo-session"`)

**Auto-generation**: If you pass `session_id=None` or an empty string to `create_session()`, ADK automatically generates a UUID for you (e.g., `"550e8400-e29b-41d4-a716-446655440000"`).

**Organizational hierarchy**: These identifiers organize sessions in a three-level structure:

```text
app_name → user_id → session_id → Session
```

This design enables scenarios like:

- Multi-tenant applications where different users have isolated conversation spaces
- Single users with multiple concurrent chat threads (e.g., different topics)
- Per-device or per-browser session isolation

##### Recommended Pattern: Get-or-Create

The recommended production pattern is to check if a session exists first, then create it only if needed. This approach safely handles both new sessions and conversation resumption:

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L155-L161" target="_blank">main.py:155-161</a>'
# Get or create session (handles both new sessions and reconnections)
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
```

This pattern works correctly in all scenarios:

- **New conversations**: If the session doesn't exist, it's created automatically
- **Resuming conversations**: If the session already exists (e.g., reconnection after network interruption), the existing session is reused with full conversation history
- **Idempotent**: Safe to call multiple times without errors

**Important**: The session must exist before calling `runner.run_live()` with the same identifiers. If the session doesn't exist, `run_live()` will raise `ValueError: Session not found`.

#### Create RunConfig

[RunConfig](configuration.md) defines the streaming behavior for this specific session—which modalities to use (text or audio), whether to enable transcription, voice activity detection, proactivity, and other advanced features.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L110-L124" target="_blank">main.py:110-124</a>'
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

# Native audio models require AUDIO response modality with audio transcription
response_modalities = ["AUDIO"]
run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=response_modalities,
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
    session_resumption=types.SessionResumptionConfig()
)
```

`RunConfig` is **session-specific**—each streaming session can have different configuration. For example, one user might prefer text-only responses while another uses voice mode. See [Configuration](configuration.md) for complete configuration options.

#### Create LiveRequestQueue

`LiveRequestQueue` is the communication channel for sending messages to the agent during streaming. It's a thread-safe async queue that buffers user messages (text content, audio blobs, activity signals) for orderly processing.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L163" target="_blank">main.py:163</a>'
from google.adk.agents.live_request_queue import LiveRequestQueue

live_request_queue = LiveRequestQueue()
```

`LiveRequestQueue` is **session-specific and stateful**—you create a new queue for each streaming session and close it when the session ends. Unlike `Agent` and `Runner`, queues cannot be reused across sessions.

!!! warning "One Queue Per Session"

    Never reuse a `LiveRequestQueue` across multiple streaming sessions. Each call to `run_live()` requires a fresh queue. Reusing queues can cause message ordering issues and state corruption.

    The close signal persists in the queue (see [`live_request_queue.py:66-67`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/agents/live_request_queue.py#L66-L67)) and terminates the sender loop (see [`base_llm_flow.py:628-630`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/flows/llm_flows/base_llm_flow.py#L628-L630)). Reusing a queue would carry over this signal and any remaining messages from the previous session.

### Phase 3: Bidi-streaming with `run_live()` event loop

Once the streaming loop is running, you can send messages to the agent and receive responses **concurrently**—this is Bidi-streaming in action. The agent can be generating a response while you're sending new input, enabling natural interruption-based conversation.

#### Send Messages to the Agent

Use `LiveRequestQueue` methods to send different types of messages to the agent during the streaming session:

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L169-L217" target="_blank">main.py:169-217</a>'
from google.genai import types

# Send text content
content = types.Content(parts=[types.Part(text=json_message["text"])])
live_request_queue.send_content(content)

# Send audio blob
audio_blob = types.Blob(
    mime_type="audio/pcm;rate=16000",
    data=audio_data
)
live_request_queue.send_realtime(audio_blob)
```

These methods are **non-blocking**—they immediately add messages to the queue without waiting for processing. This enables smooth, responsive user experiences even during heavy AI processing.

See [Sending different message types](#sending-different-message-types) for detailed API documentation.

#### Receive and Process Events

The `run_live()` async generator continuously yields `Event` objects as the agent processes input and generates responses. Each event represents a discrete occurrence—partial text generation, audio chunks, tool execution, transcription, interruption, or turn completion.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L219-L234" target="_blank">main.py:219-234</a>'
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config
):
    event_json = event.model_dump_json(exclude_none=True, by_alias=True)
    await websocket.send_text(event_json)
```

Events are designed for **streaming delivery**—you receive partial responses as they're generated, not just complete messages. This enables real-time UI updates and responsive user experiences.

See [Events](events.md) for comprehensive event handling patterns.

### Phase 4: Terminate Live API session

When the streaming session should end (user disconnects, conversation completes, timeout occurs), close the queue gracefully to signal termination to terminate the Live API session.

#### Close the Queue

Send a close signal through the queue to terminate the streaming loop:

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L253" target="_blank">main.py:253</a>'
live_request_queue.close()
```

This signals `run_live()` to stop yielding events and exit the async generator loop. The agent completes any in-progress processing and the streaming session ends cleanly.


## LiveRequestQueue and LiveRequest

The `LiveRequestQueue` is your primary interface for sending messages to the Agent in streaming conversations. Rather than managing separate channels for text, audio, and control signals, ADK provides a unified `LiveRequest` container that handles all message types through a single, elegant API:

```python title='Reference: <a href="../api-reference/python/google-adk.html#google.adk.agents.LiveRequestQueue">LiveRequestQueue</a>'
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

```mermaid
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

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L194-L199" target="_blank">main.py:194-199</a>'
content = types.Content(parts=[types.Part(text=json_message["text"])])
live_request_queue.send_content(content)
```

**Using Content and Part with ADK Gemini Live API Toolkit:**

- **`Content`** (`google.genai.types.Content`): A container that represents a single message or turn in the conversation. It holds an array of `Part` objects that together compose the complete message.

- **`Part`** (`google.genai.types.Part`): An individual piece of content within a message. For ADK Gemini Live API Toolkit with Live API, you'll use:
  - `text`: Text content (including code) that you send to the model

In practice, most messages use a single text Part for ADK Gemini Live API Toolkit. The multi-part structure is designed for scenarios like:
- Mixing text with function responses (automatically handled by ADK)
- Combining text explanations with structured data
- Future extensibility for new content types

For Live API, multimodal inputs (audio/video) use different mechanisms (see `send_realtime()` below), not multi-part Content.

!!! note "Content and Part Usage in ADK Gemini Live API Toolkit"
    
    While the Gemini API `Part` type supports many fields (`inline_data`, `file_data`, `function_call`, `function_response`, etc.), most are either handled automatically by ADK or use different mechanisms in Live API:
    
    - **Function calls**: ADK automatically handles the function calling loop - receiving function calls from the model, executing your registered functions, and sending responses back. You don't manually construct these.
    - **Images/Video**: Do NOT use `send_content()` with `inline_data`. Instead, use `send_realtime(Blob(mime_type="image/jpeg", data=...))` for continuous streaming. See [How to use image and video](audio-video.md#how-to-use-image-and-video).

### send_realtime(): Sends Audio, Image and Video in Real-Time

The `send_realtime()` method sends binary data streams—primarily audio, image and video—flow through the `Blob` type, which handles transmission in realtime mode. Unlike text content that gets processed in turn-by-turn mode, blobs are designed for continuous streaming scenarios where data arrives in chunks. You provide raw bytes, and Pydantic automatically handles base64 encoding during JSON serialization for safe network transmission (configured in `LiveRequest.model_config`). The MIME type helps the model understand the content format.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L181-L184" target="_blank">main.py:181-184</a>'
audio_blob = types.Blob(
    mime_type="audio/pcm;rate=16000",
    data=audio_data
)
live_request_queue.send_realtime(audio_blob)
```

!!! note "Learn More"
    
    For complete details on audio, image and video specifications, formats, and best practices, see [Audio and video](audio-video.md).

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

!!! note "Learn More"
    
    For detailed comparison of automatic VAD vs manual activity signals, including when to disable VAD and best practices, see [Voice activity detection](voice.md#voice-activity-detection-vad).

### Control Signals

The `close` signal provides graceful termination semantics for streaming sessions. It signals the system to cleanly close the model connection and end the Bidi-stream. In ADK Gemini Live API Toolkit, your application is responsible for sending the `close` signal explicitly:

**Manual closure in BIDI mode:** When using `StreamingMode.BIDI` (Bidi-streaming), your application should manually call `close()` when the session terminates or when errors occur. This practice minimizes session resource usage.

**Automatic closure in SSE mode:** When using the legacy `StreamingMode.SSE` (not Bidi-streaming), ADK automatically calls `close()` on the queue when it receives a `turn_complete=True` event from the model (see [`base_llm_flow.py:1150`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/flows/llm_flows/base_llm_flow.py#L1150)).

See [StreamingMode: BIDI or SSE](configuration.md#streamingmode-bidi-or-sse) for detailed comparison and when to use each mode.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L238-L253" target="_blank">main.py:238-253</a>'
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

!!! note "Learn More"
    
    For comprehensive error handling patterns during streaming, including when to use `break` vs `continue` and handling different error types, see [Error events](events.md#error-events).

## Concurrency and Thread Safety

Understanding how `LiveRequestQueue` handles concurrency is essential for building reliable streaming applications. The queue is built on `asyncio.Queue`, which means it's safe for concurrent access **within the same event loop thread** (the common case), but requires special handling when called from **different threads** (the advanced case). This section explains the design choices behind `LiveRequestQueue`'s API, when you can safely use it without extra precautions, and when you need thread-safety mechanisms like `loop.call_soon_threadsafe()`.

### Async Queue Management

`LiveRequestQueue` uses synchronous methods (`send_content()`, `send_realtime()`) instead of async methods, even though the underlying queue is consumed asynchronously. This design choice uses `asyncio.Queue.put_nowait()` - a non-blocking operation that doesn't require `await`.

**Why synchronous send methods?** Convenience and simplicity. You can call them from anywhere in your async code without `await`:

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L169-L199" target="_blank">main.py:169-199</a>'
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

| Guarantee | Description | Impact |
|-----------|-------------|--------|
| **FIFO ordering** | Messages processed in send order (guaranteed by underlying `asyncio.Queue`) | Maintains conversation context and interaction consistency |
| **No coalescing** | Each message delivered independently | No automatic batching—each send operation creates one request |
| **Unbounded by default** | Queue accepts unlimited messages without blocking | **Benefit**: Simplifies client code (no blocking on send)<br>**Risk**: Memory growth if sending faster than processing<br>**Mitigation**: Monitor queue depth in production |

> **Production Tip**: For high-throughput audio/video streaming, monitor `live_request_queue._queue.qsize()` to detect backpressure. If the queue depth grows continuously, slow down your send rate or implement batching. Note: `_queue` is an internal attribute and may change in future releases; use with caution.


## How run_live() Works

`run_live()` is an async generator that streams conversation events in real-time. It yields events immediately as they're generated—no buffering, no polling, no callbacks. Events are streamed without internal buffering. Overall memory depends on session persistence (e.g., in-memory vs database), making it suitable for both quick exchanges and extended sessions.

### Method Signature and Flow

**Usage:**

```python title='Reference: <a href="../api-reference/python/google-adk.html#google.adk.runners.Runner.run_live">Runner.run_live()</a>'
# The method signature reveals the thoughtful design
async def run_live(
    self,
    *,                                      # Keyword-only arguments
    user_id: Optional[str] = None,          # User identification (required unless session provided)
    session_id: Optional[str] = None,       # Session tracking (required unless session provided)
    live_request_queue: LiveRequestQueue,   # The bidirectional communication channel
    run_config: Optional[RunConfig] = None, # Streaming behavior configuration
    session: Optional[Session] = None,      # Deprecated: use user_id and session_id instead
) -> AsyncGenerator[Event, None]:           # Generator yielding conversation events
```

As its signature tells, every streaming conversation needs identity (user_id), continuity (session_id), communication (live_request_queue), and configuration (run_config). The return type—an async generator of Events—promises real-time delivery without overwhelming system resources.

```mermaid
sequenceDiagram
participant Client
participant Runner
participant Agent
participant LLMFlow
participant Gemini

Client->>Runner: runner.run_live(user_id, session_id, queue, config)
Runner->>Agent: agent.run_live(context)
Agent->>LLMFlow: _llm_flow.run_live(context)
LLMFlow->>Gemini: Connect and stream

loop Continuous Streaming
    Gemini-->>LLMFlow: LlmResponse
    LLMFlow-->>Agent: Event
    Agent-->>Runner: Event
    Runner-->>Client: Event (yield)
end
```

### Basic Usage Pattern

The simplest way to consume events from `run_live()` is to iterate over the async generator with a for-loop:

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L225-L233" target="_blank">main.py:225-233</a>'
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config
):
    event_json = event.model_dump_json(exclude_none=True, by_alias=True)
    logger.debug(f"[SERVER] Event: {event_json}")
    await websocket.send_text(event_json)
```

!!! note "Session Identifiers"

    Both `user_id` and `session_id` must match the identifiers you used when creating the session via `SessionService.create_session()`. These can be any string values based on your application's needs (e.g., UUIDs, email addresses, custom tokens). See [Get or Create Session](#get-or-create-session) for detailed guidance on session identifiers.

### Connection Lifecycle in run_live()

The `run_live()` method manages the underlying Live API connection lifecycle automatically:

**Connection States:**
1. **Initialization**: Connection established when `run_live()` is called
2. **Active Streaming**: Bidirectional communication via `LiveRequestQueue` (upstream to the model) and `run_live()` (downstream from the model)
3. **Graceful Closure**: Connection closes when `LiveRequestQueue.close()` is called
4. **Error Recovery**: ADK supports transparent session resumption; enable via `RunConfig.session_resumption` to handle transient failures. See [Live API session resumption](#live-api-session-resumption) for details.

#### What run_live() Yields

The `run_live()` method yields a stream of `Event` objects in real-time as the agent processes user input and generates responses. Understanding the different event types helps you build responsive UIs that handle text, audio, transcriptions, tool calls, metadata, and errors appropriately. Each event type is explained in detail in [Events](events.md).

| Event Type | Description |
|------------|-------------|
| **[Text events](events.md#text-events)** | Model's text responses when using `response_modalities=["TEXT"]`; includes `partial`, `turn_complete`, and `interrupted` flags for streaming UI management |
| **[Audio events with inline data](events.md#audio-events)** | Raw audio bytes (`inline_data`) streamed in real-time when using `response_modalities=["AUDIO"]`; ephemeral (not persisted to session) |
| **[Audio events with file data](events.md#audio-events-with-file-data)** | Audio aggregated into files and stored in artifacts; contains `file_data` references instead of raw bytes; can be persisted to session history |
| **[Metadata events](events.md#metadata-events)** | Token usage information (`prompt_token_count`, `candidates_token_count`, `total_token_count`) for cost monitoring and quota tracking |
| **[Transcription events](events.md#transcription-events)** | Speech-to-text for user input (`input_transcription`) and model output (`output_transcription`) when transcription is enabled in `RunConfig` |
| **[Tool call events](events.md#tool-call-events)** | Function call requests from the model; ADK handles execution automatically |
| **[Error events](events.md#error-events)** | Model errors and connection issues with `error_code` and `error_message` fields |

!!! note "Source Reference"

    See the complete event type handling implementation in [`runners.py`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/runners.py)

#### When run_live() Exits

The `run_live()` event loop can exit under various conditions. Understanding these exit scenarios is crucial for proper resource cleanup and error handling:

| Exit Condition | Trigger | Graceful? | Description |
|---|---|---|---|
| **Manual close** | `live_request_queue.close()` | ✅ Yes | User explicitly closes the queue, sending `LiveRequest(close=True)` signal |
| **All agents complete** | Last agent in SequentialAgent calls `task_completed()` | ✅ Yes | After all sequential agents finish their tasks |
| **Session timeout** | Live API duration limit reached | ⚠️ Connection closed | Session exceeds maximum duration (see limits below) |
| **Early exit** | `end_invocation` flag set | ✅ Yes | Set during preprocessing or by tools/callbacks to terminate early |
| **Empty event** | Queue closure signal | ✅ Yes | Internal signal indicating event stream has ended |
| **Errors** | Connection errors, exceptions | ❌ No | Unhandled exceptions or connection failures |

!!! warning "SequentialAgent Behavior"

    When using `SequentialAgent`, the `task_completed()` function does NOT exit your application's `run_live()` loop. It only signals the end of the current agent's work, triggering a seamless transition to the next agent in the sequence. Your event loop continues receiving events from subsequent agents. The loop only exits when the **last** agent in the sequence completes.

!!! note "Learn More"

    For session resumption and connection recovery details, see [Live API session resumption](#live-api-session-resumption). For multi-agent workflows, see [Best practices for multi-agent workflows](workflows.md#best-practices-for-multi-agent-workflows).

#### Events Saved to ADK `Session`

Not all events yielded by `run_live()` are persisted to the ADK `Session`. When `run_live()` exits, only certain events are saved to the session while others remain ephemeral. Understanding which events are saved versus which are ephemeral is crucial for applications that use session persistence, resumption, or need to review conversation history.

!!! note "Source Reference"

    See session event persistence logic in [`runners.py`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/runners.py)

**Events Saved to the ADK `Session`:**

These events are persisted to the ADK `Session` and available in session history:

- **Audio Events with File Data**: Saved to ADK `Session` only if `RunConfig.save_live_blob` is `True`; audio data is aggregated into files in artifacts with `file_data` references
- **Usage Metadata Events**: Always saved to track token consumption across the ADK `Session`
- **Non-Partial Transcription Events**: Final transcriptions are saved; partial transcriptions are not persisted
- **Function Call and Response Events**: Always saved to maintain tool execution history
- **Other Control Events**: Most control events (e.g., `turn_complete`, `finish_reason`) are saved

**Events NOT Saved to the ADK `Session`:**

These events are ephemeral and only yielded to callers during active streaming:

- **Audio Events with Inline Data**: Raw audio `Blob` data in `inline_data` is never saved to the ADK `Session` (only yielded for real-time playback)
- **Partial Transcription Events**: Only yielded for real-time display; final transcriptions are saved

!!! note "Audio Persistence"

    To save audio conversations to the ADK `Session` for review or resumption, enable `RunConfig.save_live_blob = True`. This persists audio streams to artifacts. See [save_live_blob](configuration.md#save_live_blob) for configuration details.


## Understanding Live API Connections and Sessions

When building ADK Gemini Live API Toolkit applications, it's essential to understand how ADK manages the communication layer between itself and the  Live API backend. This section explores the fundamental distinction between **connections** (the WebSocket transport links that ADK establishes to Live API) and **sessions** (the logical conversation contexts maintained by Live API). Unlike traditional request-response APIs, the Bidi-streaming architecture introduces unique constraints: connection timeouts, session duration limits that vary by modality (audio-only vs audio+video), finite context windows, and concurrent session quotas that differ between Gemini Live API and Gemini Live API (Agent Platform).

### ADK `Session` vs Live API Session

Understanding the distinction between **ADK `Session`** and **Live API session** is crucial for building reliable streaming applications with ADK Gemini Live API Toolkit.

**ADK `Session`** (managed by SessionService):
- Persistent conversation storage for conversation history, events, and state, created via `SessionService.create_session()`
- Storage options: in-memory, database (PostgreSQL/MySQL/SQLite), or Agent Platform
- Survives across multiple `run_live()` calls and application restarts (with the persistent `SessionService`)

**Live API session** (managed by Live API backend):
- Maintained by the Live API during the `run_live()` event loop is running, and destroyed when streaming ends by calling `LiveRequestQueue.close()`
- Subject to platform duration limits, and can be resumed across multiple connections using session resumption handles (see [How ADK Manages Session Resumption](#how-adk-manages-session-resumption) below)

**How they work together:**

1. **When `run_live()` is called:**
   - Retrieves the ADK `Session` from `SessionService`
   - Initializes the Live API session with conversation history from `session.events`
   - Streams events bidirectionally with the Live API backend
   - Updates the ADK `Session` with new events as they occur
2. **When `run_live()` ends**
   - The Live API session terminates
   - The ADK `Session` persists
3. **When `run_live()` is called again** or **the application is restarted**:
    - ADK loads the history from the ADK `Session`
    - Creates a new Live API session with that context

In short, ADK `Session` provides persistent, long-term conversation storage, while Live API sessions are ephemeral streaming contexts. This separation enables production applications to maintain conversation continuity across network interruptions, application restarts, and multiple streaming sessions.

The following diagram illustrates the relationship between ADK Session persistence and ephemeral Live API session contexts, showing how conversation history is maintained across multiple `run_live()` calls:

```mermaid
sequenceDiagram
    participant App as Your Application
    participant SS as SessionService
    participant ADK_Session as ADK Session<br/>(Persistent Storage)
    participant ADK as ADK (run_live)
    participant LiveSession as Live API Session<br/>(Ephemeral)

    Note over App,LiveSession: First run_live() call

    App->>SS: get_session(user_id, session_id)
    SS->>ADK_Session: Load session data
    ADK_Session-->>SS: Session with events history
    SS-->>App: Session object

    App->>ADK: runner.run_live(...)
    ADK->>LiveSession: Initialize with history from ADK Session
    activate LiveSession

    Note over ADK,LiveSession: Bidirectional streaming...

    ADK->>ADK_Session: Update with new events

    App->>ADK: queue.close()
    ADK->>LiveSession: Terminate
    deactivate LiveSession
    Note over LiveSession: Live API session destroyed
    Note over ADK_Session: ADK Session persists

    Note over App,LiveSession: Second run_live() call (or after restart)

    App->>SS: get_session(user_id, session_id)
    SS->>ADK_Session: Load session data
    ADK_Session-->>SS: Session with events history
    SS-->>App: Session object (with previous history)

    App->>ADK: runner.run_live(...)
    ADK->>LiveSession: Initialize new session with full history
    activate LiveSession

    Note over ADK,LiveSession: Bidirectional streaming continues...
```

**Key insights:**
- ADK Session survives across multiple `run_live()` calls and app restarts
- Live API session is ephemeral - created and destroyed per streaming session
- Conversation continuity is maintained through ADK Session's persistent storage
- SessionService manages the persistence layer (in-memory, database, or Agent Platform)

Now that we understand the difference between ADK `Session` objects and Live API sessions, let's focus on Live API connections and sessions—the backend infrastructure that powers real-time bidirectional streaming.

### Live API Connections and Sessions

Understanding the distinction between **connections** and **sessions** at the Live API level is crucial for building reliable ADK Gemini Live API Toolkit applications.

**Connection**: The physical WebSocket link between ADK and the Live API server. This is the network transport layer that carries bidirectional streaming data.

**Session**: The logical conversation context maintained by the Live API, including conversation history, tool call state, and model context. A session can span multiple connections.

| **Aspect** | **Connection** | **Session** |
|--------|-----------|---------|
| **What is it?** | WebSocket network connection | Logical conversation context |
| **Scope** | Transport layer | Application layer |
| **Can span?** | Single network link | Multiple connections via resumption |
| **Failure impact** | Network error or timeout | Lost conversation history |

#### Live API Connection and Session Limits by Platform

Understanding the constraints of each platform is critical for production planning. Gemini Live API and Gemini Live API (Agent Platform) have different limits that affect how long conversations can run and how many users can connect simultaneously. The most important distinction is between **connection duration** (how long a single WebSocket connection stays open) and **session duration** (how long a logical conversation can continue).

| Constraint Type | Gemini Live API<br>(Google AI Studio) | Gemini Live API<br>(Agent Platform) | Notes |
|----------------|---------------------------------------|--------------------------------------|-------|
| **Connection duration** | ~10 minutes | Not documented separately | Each Gemini WebSocket connection auto-terminates; ADK reconnects transparently with session resumption |
| **Session Duration (Audio-only)** | 15 minutes | 10 minutes | Maximum session duration without context window compression. Both platforms: unlimited with context window compression enabled |
| **Session Duration (Audio + video)** | 2 minutes | 10 minutes | Gemini has shorter limit for video; Agent Platform treats all sessions equally. Both platforms: unlimited with context window compression enabled |
| **Concurrent sessions** | 50 (Tier 1)<br>1,000 (Tier 2+) | Up to 1,000 | Gemini limits vary by API tier; Agent Platform limit is per Google Cloud project |

!!! note "Source References"

    - [Gemini Live API Capabilities Guide](https://ai.google.dev/gemini-api/docs/live-guide)
    - [Gemini API Quotas](https://ai.google.dev/gemini-api/docs/quota)
    - [Gemini Live API (Agent Platform)](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## Live API Session Resumption

By default, the Live API limits connection duration to approximately 10 minutes—each WebSocket connection automatically closes after this duration. To overcome this limit and enable longer conversations, the **Live API provides [Session Resumption](https://ai.google.dev/gemini-api/docs/live#session-resumption)**, a feature that transparently migrates a session across multiple connections. When enabled, the Live API generates resumption handles that allow reconnecting to the same session context, preserving the full conversation history and state.

**ADK automates this entirely**: When you enable session resumption in RunConfig, ADK automatically handles all reconnection logic—detecting connection closures, caching resumption handles, and reconnecting seamlessly in the background. You don't need to write any reconnection code. Sessions continue seamlessly beyond the 10-minute connection limit, handling connection timeouts, network disruptions, and planned reconnections automatically.

### Scope of ADK's Reconnection Management

ADK manages the **ADK-to-Live API connection** (the WebSocket between ADK and the Gemini Live API backend). This is transparent to your application code.

**Your application remains responsible for**:

- Managing client connections to your application (e.g., user's WebSocket to your FastAPI server)
- Implementing client-side reconnection logic if needed
- Handling network failures between clients and your application

When ADK reconnects to the Live API, your application's event loop continues normally—you keep receiving events from `run_live()` without interruption. From your application's perspective, the Live API session continues seamlessly.

**Configuration:**

```python
from google.genai import types

run_config = RunConfig(
    session_resumption=types.SessionResumptionConfig()
)
```

**When NOT to Enable Session Resumption:**

While session resumption is recommended for most production applications, consider these scenarios where you might not need it:

- **Short sessions (<10 minutes)**: If your sessions typically complete within the ~10 minute connection timeout, resumption adds unnecessary overhead
- **Stateless interactions**: Request-response style interactions where each turn is independent don't benefit from session continuity
- **Development/testing**: Simpler debugging when each session starts fresh without carrying over state
- **Cost-sensitive deployments**: Session resumption may incur additional platform costs or resource usage (verify with your platform)

**Best practice**: Enable session resumption by default for production, disable only when you have a specific reason not to use it.

### How ADK Manages Session Resumption

While session resumption is supported by both Gemini Live API and Gemini Live API (Agent Platform), using it directly requires managing resumption handles, detecting connection closures, and implementing reconnection logic. ADK takes full responsibility for this complexity, automatically utilizing session resumption behind the scenes so developers don't need to write any reconnection code. You simply enable it in RunConfig, and ADK handles everything transparently.

**ADK's automatic management:**

1. **Initial Connection**: ADK establishes a WebSocket connection to Live API
2. **Handle Updates**: Throughout the session, the Live API sends `session_resumption_update` messages containing updated handles. ADK automatically caches the latest handle in `InvocationContext.live_session_resumption_handle`
3. **Graceful Connection Close**: When the ~10 minute connection limit is reached, the WebSocket closes gracefully (no exception)
4. **Automatic Reconnection**: ADK's internal loop detects the close and automatically reconnects using the most recent cached handle
5. **Session Continuation**: The same session continues seamlessly with full context preserved

!!! note "Implementation Detail"

    During reconnection, ADK retrieves the cached handle from `InvocationContext.live_session_resumption_handle` and includes it in the new `LiveConnectConfig` for the `live.connect()` call. This is handled entirely by ADK's internal reconnection loop—developers never need to access or manage these handles directly.

### Sequence Diagram: Automatic Reconnection

The following sequence diagram illustrates how ADK automatically manages Live API session resumption when the ~10 minute connection timeout is reached. ADK detects the graceful close, retrieves the cached resumption handle, and reconnects transparently without application code changes:

```mermaid
sequenceDiagram
    participant App as Your Application
    participant ADK as ADK (run_live)
    participant WS as WebSocket Connection
    participant API as Live API (Gemini/Agent Platform)
    participant LiveSession as Live Session Context

    Note over App,LiveSession: Initial Connection (with session resumption enabled)

    App->>ADK: runner.run_live(run_config=RunConfig(session_resumption=...))
    ADK->>API: WebSocket connect()
    activate WS
    API->>LiveSession: Create new session
    activate LiveSession

    Note over ADK,API: Bidirectional Streaming (0-10 minutes)

    App->>ADK: send_content(text) / send_realtime(audio)
    ADK->>API: → Content via WebSocket
    API->>LiveSession: Update conversation history
    API-->>ADK: ← Streaming response
    ADK-->>App: ← yield event

    Note over API,LiveSession: Live API sends resumption handle updates
    API-->>ADK: session_resumption_update { new_handle: "abc123" }
    ADK->>ADK: Cache handle in InvocationContext

    Note over WS,API: ~10 minutes elapsed - Connection timeout

    API->>WS: Close WebSocket (graceful close)
    deactivate WS
    Note over LiveSession: Session context preserved

    Note over ADK: Graceful close detected - No exception raised
    ADK->>ADK: while True loop continues

    Note over ADK,API: Automatic Reconnection

    ADK->>API: WebSocket connect(session_resumption.handle="abc123")
    activate WS
    API->>LiveSession: Attach to existing session
    API-->>ADK: Session resumed with full context

    Note over ADK,API: Bidirectional Streaming Continues

    App->>ADK: send_content(text) / send_realtime(audio)
    ADK->>API: → Content via WebSocket
    API->>LiveSession: Update conversation history
    API-->>ADK: ← Streaming response
    ADK-->>App: ← yield event

    Note over App,LiveSession: Session continues until duration limit or explicit close

    deactivate WS
    deactivate LiveSession
```

!!! note "Events and Session Persistence"

    For details on which events are saved to the ADK `Session` versus which are only yielded during streaming, see [Events saved to ADK `Session`](#events-saved-to-adk-session).

## Live API Context Window Compression

**Problem:** Live API sessions face two critical constraints that limit conversation duration. First, **session duration limits** impose hard time caps: without compression, Gemini Live API limits audio-only sessions to 15 minutes and audio+video sessions to just 2 minutes, while Agent Platform limits all sessions to 10 minutes. Second, **context window limits** restrict conversation length: models have finite token capacities (128k tokens for `gemini-2.5-flash-native-audio-preview-12-2025`, 32k-128k for Agent Platform models). Long conversations—especially extended customer support sessions, tutoring interactions, or multi-hour voice dialogues—will hit either the time limit or the token limit, causing the session to terminate or lose critical conversation history.

**Solution:** [Context window compression](https://ai.google.dev/gemini-api/docs/live-session#context-window-compression) solves both constraints simultaneously. It uses a sliding-window approach to automatically compress or summarize earlier conversation history when the token count reaches a configured threshold. The Live API preserves recent context in full detail while compressing older portions. **Critically, enabling context window compression extends session duration to unlimited time**, removing the session duration limits (15 minutes for audio-only / 2 minutes for audio+video on Gemini Live API; 10 minutes for all sessions on Agent Platform) while also preventing token limit exhaustion. However, there is a trade-off: as the feature summarizes earlier conversation history rather than retaining it all, the detail of past context will be gradually lost over time. The model will have access to compressed summaries of older exchanges, not the full verbatim history.

### Platform Behavior and Official Limits

Session duration management and context window compression are **Live API platform features**. ADK configures these features via RunConfig and passes the configuration to the Live API, but the actual enforcement and implementation are handled by the Gemini Live API backends.

**Important**: The duration limits and "unlimited" session behavior mentioned in this guide are based on current Live API behavior. These limits are subject to change by Google. Always verify current session duration limits and compression behavior in the official documentation:

- [Gemini Live API Documentation](https://ai.google.dev/gemini-api/docs/live)
- [Gemini Live API (Agent Platform) Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

ADK provides an easy way to configure context window compression through RunConfig. However, developers are responsible for appropriately configuring the compression parameters (`trigger_tokens` and `target_tokens`) based on their specific requirements—model context window size, expected conversation patterns, and quality needs:

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

# For gemini-2.5-flash-native-audio-preview-12-2025 (128k context window)
run_config = RunConfig(
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=100000,  # Start compression at ~78% of 128k context
        sliding_window=types.SlidingWindow(
            target_tokens=80000  # Compress to ~62% of context, preserving recent turns
        )
    )
)
```

**How it works:**

When context window compression is enabled:

1. The Live API monitors the total token count of the conversation context
2. When the context reaches the `trigger_tokens` threshold, compression activates
3. Earlier conversation history is compressed or summarized using a sliding window approach
4. Recent context (last `target_tokens` worth) is preserved in full detail
5. **Two critical effects occur simultaneously:**
   - Session duration limits are removed (no more 15-minute/2-minute caps on Gemini Live API or 10-minute caps on Agent Platform)
   - Token limits are managed (sessions can continue indefinitely regardless of conversation length)

**Choosing appropriate thresholds:**

- Set `trigger_tokens` to 70-80% of your model's context window to allow headroom
- Set `target_tokens` to 60-70% to provide sufficient compression
- Test with your actual conversation patterns to optimize these values

**Parameter Selection Strategy:**

The examples above use 78% for `trigger_tokens` and 62% for `target_tokens`. Here's the reasoning:

1. **trigger_tokens at 78%**: Provides a buffer before hitting the hard limit
   - Allows room for the current turn to complete
   - Prevents mid-response compression interruptions
   - Typical conversations can continue for several more turns

2. **target_tokens at 62%**: Leaves substantial room after compression
   - 16 percentage points (78% - 62%) freed up per compression
   - Allows for multiple turns before next compression
   - Balances preservation of context with compression frequency

3. **Adjusting for your use case**:
   - **Long turns** (detailed technical discussions): Increase buffer → 70% trigger, 50% target
   - **Short turns** (quick Q&A): Tighter margins → 85% trigger, 70% target
   - **Context-critical** (requires historical detail): Higher target → 80% trigger, 70% target
   - **Performance-sensitive** (minimize compression overhead): Lower trigger → 70% trigger, 50% target

Always test with your actual conversation patterns to find optimal values.

### When NOT to Use Context Window Compression

While compression enables unlimited session duration, consider these trade-offs:

**Context Window Compression Trade-offs:**

| Aspect | With Compression | Without Compression | Best For |
|--------|------------------|---------------------|----------|
| **Session Duration** | Unlimited | 15 min (audio)<br>2 min (video) Gemini<br>10 min Agent Platform | Compression: Long sessions<br>No compression: Short sessions |
| **Context Quality** | Older context summarized | Full verbatim history | Compression: General conversation<br>No compression: Precision-critical |
| **Latency** | Compression overhead | No overhead | Compression: Async scenarios<br>No compression: Real-time |
| **Memory Usage** | Bounded | Grows with session | Compression: Long sessions<br>No compression: Short sessions |
| **Implementation** | Configure thresholds | No configuration | Compression: Production<br>No compression: Prototypes |

**Common Use Cases:**

✅ **Enable compression when:**
- Sessions need to exceed platform duration limits (15/2/10 minutes)
- Extended conversations may hit token limits (128k for 2.5-flash)
- Customer support sessions that can last hours
- Educational tutoring with long interactions

❌ **Disable compression when:**
- All sessions complete within duration limits
- Precision recall of early conversation is critical
- Development/testing phase (full history aids debugging)
- Quality degradation from summarization is unacceptable

**Best practice**: Enable compression only when you need sessions longer than platform duration limits OR when conversations may exceed context window token limits.

## Best Practices for Live API Connection and Session Management

### Essential: Enable Session Resumption

- ✅ **Always enable session resumption** in RunConfig for production applications
- ✅ This enables ADK to automatically handle Gemini's ~10 minute connection timeouts transparently
- ✅ Sessions continue seamlessly across multiple WebSocket connections without user interruption
- ✅ Session resumption handle caching and management

```python
from google.genai import types

run_config = RunConfig(
    response_modalities=["AUDIO"],
    session_resumption=types.SessionResumptionConfig()
)
```

### Recommended: Enable Context Window Compression for Unlimited Sessions

- ✅ **Enable context window compression** if you need sessions longer than 15 minutes (audio-only) or 2 minutes (audio+video)
- ✅ Once enabled, session duration becomes unlimited—no need to monitor time-based limits
- ✅ Configure `trigger_tokens` and `target_tokens` based on your model's context window
- ✅ Test compression settings with realistic conversation patterns
- ⚠️ **Use judiciously**: Compression adds latency during summarization and may lose conversational nuance—only enable when extended sessions are truly necessary for your use case

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    session_resumption=types.SessionResumptionConfig(),
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=100000,
        sliding_window=types.SlidingWindow(target_tokens=80000)
    )
)
```

### Optional: Monitor Session Duration

**Only applies if NOT using context window compression:**

- ✅ Focus on **session duration limits**, not connection timeouts (ADK handles those automatically)
- ✅ **Gemini Live API**: Monitor for 15-minute limit (audio-only) or 2-minute limit (audio+video)
- ✅ **Gemini Live API (Agent Platform)**: Monitor for 10-minute session limit
- ✅ Warn users 1-2 minutes before session duration limits
- ✅ Implement graceful session transitions for conversations exceeding session limits

## Concurrent Live API Sessions and Quota Management

**Problem:** Production voice applications typically serve multiple users simultaneously, each requiring their own Live API session. However, both Gemini Live API and Gemini Live API (Agent Platform) impose strict concurrent session limits that vary by platform and pricing tier. Without proper quota planning and session management, applications can hit these limits quickly, causing connection failures for new users or degraded service quality during peak usage.

**Solution:** Understand platform-specific quotas, design your architecture to stay within concurrent session limits, implement session pooling or queueing strategies when needed, and monitor quota usage proactively. ADK handles individual session lifecycle automatically, but developers must architect their applications to manage multiple concurrent users within quota constraints.

### Understanding Concurrent Live API Session Quotas

Both platforms limit how many Live API sessions can run simultaneously, but the limits and mechanisms differ significantly:

**Gemini Live API (Google AI Studio) - Tier-based quotas:**

| **Tier** | **Concurrent Sessions** | **TPM (Tokens Per Minute)** | **Access** |
|----------|------------------------:|----------------------------:|------------|
| **Free Tier** | Limited* | 1,000,000 | Free API key |
| **Tier 1** | 50 | 4,000,000 | Pay-as-you-go |
| **Tier 2** | 1,000 | 10,000,000 | Higher usage tier |
| **Tier 3** | 1,000 | 10,000,000 | Higher usage tier |

*Free tier concurrent session limits are not explicitly documented but are significantly lower than paid tiers.

!!! note "Source"

    [Gemini API Quotas](https://ai.google.dev/gemini-api/docs/quota)

**Gemini Live API (Agent Platform) - Project-based quotas:**

| **Resource Type** | **Limit** | **Scope** |
|---------------|------:|-------|
| **Concurrent live bidirectional connections** | 10 per minute | Per project, per region |
| **Maximum concurrent sessions** | Up to 1,000 | Per project |
| **Session creation/deletion/update** | 100 per minute | Per project, per region |

!!! note "Source"

    [Gemini Live API (Agent Platform)](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api) | [Agent Platform Quotas](https://cloud.google.com/vertex-ai/generative-ai/docs/quotas)

**Requesting a quota increase:**

To request an increase for Live API concurrent sessions, navigate to the [Quotas page](https://console.cloud.google.com/iam-admin/quotas) in the Google Cloud Console. Filter for the quota named **"Bidi generate content concurrent requests"** to find quota values for each project, region and base model, and submit a quota increase request. You'll need the Quota Administrator role (`roles/servicemanagement.quotaAdmin`) to make the request. See [View and manage quotas](https://cloud.google.com/docs/quotas/view-manage) for detailed instructions.

![Quota value on Cloud Console](assets/adk-streaming-guide-quota-console.png)

**Key differences:**

1. **Gemini Live API**: Concurrent session limits scale dramatically with API tier (50 → 1,000 sessions). Best for applications with unpredictable or rapidly scaling user bases willing to pay for higher tiers.

2. **Gemini Live API (Agent Platform)**: Rate-limited by connection establishment rate (10/min) but supports up to 1,000 total concurrent sessions. Best for enterprise applications with gradual scaling patterns and existing Google Cloud infrastructure. Additionally, you can request quota increases to prepare for production deployments with higher concurrency requirements.

### Architectural Patterns for Managing Quotas

Once you understand your concurrent session quotas, the next challenge is architecting your application to operate effectively within those limits. The right approach depends on your expected user concurrency, scaling requirements, and tolerance for queueing. This section presents two architectural patterns—from simple direct mapping for low-concurrency applications to session pooling with queueing for applications that may exceed quota limits during peak usage. Choose the pattern that matches your current scale and design it to evolve as your user base grows.

**Choosing the Right Architecture:**

```text
                Start: Designing Quota Management
                              |
                              v
                   Expected Concurrent Users?
                     /                    \
            < Quota Limit           > Quota Limit or Unpredictable
                   |                              |
                   v                              v
          Pattern 1: Direct Mapping    Pattern 2: Session Pooling
          - Simple 1:1 mapping         - Queue waiting users
          - No quota logic             - Graceful degradation
          - Fast development           - Peak handling
                   |                              |
                   v                              v
              Good for:                      Good for:
              - Prototypes                   - Production at scale
              - Small teams                  - Unpredictable load
              - Controlled users             - Public applications
```

**Quick Decision Guide:**

| Factor | Direct Mapping | Session Pooling |
|--------|----------------|-----------------|
| **Expected users** | Always < quota | May exceed quota |
| **User experience** | Always instant | May wait during peaks |
| **Implementation complexity** | Low | Medium |
| **Operational overhead** | None | Monitor queue depth |
| **Best for** | Prototypes, internal tools | Production, public apps |

#### Pattern 1: Direct Mapping (Simple Applications)

For small-scale applications where concurrent users will never exceed quota limits, create a dedicated Live API session for each connected user with a simple 1:1 mapping:

1. **When a user connects:** Immediately start a `run_live()` session for them
2. **When they disconnect:** The session ends
3. **No quota management logic:** Assumes your total concurrent users will always stay below your quota limits

This is the simplest possible architecture and works well for prototypes, development environments, and small-scale applications with predictable user loads.

#### Pattern 2: Session Pooling with Queueing

For applications that may exceed concurrent session limits during peak usage, track the number of active Live API sessions and enforce your quota limit at the application level:

1. **When a new user connects:** Check if you have available session slots
2. **If slots are available:** Start a session immediately
3. **If you've reached your quota limit:**
   - Place the user in a waiting queue
   - Notify them they're waiting for an available slot
4. **As sessions end:** Automatically process the queue to start sessions for waiting users

This provides graceful degradation—users wait briefly during peak times rather than experiencing hard connection failures.

