# Runtime Configuration

Supported in ADKPython v0.1.0TypeScript v0.2.0Go v0.1.0Java v0.1.0Kotlin v0.1.0

`RunConfig` controls how agents behave at runtime, including streaming mode, speech settings, LLM call limits, and live agent options. Pass a `RunConfig` to `runner.run_async()` or `runner.run_live()` to override default behavior.

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

```typescript
import { RunConfig, StreamingMode } from '@google/adk';

const config: RunConfig = {
  streamingMode: StreamingMode.SSE,
  maxLlmCalls: 200,
};
```

```go
import "google.golang.org/adk/v2/agent"

config := agent.RunConfig{
    StreamingMode: agent.StreamingModeSSE,
}
```

```java
import com.google.adk.agents.RunConfig;
import com.google.adk.agents.RunConfig.StreamingMode;

RunConfig config = RunConfig.builder()
    .streamingMode(StreamingMode.SSE)
    .maxLlmCalls(200)
    .build();
```

```kotlin
val config =
    RunConfig(
        streamingMode = StreamingMode.SSE,
    )

// Pass it to runner.runAsync
// runner.runAsync(..., runConfig = config)
```

## Manage sessions and context

Supported in ADKPython

For long-running sessions, you can control how much history is loaded and whether the context window is compressed:

- `get_session_config`: Limits which events are fetched when loading a session. Use `num_recent_events` or `after_timestamp` to avoid loading the full event history on every invocation.
- `context_window_compression`: Enables context window compression for LLM input, useful when sessions approach model context limits.

```python
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.base_session_service import GetSessionConfig

config = RunConfig(
    get_session_config=GetSessionConfig(num_recent_events=50),
)
```

## Enable streaming

To control how the agent delivers responses, set the `streaming_mode` parameter:

- **`StreamingMode.NONE`** (default): The runner returns one complete response per turn. Suitable for CLI tools, batch processing, and synchronous workflows.
- **`StreamingMode.SSE`**: Server-Sent Events streaming. The runner yields partial events as the LLM generates, enabling typewriter-style UIs and real-time chat displays.
- **`StreamingMode.BIDI`**: Reserved for bidirectional streaming, but **not used** in the standard `run_async()` path. For bidirectional streaming, use `runner.run_live()` instead.

Set `support_cfc=True` alongside `StreamingMode.SSE` to enable Compositional Function Calling (CFC), which allows the model to dynamically compose and execute function calls. CFC uses the Live API under the hood.

Experimental

CFC support is experimental and its API or behavior may change in future releases.

```python
from google.adk.agents.run_config import RunConfig, StreamingMode

config = RunConfig(
    streaming_mode=StreamingMode.SSE,
    support_cfc=True,
    max_llm_calls=150,
)
```

```typescript
import { RunConfig, StreamingMode } from '@google/adk';

const config: RunConfig = {
    streamingMode: StreamingMode.SSE,
    supportCfc: true,
    maxLlmCalls: 150,
};
```

```go
import "google.golang.org/adk/v2/agent"

config := agent.RunConfig{
    StreamingMode: agent.StreamingModeSSE,
}
```

```java
import com.google.adk.agents.RunConfig;
import com.google.adk.agents.RunConfig.StreamingMode;

RunConfig config = RunConfig.builder()
    .streamingMode(StreamingMode.SSE)
    .maxLlmCalls(150)
    .build();
```

```kotlin
val streamingConfig =
    RunConfig(
        streamingMode = StreamingMode.SSE,
    )
```

## Configure audio and speech

Supported in ADKPythonTypeScriptJava

For voice-enabled agents, configure speech synthesis, audio transcription, and response modalities.

- `speech_config`: Sets the voice and language for speech output (e.g., the "Kore" voice with `en-US`).
- `response_modalities`: Controls output formats. Set to `["AUDIO", "TEXT"]` for agents that both speak and return text.
- `output_audio_transcription` / `input_audio_transcription`: Enable transcription of audio output from the model and audio input from the user. Both default to `AudioTranscriptionConfig()` in Python.

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
    response_modalities=["AUDIO", "TEXT"],
    streaming_mode=StreamingMode.SSE,
    max_llm_calls=1000,
)
```

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
    responseModalities: [Modality.AUDIO, Modality.TEXT],
    streamingMode: StreamingMode.SSE,
    maxLlmCalls: 1000,
};
```

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
        .responseModalities(ImmutableList.of(new Modality(Modality.Known.AUDIO), new Modality(Modality.Known.TEXT)))
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

Supported in ADKPythonTypeScript

When using `runner.run_live()`, configure real-time behavior with these additional parameters:

- `realtime_input_config`: Configures how audio input is received from users.
- `proactivity`: Allows the model to respond proactively and ignore irrelevant input.
- `enable_affective_dialog`: When `True`, the model detects user emotions and adapts its tone accordingly.
- `avatar_config`: Configures an avatar for live agents.
- `session_resumption`: Enables transparent session resumption across disconnects.
- `save_live_blob`: When `True`, saves live audio and video data to the session and artifact service.
- `tool_thread_pool_config`: Runs tool executions in a background thread pool to keep the event loop responsive to user interruptions.

Not all parameters are available in every language. See the [API reference](#api-reference) for language-specific details.

```python
from google.adk.agents.run_config import RunConfig, ToolThreadPoolConfig

config = RunConfig(
    save_live_blob=True,
    tool_thread_pool_config=ToolThreadPoolConfig(max_workers=8),
)
```

Thread pool and the GIL

Thread pools help with blocking I/O and C extensions that release the GIL (e.g. `time.sleep()`, network calls, numpy). They do **not** help with pure Python CPU-bound code since the GIL prevents true parallel execution of Python bytecode.

```typescript
import { RunConfig } from '@google/adk';

const config: RunConfig = {
    enableAffectiveDialog: true,
    proactivity: {
        proactiveAudio: true,
    },
};
```

## Configure runtime limits and debugging

Use these parameters to control runtime guardrails and debugging:

- `max_llm_calls`: Caps the total number of LLM calls per run (default: 500). Set to 0 or negative for unlimited calls, though this is not recommended for production. Values at or above `sys.maxsize` raise an error.
- `save_input_blobs_as_artifacts`: When `True`, saves input blobs (e.g., uploaded files) as run artifacts for debugging and auditing.
- `custom_metadata`: A `dict[str, Any]` of arbitrary metadata attached to the invocation, useful for tracing or logging.

## API reference

For the complete list of fields, types, and defaults, see the API reference for your language:

- [Python API reference](https://adk.dev/api-reference/python/google-adk.html#google.adk.agents.RunConfig)
- [TypeScript API reference](https://adk.dev/api-reference/typescript/interfaces/RunConfig.html)
- [Go API reference](https://pkg.go.dev/google.golang.org/adk/v2/agent#RunConfig)
- [Java API reference](https://adk.dev/api-reference/java/com/google/adk/agents/RunConfig.html)
- [Kotlin API reference](https://adk.dev/api-reference/kotlin/google-adk-kotlin-core/com.google.adk.kt.agents/-run-config/index.md)
