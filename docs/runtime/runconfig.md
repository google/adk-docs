# Runtime Configuration

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

`RunConfig` controls how agents behave at runtime, including streaming mode,
speech settings, LLM call limits, and live agent options. Pass a `RunConfig`
to `runner.run_async()` or `runner.run_live()` to override default behavior.

=== "Python"

    ```python
    --8<-- "examples/inline/python/runtime/runconfig/001-runtime-configuration.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/runtime/runconfig/002-runtime-configuration.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/runtime/runconfig/003-runtime-configuration.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/runtime/runconfig/004-runtime-configuration.java"
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
    --8<-- "examples/inline/python/runtime/runconfig/005-manage-sessions-and-context.py"
    ```

## Enable streaming

To control how the agent delivers responses, set the `streaming_mode` parameter:

- **`StreamingMode.NONE`** (default): The runner returns one complete response
  per turn. Suitable for CLI tools, batch processing, and synchronous workflows.
- **`StreamingMode.SSE`**: Server-Sent Events streaming. The runner yields
  partial events as the LLM generates, enabling typewriter-style UIs and
  real-time chat displays.
- **`StreamingMode.BIDI`**: Reserved for bidirectional streaming, but **not
  used** in the standard `run_async()` path. For bidirectional streaming, use
  `runner.run_live()` instead.

Set `support_cfc=True` alongside `StreamingMode.SSE` to enable Compositional
Function Calling (CFC), which allows the model to dynamically compose and
execute function calls. CFC uses the Live API under the hood.

!!! example "Experimental"
    CFC support is experimental and its API or behavior may change in future
    releases.

=== "Python"

    ```python
    --8<-- "examples/inline/python/runtime/runconfig/006-enable-streaming.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/runtime/runconfig/007-enable-streaming.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/runtime/runconfig/003-runtime-configuration.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/runtime/runconfig/009-enable-streaming.java"
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

- `speech_config`: Sets the voice and language for speech output (e.g., the
  "Kore" voice with `en-US`).
- `response_modalities`: Controls output formats. Set to `["AUDIO", "TEXT"]` for
  agents that both speak and return text.
- `output_audio_transcription` / `input_audio_transcription`: Enable
  transcription of audio output from the model and audio input from the user.
  Both default to `AudioTranscriptionConfig()` in Python.

=== "Python"

    ```python
    --8<-- "examples/inline/python/runtime/runconfig/010-configure-audio-and-speech.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/runtime/runconfig/011-configure-audio-and-speech.ts"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/runtime/runconfig/012-configure-audio-and-speech.java"
    ```

## Configure live agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

When using `runner.run_live()`, configure real-time behavior with these
additional parameters:

- `realtime_input_config`: Configures how audio input is received from users.
- `proactivity`: Allows the model to respond proactively and ignore irrelevant
  input.
- `enable_affective_dialog`: When `True`, the model detects user emotions and
  adapts its tone accordingly.
- `avatar_config`: Configures an avatar for live agents.
- `session_resumption`: Enables transparent session resumption across
  disconnects.
- `save_live_blob`: When `True`, saves live audio and video data to the session
  and artifact service.
- `tool_thread_pool_config`: Runs tool executions in a background thread pool
  to keep the event loop responsive to user interruptions.
- `explicit_vad_signal`: Enables explicit voice activity detection (VAD)
  signals from the model.
- `history_config`: Configures the exchange of history between the client and
  the server.
- `translation_config`: Configures real-time speech-to-speech translation. Only
  translation models support it.

Not all parameters are available in every language. See the
[API reference](#api-reference) for language-specific details.

=== "Python"

    ```python
    --8<-- "examples/inline/python/runtime/runconfig/013-configure-live-agents.py"
    ```

    !!! note "Thread pool and the GIL"
        Thread pools help with blocking I/O and C extensions that release the
        GIL (e.g. `time.sleep()`, network calls, numpy). They do **not** help
        with pure Python CPU-bound code since the GIL prevents true parallel
        execution of Python bytecode.

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/runtime/runconfig/014-configure-live-agents.ts"
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
