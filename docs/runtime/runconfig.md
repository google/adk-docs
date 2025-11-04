# Runtime Configuration

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

`RunConfig` defines runtime behavior and options for agents in the ADK. It
controls speech and streaming settings, function calling, artifact saving, and
limits on LLM calls.

When constructing an agent run, you can pass a `RunConfig` to customize how the
agent interacts with models, handles audio, and streams responses. By default,
no streaming is enabled and inputs aren’t retained as artifacts. Use `RunConfig`
to override these defaults.

## Class Definition

The `RunConfig` class holds configuration parameters for an agent's runtime behavior.

- Python ADK uses Pydantic for this validation.

- Java ADK typically uses immutable data classes.

- Go ADK has mutable structs by default.

=== "Python"

    ```python
    class RunConfig(BaseModel):
        """Configs for runtime behavior of agents."""

        model_config = ConfigDict(
            extra='forbid',
        )

        speech_config: Optional[types.SpeechConfig] = None
        response_modalities: Optional[list[str]] = None
        save_input_blobs_as_artifacts: bool = False
        support_cfc: bool = False
        streaming_mode: StreamingMode = StreamingMode.NONE
        output_audio_transcription: Optional[types.AudioTranscriptionConfig] = None
        max_llm_calls: int = 500
    ```

=== "Java"

    ```java
    public abstract class RunConfig {

      public enum StreamingMode {
        NONE,
        SSE,
        BIDI
      }

      public abstract @Nullable SpeechConfig speechConfig();

      public abstract ImmutableList<Modality> responseModalities();

      public abstract boolean saveInputBlobsAsArtifacts();

      public abstract @Nullable AudioTranscriptionConfig outputAudioTranscription();

      public abstract int maxLlmCalls();

      // ...
    }
    ```

=== "Go"

    ```go
    import "google.golang.org/genai"

    type StreamingMode string

    const (
    	StreamingModeNone StreamingMode = "none"
    	StreamingModeSSE  StreamingMode = "sse"
    	StreamingModeBidi StreamingMode = "bidi"
    )

    // RunConfig controls runtime behavior.
    type RunConfig struct {
    	// Speech configuration for the live agent.
    	SpeechConfig *genai.SpeechConfig
    	// Output transcription for live agents with audio response.
    	OutputAudioTranscriptionConfig *genai.AudioTranscriptionConfig
    	// The output modalities. If not set, it defaults to AUDIO.
    	ResponseModalities []string
    	// Streaming mode, None or StreamingMode.SSE or StreamingMode.BIDI.
    	StreamingMode StreamingMode
    	// Whether or not to save the input blobs as artifacts
    	SaveInputBlobsAsArtifacts bool

    	// Whether to support CFC (Compositional Function Calling). Only applicable for
    	// StreamingModeSSE. If it's true. the LIVE API will be invoked since only LIVE
    	// API supports CFC.
    	//
    	// .. warning::
    	//      This feature is **experimental** and its API or behavior may change
    	//     in future releases.
    	SupportCFC bool

    	// A limit on the total number of llm calls for a given run.
    	//
    	// Valid Values:
    	//  - More than 0 and less than sys.maxsize: The bound on the number of llm
    	//    calls is enforced, if the value is set in this range.
    	//  - Less than or equal to 0: This allows for unbounded number of llm calls.
    	MaxLLMCalls int
    }
    ```

## Runtime Parameters

