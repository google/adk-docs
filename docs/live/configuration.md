# Configuration

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-preview">Experimental</span>
</div>

`RunConfig` is where you shape a live session: how the agent sounds, how much history it
keeps, and what limits it runs under. You pass it to
[`Runner.run_live()`](https://google.github.io/adk-docs/api-reference/python/), and it
applies to that session only — two users of the same agent can run with completely
different configurations.

This page is the `RunConfig` reference for live agents. Voice, transcription, and turn
detection have their own page: see [Voice](voice.md).

## RunConfig Parameter Quick Reference

This table provides a quick reference for the `RunConfig` parameters that matter most to live agents:

| Parameter | Type | Purpose | Platform Support | Reference |
|-----------|------|---------|------------------|-----------|
| **response_modalities** | list[str] | Output format. Live agents must use `AUDIO` — the native audio models do not accept `TEXT` | Both | [Details](#response-modalities) |
| **streaming_mode** | StreamingMode | Chunked or single-shot delivery on the `run_async()` path; not read by `run_live()` | Both | [Details](#streamingmode-bidi-or-sse) |
| **session_resumption** | SessionResumptionConfig | Enable automatic reconnection | Both | [Details](sessions.md#live-api-session-resumption) |
| **context_window_compression** | ContextWindowCompressionConfig | Unlimited session duration | Both | [Details](sessions.md#live-api-context-window-compression) |
| **history_config** | HistoryConfig | Control how prior conversation history is replayed to the Live server | Both | [Details](#history_config) |
| **max_llm_calls** | int | Limit total LLM calls per session | Both | [Details](#max_llm_calls) |
| **save_live_blob** | bool | Persist audio/video streams | Both | [Details](#save_live_blob) |
| **custom_metadata** | dict[str, Any] | Attach metadata to invocation events | Both | [Details](#custom_metadata) |
| **support_cfc** | bool | Enable compositional function calling | Gemini (2.x models only) | [Details](#support_cfc-experimental) |
| **speech_config** | SpeechConfig | Voice and language configuration | Both | [Voice configuration](voice.md#voice-configuration-speech-config) |
| **input_audio_transcription** | AudioTranscriptionConfig | Transcribe user speech | Both | [Audio transcription](voice.md#audio-transcription) |
| **output_audio_transcription** | AudioTranscriptionConfig | Transcribe model speech | Both | [Audio transcription](voice.md#audio-transcription) |
| **realtime_input_config** | RealtimeInputConfig | VAD configuration | Both | [Voice activity detection](voice.md#voice-activity-detection-vad) |
| **explicit_vad_signal** | bool | Emit voice activity events from the model | Both | [Details](#other-live-related-fields) |
| **proactivity** | ProactivityConfig | Enable proactive audio | Gemini (2.5 native audio only) | [Proactivity and affective dialog](voice.md#proactivity-and-affective-dialog) |
| **enable_affective_dialog** | bool | Emotional adaptation | Gemini (2.5 native audio only) | [Proactivity and affective dialog](voice.md#proactivity-and-affective-dialog) |
| **translation_config** | TranslationConfig | Real-time speech-to-speech translation | Gemini (translation models only) | [Details](#other-live-related-fields) |
| **avatar_config** | AvatarConfig | Render the agent as an animated avatar | Both | [Details](#other-live-related-fields) |

!!! note "Reference"

    [`RunConfig`](../api-reference/python/google-adk.html#google.adk.agents.RunConfig) in the Python API reference

**Platform Support Legend:**

- **Both**: Supported on both Gemini Live API and Gemini Live API (Agent Platform)
- **Gemini**: Only supported on Gemini Live API
- **Model-specific**: Requires specific model architecture (e.g., native audio)

**Import Paths:**

All configuration type classes referenced in the table above are imported from `google.genai.types`:

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode

# Configuration types are accessed via types module
run_config = RunConfig(
    session_resumption=types.SessionResumptionConfig(),
    context_window_compression=types.ContextWindowCompressionConfig(...),
    speech_config=types.SpeechConfig(...),
    # etc.
)
```

The `RunConfig` class itself and `StreamingMode` enum are imported from `google.adk.agents.run_config`.

## Response Modalities

`response_modalities` controls the output format, and a session gets exactly one. **For live
agents the value is always `["AUDIO"]`**: every Live API model ADK supports is a
[native audio model](models.md#native-audio-models), and those accept no other modality.

ADK fills this in for you when you leave it unset
([`runners.py:1672-1673`](https://github.com/google/adk-python/blob/096ecfcf56ad47a9a63da1d76a062f56d7586692/src/google/adk/runners.py#L1672-L1673)),
so most live applications never touch the field.

!!! warning "Migrating from `response_modalities=["TEXT"]`"

    Older ADK samples and half-cascade models allowed a text-only live session. That no
    longer works — `run_live()` with `["TEXT"]` fails against
    `gemini-3.1-flash-live-preview`, `gemini-2.5-flash-native-audio-preview-12-2025`, and
    `gemini-live-2.5-flash-native-audio` alike.

    **To get text out of a live agent, read
    [`event.output_transcription`](voice.md#audio-transcription)** — transcription is enabled
    by default in ADK, so deleting the `response_modalities` line is usually the whole fix.

    `["TEXT"]` is still correct on the `run_async()` path, which runs on standard Gemini
    models. See [Bidi-streaming or SSE](#streamingmode-bidi-or-sse).

Response modality only affects model output — **you can always send text, voice, or video
input** (if the model supports that input modality) regardless of it.

## Bidi-streaming or SSE { #streamingmode-bidi-or-sse }

ADK can reach Gemini over two different endpoints, and **the `Runner` method you call is
what picks one**:

- **`runner.run_live()`**: ADK opens a WebSocket to the **Live API** (the bidirectional
  streaming endpoint via `live.connect()`). This is what the rest of this guide covers, and
  it is required for real-time audio and video
- **`runner.run_async()`**: ADK uses HTTP to the **standard Gemini API** (the
  unary/streaming endpoint via `generate_content_async()`). Set
  `RunConfig.streaming_mode = StreamingMode.SSE` to stream that response back chunk by chunk

The two model sets barely overlap. Standard Gemini models such as `gemini-flash-latest` do
not speak the Live API protocol, and the Live API models in
[Supported models](models.md#native-audio-models) are meant to be driven with `run_live()`,
so choosing a model is part of choosing a `Runner` method.

!!! warning "`StreamingMode.BIDI` does not switch ADK to the Live API"

    `RunConfig.streaming_mode` is read only on the `run_async()` code path, where it
    chooses between a single complete response (`StreamingMode.NONE`, the default) and
    chunked delivery (`StreamingMode.SSE`). The `run_live()` path never reads it, so
    setting `streaming_mode=StreamingMode.BIDI` has no effect — and it fails silently, with
    no error or warning. **Calling `run_live()` is what gets you bidirectional streaming.**
    ADK's own `StreamingMode` docstring says as much: BIDI "is not used in the standard
    execution path", and the real bidirectional behavior "uses a completely different code
    path that doesn't rely on `streaming_mode`".

```python
# Live API: no streaming_mode needed, calling run_live() is what selects it
run_config = RunConfig(response_modalities=["AUDIO"])
async for event in runner.run_live(..., run_config=run_config):
    ...
```

**Note:** This distinction is about the **ADK-to-Gemini API communication protocol**, not your application's client-facing architecture. You can build WebSocket servers, REST APIs, SSE endpoints, or any other architecture for your clients with either one.

For the `run_async()` / SSE path — `streaming_mode` values, progressive SSE streaming, and
the language-specific configuration — see
[Runtime configuration](../runtime/runconfig.md#enable-streaming).

## Miscellaneous Controls

ADK provides additional RunConfig options to control session behavior, manage costs, and persist audio data for debugging and compliance purposes.

```python
run_config = RunConfig(
    # Limit total LLM calls per invocation
    max_llm_calls=500,  # Default: 500 (prevents runaway loops)
                        # 0 or negative = unlimited (use with caution)

    # Save audio/video artifacts for debugging/compliance
    save_live_blob=True,  # Default: False

    # Attach custom metadata to events
    custom_metadata={"user_tier": "premium", "session_type": "support"},  # Default: None

    # Enable compositional function calling (experimental)
    support_cfc=True  # Default: False (Gemini 2.x models only)
)
```

### max_llm_calls

This parameter caps the total number of LLM invocations allowed per invocation context, providing protection against runaway costs and infinite agent loops.

**Limitation for Bidi-streaming:**

**The `max_llm_calls` limit does NOT apply to `run_live()`.** This parameter only protects `run_async()` flows. If you're building bidirectional streaming applications (the focus of this guide), you will NOT get automatic cost protection from this parameter.

**For Live streaming sessions**, implement your own safeguards:

- Session duration limits
- Turn count tracking
- Custom cost monitoring by tracking token usage in model turn events (see [Event types and handling](events.md#event-types-and-handling))
- Application-level circuit breakers

### save_live_blob

This parameter controls whether audio and video streams are persisted to ADK's session and artifact services for debugging, compliance, and quality assurance purposes.

!!! warning "Migration Note: save_live_audio Deprecated"

    **If you're using `save_live_audio`:** This parameter has been deprecated in favor of `save_live_blob`. ADK will automatically migrate `save_live_audio=True` to `save_live_blob=True` with a deprecation warning, but this compatibility layer will be removed in a future release. Update your code to use `save_live_blob` instead.

Currently, **only audio is persisted** by ADK's implementation. When enabled, ADK persists audio streams to:

- **[Session service](/sessions/)**: Conversation history includes audio references
- **[Artifact service](/artifacts/)**: Audio files stored with unique IDs

**Use cases:**

- **Debugging**: Voice interaction issues, assistant behavior analysis
- **Compliance**: Audit trails for regulated industries (healthcare, financial services)
- **Quality Assurance**: Monitoring conversation quality, identifying issues
- **Training Data**: Collecting data for model improvement
- **Development/Testing**: Testing environments and cost-sensitive deployments

**Storage considerations:**

Enabling `save_live_blob=True` has significant storage implications:

- **Audio file sizes**: At 16kHz PCM, audio input generates ~1.92 MB per minute
- **Session storage**: Audio is stored in both session service and artifact service
- **Retention policy**: Check your artifact service configuration for retention periods
- **Cost impact**: Storage costs can accumulate quickly for high-volume voice applications

**Best practices:**

- Enable only when needed (debugging, compliance, training)
- Implement retention policies to auto-delete old audio artifacts
- Consider sampling (e.g., save 10% of sessions for quality monitoring)
- Use compression if supported by your artifact service

### history_config

When ADK opens a **new** Live API connection for a session that already has conversation
history, it replays that history to the server. Because the history includes the model's own
past turns, the server needs to be told not to answer them again. ADK handles this for you:
before connecting, it sets
`live_connect_config.history_config.initial_history_in_client_content = True` whenever there
is history to send and no session resumption handle is in play.

```python
from google.genai import types

# ADK sets this automatically; override only if you need the opposite behavior.
run_config = RunConfig(
    history_config=types.HistoryConfig(
        initial_history_in_client_content=True,
    ),
)
```

**What this means in practice:**

- **You normally do nothing.** ADK only fills in the value when you have not set one, so an
  explicit `history_config` on `RunConfig` always wins.
- **Reconnections skip history entirely.** When ADK reconnects with a session resumption
  handle, the server already holds the state for that session, so ADK sends no history and
  does not touch `history_config`.
- **Symptom if it goes wrong**: setting `initial_history_in_client_content=False` while
  seeding history makes the model respond to the *replayed* turns, producing a burst of
  duplicate answers at the start of the connection.

### custom_metadata

This parameter allows you to attach arbitrary key-value metadata to events generated during the current invocation. The metadata is stored in the `Event.custom_metadata` field and persisted to session storage, enabling you to tag events with application-specific context for analytics, debugging, routing, or compliance tracking.

**Configuration:**

```python
from google.adk.agents.run_config import RunConfig

# Attach metadata to all events in this invocation
run_config = RunConfig(
    custom_metadata={
        "user_tier": "premium",
        "session_type": "customer_support",
        "campaign_id": "promo_2025",
        "ab_test_variant": "variant_b"
    }
)
```

**How it works:**

When you provide `custom_metadata` in RunConfig:

1. **Metadata attachment**: The dictionary is attached to every `Event` generated during the invocation
2. **Session persistence**: Events with metadata are stored in the session service (database, Agent Platform, or in-memory)
3. **Event access**: Retrieve metadata from any event via `event.custom_metadata`
4. **A2A integration**: For Agent-to-Agent (A2A) communication, ADK automatically propagates A2A request metadata to this field

**Type specification:**

```python
custom_metadata: Optional[dict[str, Any]] = None
```

The metadata is a flexible dictionary accepting any JSON-serializable values (strings, numbers, booleans, nested objects, arrays).

**Use cases:**

- **User segmentation**: Tag events with user tier, subscription level, or cohort information
- **Session classification**: Label sessions by type (support, sales, onboarding) for analytics
- **Campaign tracking**: Associate events with marketing campaigns or experiments
- **A/B testing**: Track which variant of your application generated the event
- **Compliance**: Attach jurisdiction, consent flags, or data retention policies
- **Debugging**: Add trace IDs, feature flags, or environment identifiers
- **Analytics**: Store custom dimensions for downstream analysis

**Example - Retrieving metadata from events:**

```python
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=queue,
    run_config=RunConfig(
        custom_metadata={"user_id": "user_123", "experiment": "new_ui"}
    )
):
    if event.custom_metadata:
        print(f"User: {event.custom_metadata.get('user_id')}")
        print(f"Experiment: {event.custom_metadata.get('experiment')}")
```

**Agent-to-Agent (A2A) integration:**

When using `RemoteA2AAgent`, ADK automatically extracts metadata from A2A requests and populates `custom_metadata`:

```python
# A2A request metadata is automatically mapped to custom_metadata
# Source: a2a/converters/request_converter.py
custom_metadata = {
    "a2a_metadata": {
        # Original A2A request metadata appears here
    }
}
```

This enables seamless metadata propagation across agent boundaries in multi-agent architectures.

**Best practices:**

- Use consistent key naming conventions across your application
- Avoid storing sensitive data (PII, credentials) in metadata—use encryption if necessary
- Keep metadata size reasonable to minimize storage overhead
- Document your metadata schema for team consistency
- Consider using metadata for session filtering and search in production debugging

### Other live-related fields

`RunConfig` carries a few more fields that only take effect on the `run_live()` path. They
are passed straight through to `live_connect_config`
([`basic.py:123-152`](https://github.com/google/adk-python/blob/096ecfcf56ad47a9a63da1d76a062f56d7586692/src/google/adk/flows/llm_flows/basic.py#L123-L152)),
so their exact behavior is defined by the Live API rather than by ADK:

| Field | Type | What it does |
|-------|------|--------------|
| `explicit_vad_signal` | `bool` | Asks the model to emit explicit voice activity signals. ADK surfaces them on `event.voice_activity` instead of inferring turn boundaries from content |
| `translation_config` | `types.TranslationConfig` | Enables real-time speech-to-speech translation. Takes `target_language_code` (BCP-47) and `echo_target_language`. **Only supported by translation models** such as `gemini-3.5-live-translate-preview` — not by the native audio models in [Supported models](models.md#native-audio-models) |
| `avatar_config` | `types.AvatarConfig` | Renders the agent as an animated avatar. Takes `avatar_name` (a prebuilt avatar) or `customized_avatar`, plus `audio_bitrate_bps` / `video_bitrate_bps` |

```python
from google.genai import types

run_config = RunConfig(
    response_modalities=["AUDIO"],
    explicit_vad_signal=True,
)
```

One more field is not live-specific but is often useful in a live session:

- **`model_input_context`** (`list[types.Content]`): transient context injected into the LLM
  request for the current invocation only. The `Runner` does not persist it to the session,
  which makes it a clean way to supply per-turn grounding (a document the user just opened, a
  page they are viewing) without polluting conversation history.

### support_cfc (Experimental)

This parameter enables Compositional Function Calling (CFC), allowing the model to orchestrate multiple tools in sophisticated patterns—calling tools in parallel, chaining outputs as inputs to other tools, or conditionally executing tools based on intermediate results.

**⚠️ Experimental Feature:** CFC support is experimental and subject to change.

**Critical behavior:** When `support_cfc=True`, ADK **always uses the Live API** (WebSocket) internally, regardless of the `streaming_mode` setting. This is because only the Live API backend supports CFC capabilities.

```python
# Even with SSE mode, ADK routes through Live API when CFC is enabled
run_config = RunConfig(
    support_cfc=True,
    streaming_mode=StreamingMode.SSE  # ADK uses Live API internally
)
```

**Model requirements:**

ADK validates CFC compatibility at session initialization and will raise an error if the model is unsupported:

- ✅ **Supported**: `gemini-2.x` models (e.g., `gemini-2.5-flash-native-audio-preview-12-2025`)
- ❌ **Not supported**: any model whose name does not start with `gemini-2` — this includes both `gemini-1.5-x` and, today, `gemini-3.1-flash-live-preview`
- **Validation**: ADK checks that the model name starts with `gemini-2` when `support_cfc=True` ([`runners.py:2098-2104`](https://github.com/google/adk-python/blob/096ecfcf56ad47a9a63da1d76a062f56d7586692/src/google/adk/runners.py#L2098-L2104)). The check is a literal prefix match, so a Gemini 3.x model raises `ValueError: CFC is not supported for model: ...` even though the underlying Live API session would work
- **Code executor**: ADK automatically injects `BuiltInCodeExecutor` when CFC is enabled for safe parallel tool execution

**CFC capabilities:**

- **Parallel execution**: Call multiple independent tools simultaneously (e.g., fetch weather for multiple cities at once)
- **Function chaining**: Use one tool's output as input to another (e.g., `get_location()` → `get_weather(location)`)
- **Conditional execution**: Execute tools based on intermediate results from prior tool calls

**Use cases:**

CFC is designed for complex, multi-step workflows that benefit from intelligent tool orchestration:

- Data aggregation from multiple APIs simultaneously
- Multi-step analysis pipelines where tools feed into each other
- Complex research tasks requiring conditional exploration
- Any scenario needing sophisticated tool coordination beyond sequential execution

**For bidirectional streaming applications:** While CFC works with `run_live()`, it's primarily optimized for text-based tool orchestration. For real-time audio/video interactions (the focus of this guide), standard function calling typically provides better performance and simpler implementation.

**Learn more:**

- [Gemini Function Calling Guide](https://ai.google.dev/gemini-api/docs/function-calling) - Official documentation on compositional and parallel function calling
- [ADK Parallel Functions Example](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/contributing/samples/parallel_functions/agent.py) - Working example with async tools
- [ADK Performance Guide](/tools-custom/performance/) - Best practices for parallel-ready tools

