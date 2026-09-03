# Runtime Configuration

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

`RunConfig` controls how agents behave at runtime, including streaming mode,
speech settings, LLM call limits, and live agent options. Pass a `RunConfig`
to `runner.run_async()` or `runner.run_live()` to override default behavior.

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=200,
    )

    async for event in runner.run_async(
        ...,
        run_config=config,
    ):
        ...
    ```

=== "TypeScript"

    ```typescript
    import { RunConfig, StreamingMode } from '@google/adk';

    const config: RunConfig = {
      streamingMode: StreamingMode.SSE,
      maxLlmCalls: 200,
    };
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/v2/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
    }
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;

    RunConfig config = RunConfig.builder()
        .streamingMode(StreamingMode.SSE)
        .maxLlmCalls(200)
        .build();
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/runtime/RunConfigExample.kt:basic_usage"
    ```

## Manage sessions and context

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

For long-running sessions, you can control how much history is loaded and
whether the context window is compressed:

- `get_session_config`: Limits which events are fetched when loading a session.
  Use `num_recent_events` or `after_timestamp` to avoid loading the full event
  history on every invocation.
- `context_window_compression`: Enables context window compression for LLM
  input, useful when sessions approach model context limits.
- `include_thoughts_from_other_agents`: Controls whether thought parts from
  other agents are included in the LLM context. Disabled by default.
- `model_input_context`: A list of `types.Content` added to the LLM request for
  this invocation only. The runner does not persist it to the session, so you
  can supply per-turn context without changing the conversation history.

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig
    from google.adk.sessions.base_session_service import GetSessionConfig

    config = RunConfig(
        get_session_config=GetSessionConfig(num_recent_events=50),
    )
    ```

## Text response options { #enable-streaming }

You can control how an agent responds in text mode, word-by-word as it is
generated, or as one full response, with the ***Streaming Mode*** parameter, as
described below:

- **`StreamingMode.NONE`** (default): The runner returns one complete response
  per turn. Suitable for CLI tools, batch processing, and synchronous workflows.
- **`StreamingMode.SSE`**: Server-Sent Events streaming. The runner yields
  partial events as the LLM generates, enabling typewriter-style UIs and
  real-time chat displays.

There is another setting for the ***Streaming Mode*** parameter which enables
bidirectional streaming of data, including voice input and output. This feature
requires additional configuration beyond simple agents. For more information
about this feature, see [Live and Voice Agents](../live/index.md).

Set `support_cfc=True` alongside `StreamingMode.SSE` to enable Compositional
Function Calling (CFC), which allows the model to dynamically compose and
execute function calls. CFC uses the Live API under the hood.

!!! example "Experimental"
    CFC support is experimental and its API or behavior may change in future
    releases.

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        support_cfc=True,
        max_llm_calls=150,
    )
    ```

=== "TypeScript"

    ```typescript
    import { RunConfig, StreamingMode } from '@google/adk';

    const config: RunConfig = {
        streamingMode: StreamingMode.SSE,
        maxLlmCalls: 150,
    };
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/v2/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
    }
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;

    RunConfig config = RunConfig.builder()
        .streamingMode(StreamingMode.SSE)
        .maxLlmCalls(150)
        .build();
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/runtime/RunConfigExample.kt:streaming_config"
    ```

## Configure audio and speech

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-java">Java</span>
</div>

For voice-enabled agents, configure speech synthesis, audio transcription, and
response modalities.

!!! tip "Live agents"

    This section covers the audio fields shared across languages. For the full live
    (`run_live()`) configuration reference — transcription streaming, voice selection,
    voice activity detection, and proactive/affective dialog — see
    [Live agent configuration](../live/configuration.md).

- `speech_config`: Sets the voice and language for speech output (e.g., the
  "Kore" voice with `en-US`).
- `response_modalities`: Controls the output format. A session accepts exactly one
  modality — use `["AUDIO"]` for voice agents and `["TEXT"]` for text-only ones.
  To get both speech and text, set `["AUDIO"]` and read the text from the output
  audio transcription.
- `output_audio_transcription` / `input_audio_transcription`: Enable
  transcription of audio output from the model and audio input from the user.
  Both default to `AudioTranscriptionConfig()` in Python.

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, StreamingMode
    from google.genai import types

    config = RunConfig(
        speech_config=types.SpeechConfig(
            language_code="en-US",
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"
                )
            ),
        ),
        response_modalities=["AUDIO"],
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=1000,
    )
    ```