| Parameter                       | Python Type                                  | Java Type                                             | Go Type                               | Default (Py / Java / Go)               | Description                                                                                                                  |
| :------------------------------ | :------------------------------------------- |:------------------------------------------------------|:--------------------------------------|:---------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------|
| `speech_config`                 | `Optional[types.SpeechConfig]`               | `SpeechConfig` (nullable via `@Nullable`)             | `*genai.SpeechConfig`                 | `None` / `null` / `nil`                | Configures speech synthesis (voice, language) using the `SpeechConfig` type.                                                 |
| `response_modalities`           | `Optional[list[str]]`                        | `ImmutableList<Modality>`                             | `[]string`                            | `None` / Empty `ImmutableList` / `AUDIO` | List of desired output modalities (e.g., Python: `["TEXT", "AUDIO"]`; Java: uses structured `Modality` objects).             |
| `save_input_blobs_as_artifacts` | `bool`                                       | `boolean`                                             | `bool`                                | `False` / `false` / `false`            | If `true`, saves input blobs (e.g., uploaded files) as run artifacts for debugging/auditing.                                 |
| `streaming_mode`                | `StreamingMode`                              | `StreamingMode`                                       | `StreamingMode`                       | `StreamingMode.NONE` / `StreamingMode.NONE` / `agent.StreamingModeNone` | Sets the streaming behavior: `NONE` (default), `SSE` (server-sent events), or `BIDI` (bidirectional).                        |
| `output_audio_transcription`    | `Optional[types.AudioTranscriptionConfig]`   | `AudioTranscriptionConfig` (nullable via `@Nullable`) | `*genai.AudioTranscriptionConfig`     | `None` / `null` / `nil`                | Configures transcription of generated audio output using the `AudioTranscriptionConfig` type.                                |
| `max_llm_calls`                 | `int`                                        | `int`                                                 | `int`                                 | `500` / `500` / `0` (unlimited)        | Limits total LLM calls per run. `0` or negative means unlimited (warned); `sys.maxsize` raises `ValueError`.                 |
| `support_cfc`                   | `bool`                                       | `bool`                                                | `bool`                                | `False` / `false` / `false`            | **Python/Go:** Enables Compositional Function Calling. Requires `streaming_mode=SSE` and uses the LIVE API. **Experimental.**   |

### `speech_config`

!!! Note
    The interface or definition of `SpeechConfig` is the same, irrespective of the language.

Speech configuration settings for live agents with audio capabilities. The
`SpeechConfig` class has the following structure:

```python
class SpeechConfig(_common.BaseModel):
    """The speech generation configuration."""

    voice_config: Optional[VoiceConfig] = Field(
        default=None,
        description="""The configuration for the speaker to use.""",
    )
    language_code: Optional[str] = Field(
        default=None,
        description="""Language code (ISO 639. e.g. en-US) for the speech synthesization.
        Only available for Live API.""",
    )
```

The `voice_config` parameter uses the `VoiceConfig` class:

```python
class VoiceConfig(_common.BaseModel):
    """The configuration for the voice to use."""

    prebuilt_voice_config: Optional[PrebuiltVoiceConfig] = Field(
        default=None,
        description="""The configuration for the speaker to use.""",
    )
```

And `PrebuiltVoiceConfig` has the following structure:

```python
class PrebuiltVoiceConfig(_common.BaseModel):
    """The configuration for the prebuilt speaker to use."""

    voice_name: Optional[str] = Field(
        default=None,
        description="""The name of the prebuilt voice to use.""",
    )
```

These nested configuration classes allow you to specify:

* `voice_config`: The name of the prebuilt voice to use (in the `PrebuiltVoiceConfig`)
* `language_code`: ISO 639 language code (e.g., "en-US") for speech synthesis

When implementing voice-enabled agents, configure these parameters to control
how your agent sounds when speaking.

### `response_modalities`

Defines the output modalities for the agent. If not set, defaults to AUDIO.
Response modalities determine how the agent communicates with users through
various channels (e.g., text, audio).

### `save_input_blobs_as_artifacts`

When enabled, input blobs will be saved as artifacts during agent execution.
This is useful for debugging and audit purposes, allowing developers to review
the exact data received by agents.

### `support_cfc`

Enables Compositional Function Calling (CFC) support. Only applicable when using
StreamingMode.SSE. When enabled, the LIVE API will be invoked as only it
supports CFC functionality.

!!! example "Experimental release"

    The `support_cfc` feature is experimental and its API or behavior might
    change in future releases.

### `streaming_mode`

Configures the streaming behavior of the agent. Possible values:

* `StreamingMode.NONE`: No streaming; responses delivered as complete units
* `StreamingMode.SSE`: Server-Sent Events streaming; one-way streaming from server to client
* `StreamingMode.BIDI`: Bidirectional streaming; simultaneous communication in both directions

Streaming modes affect both performance and user experience. SSE streaming lets users see partial responses as they're generated, while BIDI streaming enables real-time interactive experiences.

### `output_audio_transcription`

