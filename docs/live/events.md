# Events

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">Experimental</span>
</div>

Everything a live agent produces reaches your application as an `Event`: partial text as
the model composes it, raw audio bytes, transcriptions of both sides of the conversation,
tool calls, token counts, and errors. A single spoken reply can arrive as dozens of
events, and handling them correctly is what makes a voice interface feel immediate rather
than laggy.

This page covers the `Event` class, the event types you will encounter, how to render
streaming text without duplicating it, and how to serialize events for transport to a
browser or mobile client. For the loop that yields these events, see
[Sessions](sessions.md).

## Understanding Events

Events are the core communication mechanism in ADK Gemini Live API Toolkit's streaming system. This section explores the complete lifecycle of events—from how they're generated through multiple pipeline layers, to concurrent processing patterns that enable true real-time interaction, to practical handling of interruptions and turn completion. You'll learn about event types (text, audio, transcriptions, tool calls), serialization strategies for network transport, and the connection lifecycle that manages streaming sessions across both Gemini Live API and Gemini Live API platforms.

### The Event Class

ADK's `Event` class is a Pydantic model that represents all communication in a streaming conversation. It extends `LlmResponse` and serves as the unified container for model responses, user input, transcriptions, and control signals.

!!! note "Source Reference"

    See Event class implementation in [`event.py:30-128`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/events/event.py#L30-L128) and [`llm_response.py:28-200`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/models/llm_response.py#L28-L200)

#### Key Fields

**Essential for all applications:**
- `content`: Contains text, audio, or function calls as `Content.parts`
- `author`: Identifies who created the event (`"user"` or agent name)
- `partial`: Distinguishes incremental chunks from complete text
- `turn_complete`: Signals when to enable user input again
- `interrupted`: Indicates when to stop rendering current output

**For voice/audio applications:**
- `input_transcription`: User's spoken words (when enabled in `RunConfig`)
- `output_transcription`: Model's spoken words (when enabled in `RunConfig`)
- `content.parts[].inline_data`: Audio data for playback

**For tool execution:**
- `content.parts[].function_call`: Model's tool invocation requests
- `content.parts[].function_response`: Tool execution results
- `long_running_tool_ids`: Track async tool execution

**For debugging and diagnostics:**
- `usage_metadata`: Token counts and billing information
- `cache_metadata`: Context cache hit/miss statistics
- `finish_reason`: Why the model stopped generating (e.g., STOP, MAX_TOKENS, SAFETY)
- `error_code` / `error_message`: Failure diagnostics

!!! note "Author Semantics"

    Transcription events have author `"user"`; model responses/events use the agent's name as `author` (not `"model"`). See [Event Authorship](#event-authorship) for details.

#### Understanding Event Identity

Events have two important ID fields:

- **`event.id`**: Unique identifier for this specific event (format: UUID). Each event gets a new ID, even partial text chunks.
- **`event.invocation_id`**: Shared identifier for all events in the current invocation (format: `"e-" + UUID`). In `run_live()`, all events from a single streaming session share the same invocation_id. (See [InvocationContext](#invocationcontext-the-execution-state-container) for more about invocations)

**Usage:**

```python
# All events in this streaming session will have the same invocation_id
async for event in runner.run_live(...):
    print(f"Event ID: {event.id}")              # Unique per event
    print(f"Invocation ID: {event.invocation_id}")  # Same for all events in session
```

**Use cases:**
- **event.id**: Track individual events in logs, deduplicate events
- **event.invocation_id**: Group events by conversation session, filter session-specific events

### Event Authorship

In live streaming mode, the `Event.author` field follows special semantics to maintain conversation clarity:

**Model responses**: Authored by the **agent name** (e.g., `"my_agent"`), not the literal string `"model"`

- This enables multi-agent scenarios where you need to track which agent generated the response
- Example: `Event(author="customer_service_agent", content=...)`

**User transcriptions**: Authored as `"user"` when the event contains transcribed user audio

**How it works**:

1. Gemini Live API returns user audio transcriptions with `content.role == 'user'`
2. ADK's `get_author_for_event()` function checks for this role marker
3. If `content.role == 'user'`, ADK sets `Event.author` to `"user"`
4. Otherwise, ADK sets `Event.author` to the agent name (e.g., `"my_agent"`)

This transformation ensures that transcribed user input is correctly attributed to the user in your application's conversation history, even though it flows through the model's response stream.

- Example: Input audio transcription → `Event(author="user", input_transcription=..., content.role="user")`

**Why this matters**:

- In multi-agent applications, you can filter events by agent: `events = [e for e in stream if e.author == "my_agent"]`
- When displaying conversation history, use `event.author` to show who said what
- Transcription events are correctly attributed to the user even though they flow through the model

!!! note "Source Reference"

    See author attribution logic in [`base_llm_flow.py:674-708`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/flows/llm_flows/base_llm_flow.py#L674-L708)

### Event Types and Handling

ADK streams distinct event types through `runner.run_live()` to support different interaction modalities: text responses for traditional chat, audio chunks for voice output, transcriptions for accessibility and logging, and tool call notifications for function execution. Each event includes metadata flags (`partial`, `turn_complete`, `interrupted`) that control UI state transitions and enable natural, human-like conversation flows. Understanding how to recognize and handle these event types is essential for building responsive streaming applications.

### Text Events

The most common event type, containing the model's text responses when you specifying `response_modalities` in `RunConfig` to `["TEXT"]` mode:

**Usage:**

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        if event.content.parts[0].text:
            text = event.content.parts[0].text

            if not event.partial:
                # Your logic to update streaming display
                update_streaming_display(text)
```

#### Default Response Modality Behavior

When `response_modalities` is not explicitly set (i.e., `None`), ADK automatically defaults to `["AUDIO"]` mode at the start of `run_live()`. This means:

- **If you provide no RunConfig**: Defaults to `["AUDIO"]`
- **If you provide RunConfig without response_modalities**: Defaults to `["AUDIO"]`
- **If you explicitly set response_modalities**: Uses your setting (no default applied)

**Why this default exists**: Some native audio models require the response modality to be explicitly set. To ensure compatibility with all models, ADK defaults to `["AUDIO"]`.

**For text-only applications**: Always explicitly set `response_modalities=["TEXT"]` in your RunConfig to avoid receiving unexpected audio events.

**Example:**

```python
# Explicit text mode
run_config = RunConfig(
    response_modalities=["TEXT"],
    streaming_mode=StreamingMode.BIDI
)
```

**Key Event Flags:**

These flags help you manage streaming text display and conversation flow in your UI:

- `event.partial`: `True` for incremental text chunks during streaming; `False` for complete merged text
- `event.turn_complete`: `True` when the model has finished its complete response
- `event.interrupted`: `True` when user interrupted the model's response

!!! note "Learn More"

    For detailed guidance on using `partial` `turn_complete` and `interrupted` flags to manage conversation flow and UI state, see [Handling Text Events](#handling-text-events).

### Audio Events

When `response_modalities` is configured to `["AUDIO"]` in your `RunConfig`, the model generates audio output instead of text, and you'll receive audio data in the event stream:

**Configuration:**

```python
# Configure RunConfig for audio responses
run_config = RunConfig(
    response_modalities=["AUDIO"],
    streaming_mode=StreamingMode.BIDI
)

# Audio arrives as inline_data in event.content.parts
async for event in runner.run_live(..., run_config=run_config):
    if event.content and event.content.parts:
        part = event.content.parts[0]
        if part.inline_data:
            # Audio event structure:
            # part.inline_data.data: bytes (raw PCM audio)
            # part.inline_data.mime_type: str (e.g., "audio/pcm")
            audio_data = part.inline_data.data
            mime_type = part.inline_data.mime_type

            print(f"Received {len(audio_data)} bytes of {mime_type}")
            # Your logic to play audio
            await play_audio(audio_data)
```

!!! note "Learn More"

    - **`response_modalities` controls how the model generates output**—you must choose either `["TEXT"]` for text responses or `["AUDIO"]` for audio responses per session. You cannot use both modalities simultaneously. See [Part 4: Response Modalities](part4.md#response-modalities) for configuration details.
    - For comprehensive coverage of audio formats, sending/receiving audio, and audio processing flow, see [Part 5: How to Use Audio, Image and Video](part5.md).

### Audio Events with File Data

When audio data is aggregated and saved as files in artifacts, ADK yields events containing `file_data` references instead of raw `inline_data`. This is useful for persisting audio to session history.

!!! note "Source Reference"

    See audio file aggregation logic in [`audio_cache_manager.py:156-178`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/flows/llm_flows/audio_cache_manager.py#L156-L178)

**Receiving Audio File References:**

```python
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=queue,
    run_config=run_config
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.file_data:
                # Audio aggregated into a file saved in artifacts
                file_uri = part.file_data.file_uri
                mime_type = part.file_data.mime_type

                print(f"Audio file saved: {file_uri} ({mime_type})")
                # Retrieve audio file from artifact service for playback
```

**File Data vs Inline Data:**

- **Inline Data** (`part.inline_data`): Raw audio bytes streamed in real-time; ephemeral and not saved to session
- **File Data** (`part.file_data`): Reference to audio file stored in artifacts; can be persisted to session history

Both input and output audio data are aggregated into audio files and saved in the artifact service. The file reference is included in the event as `file_data`, allowing you to retrieve the audio later.

!!! note "Session Persistence"

    To save audio events with file data to session history, enable `RunConfig.save_live_blob = True`. This allows audio conversations to be reviewed or replayed from persisted sessions.

### Metadata Events

Usage metadata events contain token usage information for monitoring costs and quota consumption. The `run_live()` method yields these events separately from content events.

!!! note "Source Reference"

    See usage metadata structure in [`llm_response.py:105`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/models/llm_response.py#L105)

**Accessing Token Usage:**

```python
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=queue,
    run_config=run_config
):
    if event.usage_metadata:
        print(f"Prompt tokens: {event.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {event.usage_metadata.candidates_token_count}")
        print(f"Total tokens: {event.usage_metadata.total_token_count}")

        # Track cumulative usage across the session
        total_tokens += event.usage_metadata.total_token_count or 0
```

**Available Metadata Fields:**

- `prompt_token_count`: Number of tokens in the input (prompt and context)
- `candidates_token_count`: Number of tokens in the model's response
- `total_token_count`: Sum of prompt and response tokens
- `cached_content_token_count`: Number of tokens served from cache (when using context caching)

!!! note "Cost Monitoring"

    Usage metadata events allow real-time cost tracking during streaming sessions. You can implement quota limits, display usage to users, or log metrics for billing and analytics.

### Transcription Events

When transcription is enabled in `RunConfig`, you receive transcriptions as separate events:

**Configuration:**

```python
async for event in runner.run_live(...):
    # User's spoken words (when input_audio_transcription enabled)
    if event.input_transcription:
        # Your logic to display user transcription
        display_user_transcription(event.input_transcription)

    # Model's spoken words (when output_audio_transcription enabled)
    if event.output_transcription:
        # Your logic to display model transcription
        display_model_transcription(event.output_transcription)
```

These enable accessibility features and conversation logging without separate transcription services.

!!! note "Learn More"

    For details on enabling transcription in `RunConfig` and understanding transcription delivery, see [Part 5: Audio Transcription](part5.md#audio-transcription).

### Tool Call Events

When the model requests tool execution:

**Usage:**

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.function_call:
                # Model is requesting a tool execution
                tool_name = part.function_call.name
                tool_args = part.function_call.args
                # ADK handles execution automatically
```

ADK processes tool calls automatically—you typically don't need to handle these directly unless implementing custom tool execution logic.

!!! note "Learn More"

    For details on how ADK automatically executes tools, handles function responses, and supports long-running and streaming tools, see [Automatic Tool Execution in run_live()](#automatic-tool-execution-in-run_live).

### Error Events

Production applications need robust error handling to gracefully handle model errors and connection issues. ADK surfaces errors through the `error_code` and `error_message` fields:

**Usage:**

```python
import logging

logger = logging.getLogger(__name__)

try:
    async for event in runner.run_live(...):
        # Handle errors from the model or connection
        if event.error_code:
            logger.error(f"Model error: {event.error_code} - {event.error_message}")

            # Send error notification to client
            await websocket.send_json({
                "type": "error",
                "code": event.error_code,
                "message": event.error_message
            })

            # Decide whether to continue or break based on error severity
            if event.error_code in ["SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST"]:
                # Content policy violations - usually cannot retry
                break  # Terminal error - exit loop
            elif event.error_code == "MAX_TOKENS":
                # Token limit reached - may need to adjust configuration
                break
            # For other errors, you might continue or implement retry logic
            continue  # Transient error - keep processing

        # Normal event processing only if no error
        if event.content and event.content.parts:
            # ... handle content
            pass
finally:
    queue.close()  # Always cleanup connection
```

!!! note

    The above example shows the basic structure for checking `error_code` and `error_message`. For production-ready error handling with user notifications, retry logic, and context logging, see the real-world scenarios below.

**When to use `break` vs `continue`:**

The key decision is: *Can the model's response continue meaningfully?*

**Scenario 1: Content Policy Violation (Use `break`)**

You're building a customer support chatbot. A user asks an inappropriate question that triggers a SAFETY filter:

**Example:**

```python
if event.error_code in ["SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST"]:
    # Model has stopped generating - continuation is impossible
    await websocket.send_json({
        "type": "error",
        "message": "I can't help with that request. Please ask something else."
    })
    break  # Exit loop - model won't send more events for this turn
```

**Why `break`?** The model has terminated its response. No more events will come for this turn. Continuing would just waste resources waiting for events that won't arrive.

---

**Scenario 2: Network Hiccup During Streaming (Use `continue`)**

You're building a voice transcription service. Midway through transcribing, there's a brief network glitch:

**Example:**

```python
if event.error_code == "UNAVAILABLE":
    # Temporary network issue
    logger.warning(f"Network hiccup: {event.error_message}")
    # Don't notify user for brief transient issues that may self-resolve
    continue  # Keep listening - model may recover and continue
```

**Why `continue`?** This is a transient error. The connection might recover, and the model may continue streaming the transcription. Breaking would prematurely end a potentially recoverable stream.

!!! note "User Notifications"

    For brief transient errors (lasting <1 second), don't notify the user—they won't notice the hiccup. But if the error persists or impacts the user experience (e.g., streaming pauses for >3 seconds), notify them gracefully: "Experiencing connection issues, retrying..."

---

**Scenario 3: Token Limit Reached (Use `break`)**

You're generating a long-form article and hit the maximum token limit:

**Example:**

```python
if event.error_code == "MAX_TOKENS":
    # Model has reached output limit
    await websocket.send_json({
        "type": "complete",
        "message": "Response reached maximum length",
        "truncated": True
    })
    break  # Model has finished - no more tokens will be generated
```

**Why `break`?** The model has reached its output limit and stopped. Continuing won't yield more tokens.

---

**Scenario 4: Rate Limit with Retry Logic (Use `continue` with backoff)**

You're running a high-traffic application that occasionally hits rate limits:

**Example:**

```python
retry_count = 0
max_retries = 3

async for event in runner.run_live(...):
    if event.error_code == "RESOURCE_EXHAUSTED":
        retry_count += 1
        if retry_count > max_retries:
            logger.error("Max retries exceeded")
            break  # Give up after multiple failures

        # Wait and retry
        await asyncio.sleep(2 ** retry_count)  # Exponential backoff
        continue  # Keep listening - rate limit may clear

    # Reset counter on successful event
    retry_count = 0
```

**Why `continue` (initially)?** Rate limits are often temporary. With exponential backoff, the stream may recover. But after multiple failures, `break` to avoid infinite waiting.

---

**Decision Framework:**

| Error Type | Action | Reason |
|------------|--------|--------|
| `SAFETY`, `PROHIBITED_CONTENT` | `break` | Model terminated response |
| `MAX_TOKENS` | `break` | Model finished generating |
| `UNAVAILABLE`, `DEADLINE_EXCEEDED` | `continue` | Transient network/timeout issue |
| `RESOURCE_EXHAUSTED` (rate limit) | `continue` with retry logic | May recover after brief wait |
| Unknown errors | `continue` (with logging) | Err on side of caution |

**Critical: Always use `finally` for cleanup**

**Usage:**

```python
try:
    async for event in runner.run_live(...):
        # ... error handling ...
finally:
    queue.close()  # Cleanup runs whether you break or finish normally
```

Whether you `break` or the loop finishes naturally, `finally` ensures the connection closes properly.

**Error Code Reference:**

ADK error codes come from the underlying Gemini API. Here are the most common error codes you'll encounter:

| Error Code | Category | Description | Recommended Action |
|------------|----------|-------------|-------------------|
| `SAFETY` | Content Policy | Content violates safety policies | `break` - Inform user, log incident |
| `PROHIBITED_CONTENT` | Content Policy | Content contains prohibited material | `break` - Show policy violation message |
| `BLOCKLIST` | Content Policy | Content matches blocklist | `break` - Alert user, don't retry |
| `MAX_TOKENS` | Limits | Output reached maximum token limit | `break` - Truncate gracefully, summarize |
| `RESOURCE_EXHAUSTED` | Rate Limiting | Quota or rate limit exceeded | `continue` with backoff - Retry after delay |
| `UNAVAILABLE` | Transient | Service temporarily unavailable | `continue` - Retry, may self-resolve |
| `DEADLINE_EXCEEDED` | Transient | Request timeout exceeded | `continue` - Consider retry with backoff |
| `CANCELLED` | Client | Client cancelled the request | `break` - Clean up resources |
| `UNKNOWN` | System | Unspecified error occurred | `continue` with logging - Log for analysis |

For complete error code listings and descriptions, refer to the official documentation:

!!! note "Official Documentation"

    - **FinishReason** (when model stops generating tokens): [Google AI for Developers](https://ai.google.dev/api/python/google/ai/generativelanguage/Candidate/FinishReason) | [Agent Platform](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini)
    - **BlockedReason** (when prompts are blocked by content filters): [Google AI for Developers](https://ai.google.dev/api/python/google/ai/generativelanguage/GenerateContentResponse/PromptFeedback/BlockReason) | [Agent Platform](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/configure-safety-attributes)
    - **ADK Implementation**: [`llm_response.py:145-200`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/models/llm_response.py#L145-L200)

**Best practices for error handling:**

- **Always check for errors first**: Process `error_code` before handling content to avoid processing invalid events
- **Log errors with context**: Include session_id and user_id in error logs for debugging
- **Categorize errors**: Distinguish between retryable errors (transient failures) and terminal errors (content policy violations)
- **Notify users gracefully**: Show user-friendly error messages instead of raw error codes
- **Implement retry logic**: For transient errors, consider automatic retry with exponential backoff
- **Monitor error rates**: Track error types and frequencies to identify systemic issues
- **Handle content policy errors**: For `SAFETY`, `PROHIBITED_CONTENT`, and `BLOCKLIST` errors, inform users that their content violates policies

## Handling Text Events

Understanding the `partial`, `interrupted`, and `turn_complete` flags is essential for building responsive streaming UIs. These flags enable you to provide real-time feedback during streaming, handle user interruptions gracefully, and detect conversation boundaries for proper state management.

### Handling `partial`

This flag helps you distinguish between incremental text chunks and complete merged text, enabling smooth streaming displays with proper final confirmation.

**Usage:**

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        if event.content.parts[0].text:
            text = event.content.parts[0].text

            if event.partial:
                # Your streaming UI update logic here
                update_streaming_display(text)
            else:
                # Your complete message display logic here
                display_complete_message(text)
```

**`partial` Flag Semantics:**

- `partial=True`: The text in this event is **incremental**—it contains ONLY the new text since the last event
- `partial=False`: The text in this event is **complete**—it contains the full merged text for this response segment

!!! note

    The `partial` flag is only meaningful for text content (`event.content.parts[].text`). For other content types:

    - **Audio events**: Each audio chunk in `inline_data` is independent (no merging occurs)
    - **Tool calls**: Function calls and responses are always complete (partial doesn't apply)
    - **Transcriptions**: Transcription events are always complete when yielded

**Example Stream:**

```text
Event 1: partial=True,  text="Hello",        turn_complete=False
Event 2: partial=True,  text=" world",       turn_complete=False
Event 3: partial=False, text="Hello world",  turn_complete=False
Event 4: partial=False, text="",             turn_complete=True  # Turn done
```

**Important timing relationships**:
- `partial=False` can occur **multiple times** in a turn (e.g., after each sentence)
- `turn_complete=True` occurs **once** at the very end of the model's complete response, in a **separate event**
- You may receive: `partial=False` (sentence 1) → `partial=False` (sentence 2) → `turn_complete=True`
- The merged text event (`partial=False` with content) is always yielded **before** the `turn_complete=True` event

!!! note

    ADK internally accumulates all text from `partial=True` events. When you receive an event with `partial=False`, the text content equals the sum of all preceding `partial=True` chunks. This means:

    - You can safely ignore all `partial=True` events and only process `partial=False` events if you don't need streaming display
    - If you do display `partial=True` events, the `partial=False` event provides the complete merged text for validation or storage
    - This accumulation is handled automatically by ADK's `StreamingResponseAggregator`—you don't need to manually concatenate partial text chunks

#### Handling `interrupted` Flag

This enables natural conversation flow by detecting when users interrupt the model mid-response, allowing you to stop rendering outdated content immediately.

When users send new input while the model is still generating a response (common in voice conversations), you'll receive an event with `interrupted=True`:

**Usage:**

```python
async for event in runner.run_live(...):
    if event.interrupted:
        # Your logic to stop displaying partial text and clear typing indicators
        stop_streaming_display()

        # Your logic to show interruption in UI (optional)
        show_user_interruption_indicator()
```

**Example - Interruption Scenario:**

```text
Model: "The weather in San Francisco is currently..."
User: [interrupts] "Actually, I meant San Diego"
→ event.interrupted=True received
→ Your app: stop rendering model response, clear UI
→ Model processes new input
Model: "The weather in San Diego is..."
```

**When to use interruption handling:**

- **Voice conversations**: Stop audio playback immediately when user starts speaking
- **Clear UI state**: Remove typing indicators and partial text displays
- **Conversation logging**: Mark which responses were interrupted (incomplete)
- **User feedback**: Show visual indication that interruption was recognized

#### Handling `turn_complete` Flag

This signals conversation boundaries, allowing you to update UI state (enable input controls, hide indicators) and mark proper turn boundaries in logs and analytics.

When the model finishes its complete response, you'll receive an event with `turn_complete=True`:

**Usage:**

```python
async for event in runner.run_live(...):
    if event.turn_complete:
        # Your logic to update UI to show "ready for input" state
        enable_user_input()
        # Your logic to hide typing indicator
        hide_typing_indicator()

        # Your logic to mark conversation boundary in logs
        log_turn_boundary()
```

**Event Flag Combinations:**

Understanding how `turn_complete` and `interrupted` combine helps you handle all conversation states:

| Scenario | turn_complete | interrupted | Your App Should |
|----------|---------------|-------------|-----------------|
| Normal completion | True | False | Enable input, show "ready" state |
| User interrupted mid-response | False | True | Stop display, clear partial content |
| Interrupted at end | True | True | Same as normal completion (turn is done) |
| Mid-response (partial text) | False | False | Continue displaying streaming text |

**Implementation:**

```python
async for event in runner.run_live(...):
    # Handle streaming text
    if event.content and event.content.parts and event.content.parts[0].text:
        if event.partial:
            # Your logic to show typing indicator and update partial text
            update_streaming_text(event.content.parts[0].text)
        else:
            # Your logic to display complete text chunk
            display_text(event.content.parts[0].text)

    # Handle interruption
    if event.interrupted:
        # Your logic to stop audio playback and clear indicators
        stop_audio_playback()
        clear_streaming_indicators()

    # Handle turn completion
    if event.turn_complete:
        # Your logic to enable user input
        show_input_ready_state()
        enable_microphone()
```

**Common Use Cases:**

- **UI state management**: Show/hide "ready for input" indicators, typing animations, microphone states
- **Audio playback control**: Know when to stop rendering audio chunks from the model
- **Conversation logging**: Mark clear boundaries between turns for history/analytics
- **Streaming optimization**: Stop buffering when turn is complete

**Turn completion and caching:** Audio/transcript caches are flushed automatically at specific points during streaming:
- **On turn completion** (`turn_complete=True`): Both user and model audio caches are flushed
- **On interruption** (`interrupted=True`): Model audio cache is flushed
- **On generation completion**: Model audio cache is flushed

## Serializing Events to JSON

ADK `Event` objects are Pydantic models, which means they come with powerful serialization capabilities. The `model_dump_json()` method is particularly useful for streaming events over network protocols like WebSockets or Server-Sent Events (SSE).

### Using event.model_dump_json()

This provides a simple one-liner to convert ADK events into JSON format that can be sent over network protocols like WebSockets or SSE.

The `model_dump_json()` method serializes an `Event` object to a JSON string:

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L219-L234" target="_blank">main.py:219-234</a>'
async def downstream_task() -> None:
    """Receives Events from run_live() and sends to WebSocket."""
    async for event in runner.run_live(
        user_id=user_id,
        session_id=session_id,
        live_request_queue=live_request_queue,
        run_config=run_config
    ):
        event_json = event.model_dump_json(exclude_none=True, by_alias=True)
        await websocket.send_text(event_json)
```

**What gets serialized:**

- Event metadata (author, server_content fields)
- Content (text, audio data, function calls)
- Event flags (partial, turn_complete, interrupted)
- Transcription data (input_transcription, output_transcription)
- Tool execution information

**When to use `model_dump_json()`:**

- ✅ Streaming events over network (WebSocket, SSE)
- ✅ Logging/persistence to JSON files
- ✅ Debugging and inspection
- ✅ Integration with JSON-based APIs

**When NOT to use it:**

- ❌ In-memory processing (use event objects directly)
- ❌ High-frequency events where serialization overhead matters
- ❌ When you only need a few fields (extract them directly instead)

!!! warning "Performance Warning"

    Binary audio data in `event.content.parts[].inline_data` will be base64-encoded when serialized to JSON, significantly increasing payload size (~133% overhead). For production applications with audio, send binary data separately using WebSocket binary frames or multipart HTTP. See [Optimization for Audio Transmission](#optimization-for-audio-transmission) for details.

### Serialization options

This allows you to reduce payload sizes by excluding unnecessary fields, improving network performance and client processing speed.

Pydantic's `model_dump_json()` supports several useful parameters:

**Usage:**

```python
# Exclude None values for smaller payloads (with camelCase field names)
event_json = event.model_dump_json(exclude_none=True, by_alias=True)

# Custom exclusions (e.g., skip large binary audio)
event_json = event.model_dump_json(
    exclude={'content': {'parts': {'__all__': {'inline_data'}}}},
    by_alias=True
)

# Include only specific fields
event_json = event.model_dump_json(
    include={'content', 'author', 'turn_complete', 'interrupted'},
    by_alias=True
)

# Pretty-printed JSON (for debugging)
event_json = event.model_dump_json(indent=2, by_alias=True)
```

The bidi-demo uses `exclude_none=True` to minimize payload size by omitting fields with None values.

### Deserializing on the Client

This shows how to parse and handle serialized events on the client side, enabling responsive UI updates based on event properties like turn completion and interruptions.

On the client side (JavaScript/TypeScript), parse the JSON back to objects:

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L341-L690" target="_blank">app.js:339-688</a>'
// Handle incoming messages
websocket.onmessage = function (event) {
    // Parse the incoming ADK Event
    const adkEvent = JSON.parse(event.data);

    // Handle turn complete event
    if (adkEvent.turnComplete === true) {
        // Remove typing indicator from current message
        if (currentBubbleElement) {
            const textElement = currentBubbleElement.querySelector(".bubble-text");
            const typingIndicator = textElement.querySelector(".typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }
        currentMessageId = null;
        currentBubbleElement = null;
        return;
    }

    // Handle interrupted event
    if (adkEvent.interrupted === true) {
        // Stop audio playback if it's playing
        if (audioPlayerNode) {
            audioPlayerNode.port.postMessage({ command: "endOfAudio" });
        }

        // Keep the partial message but mark it as interrupted
        if (currentBubbleElement) {
            const textElement = currentBubbleElement.querySelector(".bubble-text");

            // Remove typing indicator
            const typingIndicator = textElement.querySelector(".typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }

            // Add interrupted marker
            currentBubbleElement.classList.add("interrupted");
        }

        currentMessageId = null;
        currentBubbleElement = null;
        return;
    }

    // Handle content events (text or audio)
    if (adkEvent.content && adkEvent.content.parts) {
        const parts = adkEvent.content.parts;

        for (const part of parts) {
            // Handle text
            if (part.text) {
                // Add a new message bubble for a new turn
                if (currentMessageId == null) {
                    currentMessageId = Math.random().toString(36).substring(7);
                    currentBubbleElement = createMessageBubble(part.text, false, true);
                    currentBubbleElement.id = currentMessageId;
                    messagesDiv.appendChild(currentBubbleElement);
                } else {
                    // Update the existing message bubble with accumulated text
                    const existingText = currentBubbleElement.querySelector(".bubble-text").textContent;
                    const cleanText = existingText.replace(/\.\.\.$/, '');
                    updateMessageBubble(currentBubbleElement, cleanText + part.text, true);
                }

                scrollToBottom();
            }
        }
    }
};
```

!!! note "Demo Implementation"

    See the complete WebSocket message handler in [`app.js:339-688`](https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L341-L690)

### Optimization for Audio Transmission

Base64-encoded binary audio in JSON significantly increases payload size. For production applications, use a single WebSocket connection with both binary frames (for audio) and text frames (for metadata):

**Usage:**

```python
async for event in runner.run_live(...):
    # Check for binary audio
    has_audio = (
        event.content and
        event.content.parts and
        any(p.inline_data for p in event.content.parts)
    )

    if has_audio:
        # Send audio via binary WebSocket frame
        for part in event.content.parts:
            if part.inline_data:
                await websocket.send_bytes(part.inline_data.data)

        # Send metadata only (much smaller)
        metadata_json = event.model_dump_json(
            exclude={'content': {'parts': {'__all__': {'inline_data'}}}},
            by_alias=True
        )
        await websocket.send_text(metadata_json)
    else:
        # Text-only events can be sent as JSON
        await websocket.send_text(event.model_dump_json(exclude_none=True, by_alias=True))
```

This approach reduces bandwidth by ~75% for audio-heavy streams while maintaining full event metadata.

