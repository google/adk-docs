# Configuration for live agents

Supported in ADKPython v0.1.0Java v0.2.0

`RunConfig` is where you shape a live session: how the agent sounds, how it transcribes speech, when it decides a turn is over, how much history it keeps, and what limits it runs under. You pass it to [`Runner.run_live()`](https://google.github.io/adk-docs/api-reference/python/), and it applies to that session only. Two users of the same agent can run with completely different configurations.

`RunConfig` is not live-specific; [Runtime configuration](https://adk.dev/runtime/runconfig/index.md) documents the full class and the fields that apply to `run_async()`. What follows is the subset that matters under `run_live()`, plus the voice-facing settings that only exist in a live session.

## RunConfig Parameter Quick Reference

This table provides a quick reference for the `RunConfig` parameters that matter most to live agents:

| Parameter                      | Type                           | Purpose                                                                             | Reference                                                             |
| ------------------------------ | ------------------------------ | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| **response_modalities**        | list[str]                      | Output format. Live agents must use `AUDIO` — Live models do not accept `TEXT`      | [Details](#response-modalities)                                       |
| **streaming_mode**             | StreamingMode                  | Chunked or single-shot delivery on the `run_async()` path; not read by `run_live()` | [Details](#streamingmode-bidi-or-sse)                                 |
| **session_resumption**         | SessionResumptionConfig        | Enable automatic reconnection                                                       | [Details](https://adk.dev/live/sessions/#session-resumption)          |
| **context_window_compression** | ContextWindowCompressionConfig | Unlimited session duration                                                          | [Details](https://adk.dev/live/sessions/#context-window-compression)  |
| **history_config**             | HistoryConfig                  | Control how prior conversation history is replayed to the Live server               | [Details](#history_config)                                            |
| **max_llm_calls**              | int                            | Limit total LLM calls per session                                                   | [Details](#max_llm_calls)                                             |
| **save_live_blob**             | bool                           | Persist audio/video streams                                                         | [Details](#save_live_blob)                                            |
| **custom_metadata**            | dict[str, Any]                 | Attach metadata to invocation events                                                | [Details](#custom_metadata)                                           |
| **speech_config**              | SpeechConfig                   | Voice and language configuration                                                    | [Voice and language](#voice-and-language)                             |
| **input_audio_transcription**  | AudioTranscriptionConfig       | Transcribe user speech                                                              | [Audio transcription](#audio-transcription)                           |
| **output_audio_transcription** | AudioTranscriptionConfig       | Transcribe model speech                                                             | [Audio transcription](#audio-transcription)                           |
| **realtime_input_config**      | RealtimeInputConfig            | VAD configuration                                                                   | [Voice activity detection](#voice-activity-detection-vad)             |
| **explicit_vad_signal**        | bool                           | Emit voice activity events from the model                                           | [Details](#other-live-related-fields)                                 |
| **proactivity**                | ProactivityConfig              | Enable proactive audio (model-specific)                                             | [Proactivity and affective dialog](#proactivity-and-affective-dialog) |
| **enable_affective_dialog**    | bool                           | Emotional adaptation (model-specific)                                               | [Proactivity and affective dialog](#proactivity-and-affective-dialog) |
| **translation_config**         | TranslationConfig              | Real-time speech-to-speech translation (translation models only)                    | [Details](#other-live-related-fields)                                 |
| **avatar_config**              | AvatarConfig                   | Render the agent as an animated avatar                                              | [Details](#other-live-related-fields)                                 |

For more details on configuration options, see [`RunConfig`](https://adk.dev/api-reference/python/google-adk.html#google.adk.agents.RunConfig) in the Python API reference.

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

## Response modes

The `response_modalities` setting controls the output format, and a session gets exactly one. **For live agents the value is always `["AUDIO"]`**, because every [Live model](https://adk.dev/live/models/#live-models) ADK supports accepts no other modality. ADK fills this in for you when you leave it unset, so most live applications never touch the field.

Migrating from `response_modalities=["TEXT"]`

Older ADK samples and half-cascade models allowed a text-only live session. That no longer works: `run_live()` with `["TEXT"]` fails against current Live models, which only produce audio.

**To get text out of a live agent, read [`event.output_transcription`](#audio-transcription)**: transcription is enabled by default in ADK, so deleting the `response_modalities` line is usually the whole fix.

`["TEXT"]` is still correct on the `run_async()` path, which runs on standard Gemini models. See [Bidi-streaming or SSE](#streamingmode-bidi-or-sse).

Response modality only affects model output — **you can always send text, voice, or video input** (if the model supports that input modality) regardless of it.

## Bidi-streaming or SSE

ADK can reach Gemini over two different endpoints, and **the `Runner` method you call is what picks one**:

- **`runner.run_live()`**: ADK opens a WebSocket to the **Live API** (the bidirectional streaming endpoint via `live.connect()`). This is what the rest of this guide covers, and it is required for real-time audio and video
- **`runner.run_async()`**: ADK uses HTTP to the **standard Gemini API** (the unary/streaming endpoint via `generate_content_async()`). Set `RunConfig.streaming_mode = StreamingMode.SSE` to stream that response back chunk by chunk

The two model sets barely overlap. Standard Gemini models such as `gemini-flash-latest` do not hold a bidirectional connection, and the models in [Supported models](https://adk.dev/live/models/#live-models) are meant to be driven with `run_live()`, so choosing a model is part of choosing a `Runner` method.

Python: `StreamingMode.BIDI` does not switch ADK to the Live API

In **Python**, `RunConfig.streaming_mode` is read only on the `run_async()` code path, where it chooses between a single complete response (`StreamingMode.NONE`, the default) and chunked delivery (`StreamingMode.SSE`). The `run_live()` path never reads it, so setting `streaming_mode=StreamingMode.BIDI` has no effect and fails silently. **Calling `run_live()` is what gets you bidirectional streaming.** ADK's own Python `StreamingMode` docstring says as much: BIDI "is not used in the standard execution path", and the real bidirectional behavior "uses a completely different code path that doesn't rely on `streaming_mode`".

**Java differs.** ADK Java's flow does read `StreamingMode.BIDI`, and the Java quickstart sets it explicitly on the `RunConfig` it passes to `runLive()`. Follow each language's quickstart rather than porting the setting across.

```python
# Live API: no streaming_mode needed, calling run_live() is what selects it
run_config = RunConfig(response_modalities=["AUDIO"])
async for event in runner.run_live(..., run_config=run_config):
    ...
```

This choice affects only how ADK talks to Gemini. Your client-facing architecture is independent: you can build WebSocket servers, REST APIs, or SSE endpoints on either path.

[Runtime configuration](https://adk.dev/runtime/runconfig/#enable-streaming) covers the `run_async()` and SSE path: `streaming_mode` values, progressive SSE streaming, and the language-specific configuration.

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
)
```

### max_llm_calls

`max_llm_calls` caps LLM invocations per invocation context, and [Runtime configuration](https://adk.dev/runtime/runconfig/#configure-runtime-limits-and-debugging) documents it in full.

**It does not apply to `run_live()`.** The parameter only guards the `run_async()` path, so a live session gets no automatic cost ceiling from it. Budget your own: cap session duration, count turns, watch `usage_metadata` on model events ([Metadata](https://adk.dev/live/events/#metadata)), and put a circuit breaker in front of the loop.

### save_live_blob

`save_live_blob=True` persists the session's audio to the [session service](https://adk.dev/sessions/index.md) as references and to the [artifact service](https://adk.dev/artifacts/index.md) as files. Despite the name, **only audio is persisted** today, not video.

Enable it for debugging voice behavior, or for audit trails in regulated environments. Leave it off otherwise: 16 kHz PCM input runs about **1.92 MB per minute per session**, written to two services, and that accumulates fast on a voice workload. If you need it in production, sample a fraction of sessions rather than all of them, and set a retention policy on the artifact service — ADK does not expire these for you.

`save_live_audio` is deprecated

ADK migrates `save_live_audio=True` to `save_live_blob=True` automatically and warns, but the shim will be removed in a future release. Update to `save_live_blob`.

### history_config

When ADK opens a **new** Live API connection for a session that already has conversation history, it replays that history to the server. That history includes the model's own past turns, so the server has to be told not to answer them again. ADK handles this for you: before connecting, it sets `live_connect_config.history_config.initial_history_in_client_content = True` whenever there is history to send and no session resumption handle is in play.

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

- **You normally do nothing.** ADK only fills in the value when you have not set one, so an explicit `history_config` on `RunConfig` always wins.
- **Reconnections skip history entirely.** When ADK reconnects with a session resumption handle, the server already holds the state for that session, so ADK sends no history and does not touch `history_config`.
- **Symptom if it goes wrong**: setting `initial_history_in_client_content=False` while seeding history makes the model respond to the *replayed* turns, producing a burst of duplicate answers at the start of the connection.

### custom_metadata

`custom_metadata` attaches an arbitrary JSON-serializable dict to every `Event` in the invocation, and it behaves the same in a live session as anywhere else — see [Runtime configuration](https://adk.dev/runtime/runconfig/#configure-runtime-limits-and-debugging).

```python
run_config = RunConfig(
    response_modalities=["AUDIO"],
    custom_metadata={"user_tier": "premium", "session_type": "support"},
)
```

The live-specific consequence is scope: one `run_live()` call is one invocation, so the metadata is stamped on every event for the entire streaming session rather than a single turn. Read it back with `event.custom_metadata`.

Do not put sensitive data in `custom_metadata`

Every event carrying this metadata is persisted to the session service. Keep PII, credentials, and other sensitive values out of it, and encrypt them if you have no alternative.

### Other live-related fields

`RunConfig` carries a few more fields that only take effect on the `run_live()` path. ADK passes them straight through to the live connection, so their exact behavior is defined by the Live API rather than by ADK:

| Field                 | Type                      | What it does                                                                                                                                                                                                                                                                               |
| --------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `explicit_vad_signal` | `bool`                    | Asks the model to emit explicit voice activity signals. ADK surfaces them on `event.voice_activity` instead of inferring turn boundaries from content                                                                                                                                      |
| `translation_config`  | `types.TranslationConfig` | Enables real-time speech-to-speech translation. Takes `target_language_code` (BCP-47) and `echo_target_language`. **Only supported by translation models** such as `gemini-3.5-live-translate-preview` — not by the models in [Supported models](https://adk.dev/live/models/#live-models) |
| `avatar_config`       | `types.AvatarConfig`      | Renders the agent as an animated avatar. Takes `avatar_name` (a prebuilt avatar) or `customized_avatar`, plus `audio_bitrate_bps` / `video_bitrate_bps`                                                                                                                                    |

```python
from google.genai import types

run_config = RunConfig(
    response_modalities=["AUDIO"],
    explicit_vad_signal=True,
)
```

One more field is not live-specific but is often useful in a live session:

- **`model_input_context`** (`list[types.Content]`): transient context injected into the LLM request for the current invocation only. The `Runner` does not persist it to the session, which makes it a clean way to supply per-turn grounding (a document the user just opened, a page they are viewing) without polluting conversation history.

### Compositional function calling (support_cfc)

Compositional Function Calling (CFC) is a `run_async()` / SSE feature, not a live one: it applies to the current Live models only in theory, since none of them satisfy its model requirement. Leave `support_cfc` for the SSE path and use standard function calling in live sessions (see [Tools](https://adk.dev/live/tools/index.md)). For the parameter itself, see [Runtime configuration](https://adk.dev/runtime/runconfig/index.md).

## Audio transcription

The Live API transcribes both sides of the conversation for you, so you can show captions, log conversations, and support accessibility without a separate speech-to-text service. **Transcription is on by default in ADK** for both input (user speech) and output (model speech). Set a field to `None` to turn that direction off.

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

# On by default. This is equivalent to setting both to AudioTranscriptionConfig().
run_config = RunConfig(response_modalities=["AUDIO"])

# Turn off user-input transcription, keep model-output transcription.
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,
)
```

Transcriptions arrive as `types.Transcription` objects on `event.input_transcription` and `event.output_transcription`, separate from `event.content`. They stream in fragments: `.text` holds the latest fragment and `.finished` marks the last one for the turn. Concatenate the fragments to build the full transcript.

```python
async for event in runner.run_live(...):
    if event.input_transcription and event.input_transcription.text:
        update_caption(
            event.input_transcription.text,
            is_user=True,
            is_final=event.input_transcription.finished,
        )
    if event.output_transcription and event.output_transcription.text:
        update_caption(
            event.output_transcription.text,
            is_user=False,
            is_final=event.output_transcription.finished,
        )
```

For the event structure, see [Transcription events](https://adk.dev/live/events/#transcription).

Multi-agent sessions always transcribe

When the root agent has `sub_agents`, `run_live()` enables both input and output transcription even if you set them to `None`. Agent transfer needs the text transcript to pass conversation context to the next agent, so it cannot be disabled ([`runners.py`](https://github.com/google/adk-python/blob/main/src/google/adk/runners.py)).

## Voice and language

Set `speech_config` to choose the model's voice and language. You can set it in two places:

- **On the agent**, by passing a `Gemini` instance with a `speech_config`. Use this to give each agent in a multi-agent workflow its own voice.
- **On the session**, by setting `RunConfig.speech_config`. Use this for one voice across the whole session.

When both are set, **the agent-level voice wins**. With neither set, the Live API picks a default voice.

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.agents.run_config import RunConfig

# Agent-level voice (wins over RunConfig).
agent = Agent(
    model=Gemini(
        model="gemini-live-2.5-flash-native-audio",
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
            ),
            language_code="en-US",
        ),
    ),
    instruction="You are a helpful assistant.",
)

# Session-level default voice, used by any agent without its own.
run_config = RunConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
        ),
    ),
)
```

`voice_name` selects a prebuilt voice. [Live models](https://adk.dev/live/models/#live-models) support eight (Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr) plus the extended [Text-to-Speech voice list](https://cloud.google.com/text-to-speech/docs/voices). For the current list and per-backend availability, see the [Gemini Live API voice documentation](https://ai.google.dev/gemini-api/docs/live-api/capabilities#change-voice-and-language). An unsupported voice returns an error at connection time.

`language_code` (for example `en-US`, `ja-JP`) sets the language and accent. Live models often infer the language from the conversation and may ignore it.

## Voice activity detection (VAD)

VAD detects when the user starts and stops speaking so the model can take turns naturally, including handling interruptions. **It is on by default** on all [Live models](https://adk.dev/live/models/#live-models), and most applications need no configuration.

Disable automatic VAD when your application decides turn boundaries itself: push-to-talk, client-side VAD, or any UX where the user signals when they are done. When you disable it, you must send manual `ActivityStart`/`ActivityEnd` signals with [`send_activity_start()` / `send_activity_end()`](https://adk.dev/live/sessions/#liverequestqueue), and your client must translate its own turn signals into those calls on the server.

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(disabled=True)
    ),
)
```

A client that runs its own VAD sends those signals to your server, which forwards them with `send_activity_start()` / `send_activity_end()`. See [Connect a client](https://adk.dev/live/custom-server/#connect-a-client).

## Proactivity and affective dialog

Some Live models offer two conversational features, both off by default:

- **Proactive audio** (`proactivity`) lets the model decide when to respond, offer suggestions unprompted, or ignore irrelevant input.
- **Affective dialog** (`enable_affective_dialog`) lets the model detect emotion in the user's tone and adapt its response.

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    proactivity=types.ProactivityConfig(proactive_audio=True),
    enable_affective_dialog=True,
)
```

Both behaviors are probabilistic and make responses less predictable, so leave them off for formal or high-precision contexts and while debugging.

These settings apply to `gemini-live-2.5-flash-native-audio`. Some Live models build the behavior in and ignore both settings, so you do not need to set them. See [Supported models](https://adk.dev/live/models/#live-models).