Configuration for transcribing audio outputs from live agents with audio
response capability. This enables automatic transcription of audio responses for
accessibility, record-keeping, and multi-modal applications.

### `max_llm_calls`

Sets a limit on the total number of LLM calls for a given agent run.

* Values greater than 0 and less than `sys.maxsize`: Enforces a bound on LLM calls
* Values less than or equal to 0: Allows unbounded LLM calls *(not recommended for production)*

This parameter prevents excessive API usage and potential runaway processes.
Since LLM calls often incur costs and consume resources, setting appropriate
limits is crucial.

## Validation Rules

The `RunConfig` class validates its parameters to ensure proper agent operation. While Python ADK uses `Pydantic` for automatic type validation, Java ADK relies on its static typing and may include explicit checks in the RunConfig's construction.
For the `max_llm_calls` parameter specifically:

1. Extremely large values (like `sys.maxsize` in Python or `Integer.MAX_VALUE` in Java) are typically disallowed to prevent issues.

2. Values of zero or less will usually trigger a warning about unlimited LLM interactions.

## Examples

### Basic runtime configuration

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.NONE,
        max_llm_calls=100
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;

    RunConfig config = RunConfig.builder()
            .setStreamingMode(StreamingMode.NONE)
            .setMaxLlmCalls(100)
            .build();
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeNone,
        MaxLLMCalls:   100,
    }
    ```

This configuration creates a non-streaming agent with a limit of 100 LLM calls,
suitable for simple task-oriented agents where complete responses are
preferable.

### Enabling streaming

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=200
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;

    RunConfig config = RunConfig.builder()
        .setStreamingMode(StreamingMode.SSE)
        .setMaxLlmCalls(200)
        .build();
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
        MaxLLMCalls:   200,
    }
    ```

Using SSE streaming allows users to see responses as they're generated,
providing a more responsive feel for chatbots and assistants.

### Enabling speech support

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
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
        save_input_blobs_as_artifacts=True,
        support_cfc=True,
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=1000,
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    import com.google.common.collect.ImmutableList;
    import com.google.genai.types.Content;
    import com.google.genai.types.Modality;
    import com.google.genai.types.Part;
    import com.google.genai.types.PrebuiltVoiceConfig;
    import com.google.genai.types.SpeechConfig;
    import com.google.genai.types.VoiceConfig;

    RunConfig runConfig =
        RunConfig.builder()
            .setStreamingMode(StreamingMode.SSE)
            .setMaxLlmCalls(1000)
            .setSaveInputBlobsAsArtifacts(true)
            .setResponseModalities(ImmutableList.of(new Modality("AUDIO"), new Modality("TEXT")))
            .setSpeechConfig(
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

=== "Go"

    ```go
    import (
    	"google.golang.org/adk/agent"
    	"google.golang.org/genai"
    )

    config := agent.RunConfig{
    	SpeechConfig: &genai.SpeechConfig{
    		LanguageCode: "en-US",
    		VoiceConfig: &genai.VoiceConfig{
    			PrebuiltVoiceConfig: &genai.PrebuiltVoiceConfig{
    				VoiceName: "Kore",
    			},
    		},
    	},
    	ResponseModalities:        []string{"AUDIO", "TEXT"},
    	SaveInputBlobsAsArtifacts: true,
    	SupportCFC:                true,
    	StreamingMode:             agent.StreamingModeSSE,
    	MaxLLMCalls:               1000,
    }
    ```

This comprehensive example configures an agent with:

* Speech capabilities using the "Kore" voice (US English)
* Both audio and text output modalities
* Artifact saving for input blobs (useful for debugging)
* SSE streaming for responsive interaction
* A limit of 1000 LLM calls

### Enabling Experimental CFC Support

<div class="language-support-tag" title="This feature is an experimental preview release.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-preview">Experimental</span>
</div>

```python
from google.genai.adk import RunConfig, StreamingMode

config = RunConfig(
    streaming_mode=StreamingMode.SSE,
    support_cfc=True,
    max_llm_calls=150
)
```

=== "Go"

    ```go
    import "google.golang.org/adk/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
        SupportCFC:    true,
        MaxLLMCalls:   150,
    }
    ```

Enabling Compositional Function Calling creates an agent that can dynamically
execute functions based on model outputs, powerful for applications requiring
complex workflows.