=== "TypeScript"

    ```typescript
    import { RunConfig, StreamingMode } from '@google/adk';
    import { Modality } from '@google/genai';

    const config: RunConfig = {
        speechConfig: {
            languageCode: "en-US",
            voiceConfig: {
                prebuiltVoiceConfig: {
                    voiceName: "Kore"
                }
            },
        },
        responseModalities: [Modality.AUDIO],
        streamingMode: StreamingMode.SSE,
        maxLlmCalls: 1000,
    };
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    import com.google.common.collect.ImmutableList;
    import com.google.genai.types.Modality;
    import com.google.genai.types.PrebuiltVoiceConfig;
    import com.google.genai.types.SpeechConfig;
    import com.google.genai.types.VoiceConfig;

    RunConfig runConfig =
        RunConfig.builder()
            .streamingMode(StreamingMode.SSE)
            .maxLlmCalls(1000)
            .responseModalities(ImmutableList.of(new Modality(Modality.Known.AUDIO)))
            .speechConfig(
                SpeechConfig.builder()
                    .voiceConfig(
                        VoiceConfig.builder()
                            .prebuiltVoiceConfig(
                                PrebuiltVoiceConfig.builder().voiceName("Kore").build())
                            .build())
                    .languageCode("en-US")
                    .build())
            .build();
    ```

## Configure live agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-java">Java</span>
</div>

ADK agents can support [Live and Voice Agents](../live/index.md) to create
interactive agent experiences. You configure agents that support this
functionality using the `runner.run_live()` method.
Live agent (`run_live()`) sessions add a set of real-time parameters, including
`realtime_input_config`, `session_resumption`, `save_live_blob`,
`tool_thread_pool_config`, `proactivity`, `enable_affective_dialog`, and more.
For more information, see the live agent docs:

- **[Live agent configuration](../live/configuration.md)** — the full `RunConfig`
  reference for live agents.
- **[Sessions](../live/sessions.md#session-resumption)** — session resumption
  and reconnection.
- **[Configuration: proactivity and affective dialog](../live/configuration.md#proactivity-and-affective-dialog)** —
  native-audio conversational features and the models that support them.

The `tool_thread_pool_config` setting is an exception: it is a runtime concern rather than a
Live API one, so it stays here. It runs tool executions in a background thread
pool so the event loop keeps responding to user interruptions.
Not all parameters are available in every language. See the
[API reference](#api-reference) for language-specific details.

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, ToolThreadPoolConfig

    config = RunConfig(
        save_live_blob=True,
        tool_thread_pool_config=ToolThreadPoolConfig(max_workers=8),
    )
    ```

    !!! note "Thread pool and the GIL"
        Thread pools help with blocking I/O and C extensions that release the
        GIL (e.g. `time.sleep()`, network calls, numpy). They do **not** help
        with pure Python CPU-bound code since the GIL prevents true parallel
        execution of Python bytecode.

=== "TypeScript"

    ```typescript
    import { RunConfig } from '@google/adk';

    const config: RunConfig = {
        enableAffectiveDialog: true,
        proactivity: {
            proactiveAudio: true,
        },
    };
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.genai.types.AvatarConfig;

    RunConfig config = RunConfig.builder()
        .avatarConfig(
            AvatarConfig.builder()
                .avatarName("PREBUILT_AVATAR_ID")
                .build())
        .build();
    ```

## Configure runtime limits and debugging

Use these parameters to control runtime guardrails and debugging:

- `max_llm_calls`: Caps the total number of LLM calls per run (default: 500).
  Set to 0 or negative for unlimited calls, though this is not recommended for
  production. Passing your language's largest integer raises an error:
  `sys.maxsize` in Python, `Int.MAX_VALUE` in Kotlin.
- `save_input_blobs_as_artifacts`: When `True`, saves input blobs (e.g.,
  uploaded files) as run artifacts for debugging and auditing. Deprecated in
  Python in favor of `SaveFilesAsArtifactsPlugin`.
- `custom_metadata`: A `dict[str, Any]` of arbitrary metadata attached to the
  invocation, useful for tracing or logging.

## API reference

For the complete list of fields, types, and defaults, see the API reference for
your language:

- [Python API reference](../api-reference/python/google-adk.html#google.adk.agents.RunConfig)
- [TypeScript API reference](../api-reference/typescript/interfaces/RunConfig.html)
- [Go API reference](https://pkg.go.dev/google.golang.org/adk/v2/agent#RunConfig)
- [Java API reference](../api-reference/java/com/google/adk/agents/RunConfig.html)
- [Kotlin API reference](../api-reference/kotlin/google-adk-kotlin-core/com.google.adk.kt.agents/-run-config/index.html)
