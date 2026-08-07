# Voice

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-preview">Experimental</span>
</div>

Once audio is flowing, the remaining decisions are about how the conversation *sounds*
and how the agent decides when to speak. This page covers transcription of both sides of
the conversation, choosing a voice and language, voice activity detection — how the model
knows a user has stopped talking — and the proactive and affective behaviors available on
native audio models.

For the mechanics of moving audio bytes in and out, see
[Audio and video](audio-video.md). For the rest of `RunConfig`, see
[Configuration](configuration.md).

## Audio Transcription

The Live API provides built-in audio transcription capabilities that automatically convert speech to text for both user input and model output. This eliminates the need for external transcription services and enables real-time captions, conversation logging, and accessibility features. ADK exposes these capabilities through `RunConfig`, allowing you to enable transcription for either or both audio directions.

!!! note "Source"

    [Gemini Live API - Audio transcriptions](https://ai.google.dev/gemini-api/docs/live-guide#audio-transcriptions)

**Configuration:**

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

# Default behavior: Audio transcription is ENABLED by default
# Both input and output transcription are automatically configured
run_config = RunConfig(
    response_modalities=["AUDIO"]
    # input_audio_transcription defaults to AudioTranscriptionConfig()
    # output_audio_transcription defaults to AudioTranscriptionConfig()
)

# To disable transcription explicitly:
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,   # Explicitly disable user input transcription
    output_audio_transcription=None   # Explicitly disable model output transcription
)

# Enable only input transcription (disable output):
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=types.AudioTranscriptionConfig(),  # Explicitly enable (redundant with default)
    output_audio_transcription=None  # Explicitly disable
)

# Enable only output transcription (disable input):
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,  # Explicitly disable
    output_audio_transcription=types.AudioTranscriptionConfig()  # Explicitly enable (redundant with default)
)
```

**Event Structure**:

Transcriptions are delivered as `types.Transcription` objects on the `Event` object:

```python
from dataclasses import dataclass
from typing import Optional
from google.genai import types

@dataclass
class Event:
    content: Optional[Content]  # Audio/text content
    input_transcription: Optional[types.Transcription]  # User speech → text
    output_transcription: Optional[types.Transcription]  # Model speech → text
    # ... other fields
```

!!! note "Learn More"

    For complete Event structure, see [Part 3: The Event Class](part3.md#the-event-class).

Each `Transcription` object has two attributes:
- **`.text`**: The transcribed text (string)
- **`.finished`**: Boolean indicating if transcription is complete (True) or partial (False)

**How Transcriptions Are Delivered**:

Transcriptions arrive as separate fields in the event stream, not as content parts. Always use defensive null checking when accessing transcription data:

**Processing Transcriptions:**

```python
from google.adk.runners import Runner

# ... runner setup code ...

async for event in runner.run_live(...):
    # User's speech transcription (from input audio)
    if event.input_transcription:  # First check: transcription object exists
        # Access the transcription text and status
        user_text = event.input_transcription.text
        is_finished = event.input_transcription.finished

        # Second check: text is not None or empty
        # This handles cases where transcription is in progress or empty
        if user_text and user_text.strip():
            print(f"User said: {user_text} (finished: {is_finished})")

            # Your caption update logic
            update_caption(user_text, is_user=True, is_final=is_finished)

    # Model's speech transcription (from output audio)
    if event.output_transcription:  # First check: transcription object exists
        model_text = event.output_transcription.text
        is_finished = event.output_transcription.finished

        # Second check: text is not None or empty
        # This handles cases where transcription is in progress or empty
        if model_text and model_text.strip():
            print(f"Model said: {model_text} (finished: {is_finished})")

            # Your caption update logic
            update_caption(model_text, is_user=False, is_final=is_finished)
```

!!! tip "Best Practice for Transcription Null Checking"

    Always use two-level null checking for transcriptions:

    1. Check if the transcription object exists (`if event.input_transcription`)
    2. Check if the text is not empty (`if user_text and user_text.strip()`)

    This pattern prevents errors from `None` values and handles partial transcriptions that may be empty.

### Handling Audio Transcription at the Client

In web applications, transcription events need to be forwarded from the server to the browser and rendered in the UI. The bidi-demo demonstrates a pattern where the server forwards all ADK events (including transcription events) to the WebSocket client, and the client handles displaying transcriptions as speech bubbles with visual indicators for partial vs. finished transcriptions.

**Architecture:**

1. **Server side**: Forward transcription events through WebSocket (already shown in previous section)
2. **Client side**: Process `inputTranscription` and `outputTranscription` events from the WebSocket
3. **UI rendering**: Display partial transcriptions with typing indicators, finalize when `finished: true`

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L532-L655" target="_blank">app.js:530-653</a>'
// Handle input transcription (user's spoken words)
if (adkEvent.inputTranscription && adkEvent.inputTranscription.text) {
    const transcriptionText = adkEvent.inputTranscription.text;
    const isFinished = adkEvent.inputTranscription.finished;

    if (transcriptionText) {
        if (currentInputTranscriptionId == null) {
            // Create new transcription bubble
            currentInputTranscriptionId = Math.random().toString(36).substring(7);
            currentInputTranscriptionElement = createMessageBubble(
                transcriptionText,
                true,  // isUser
                !isFinished  // isPartial
            );
            currentInputTranscriptionElement.id = currentInputTranscriptionId;
            currentInputTranscriptionElement.classList.add("transcription");
            messagesDiv.appendChild(currentInputTranscriptionElement);
        } else {
            // Update existing transcription bubble
            if (currentOutputTranscriptionId == null && currentMessageId == null) {
                // Accumulate input transcription text (Live API sends incremental pieces)
                const existingText = currentInputTranscriptionElement
                    .querySelector(".bubble-text").textContent;
                const cleanText = existingText.replace(/\.\.\.$/, '');
                const accumulatedText = cleanText + transcriptionText;
                updateMessageBubble(
                    currentInputTranscriptionElement,
                    accumulatedText,
                    !isFinished
                );
            }
        }

        // If transcription is finished, reset the state
        if (isFinished) {
            currentInputTranscriptionId = null;
            currentInputTranscriptionElement = null;
        }
    }
}

// Handle output transcription (model's spoken words)
if (adkEvent.outputTranscription && adkEvent.outputTranscription.text) {
    const transcriptionText = adkEvent.outputTranscription.text;
    const isFinished = adkEvent.outputTranscription.finished;

    if (transcriptionText) {
        // Finalize any active input transcription when model starts responding
        if (currentInputTranscriptionId != null && currentOutputTranscriptionId == null) {
            const textElement = currentInputTranscriptionElement
                .querySelector(".bubble-text");
            const typingIndicator = textElement.querySelector(".typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
            currentInputTranscriptionId = null;
            currentInputTranscriptionElement = null;
        }

        if (currentOutputTranscriptionId == null) {
            // Create new transcription bubble for model
            currentOutputTranscriptionId = Math.random().toString(36).substring(7);
            currentOutputTranscriptionElement = createMessageBubble(
                transcriptionText,
                false,  // isUser
                !isFinished  // isPartial
            );
            currentOutputTranscriptionElement.id = currentOutputTranscriptionId;
            currentOutputTranscriptionElement.classList.add("transcription");
            messagesDiv.appendChild(currentOutputTranscriptionElement);
        } else {
            // Update existing transcription bubble
            const existingText = currentOutputTranscriptionElement
                .querySelector(".bubble-text").textContent;
            const cleanText = existingText.replace(/\.\.\.$/, '');
            updateMessageBubble(
                currentOutputTranscriptionElement,
                cleanText + transcriptionText,
                !isFinished
            );
        }

        // If transcription is finished, reset the state
        if (isFinished) {
            currentOutputTranscriptionId = null;
            currentOutputTranscriptionElement = null;
        }
    }
}
```

**Key Implementation Patterns:**

1. **Incremental Text Accumulation**: The Live API may send transcriptions in multiple chunks. Accumulate text by appending new pieces to existing content:
   ```javascript
   const accumulatedText = cleanText + transcriptionText;
   ```

2. **Partial vs Finished States**: Use the `finished` flag to determine whether to show typing indicators:
   - `finished: false` → Show typing indicator (e.g., "...")
   - `finished: true` → Remove typing indicator, finalize bubble

3. **Bubble State Management**: Track current transcription bubbles separately for input and output using IDs. Create new bubbles only when starting fresh transcriptions:
   ```javascript
   if (currentInputTranscriptionId == null) {
       // Create new bubble
   } else {
       // Update existing bubble
   }
   ```

4. **Turn Coordination**: When the model starts responding (first output transcription arrives), finalize any active input transcription to prevent overlapping updates.

This pattern ensures smooth real-time transcription display with proper handling of streaming updates, turn transitions, and visual feedback for users.

### Multi-Agent Transcription Requirements

For multi-agent scenarios (agents with `sub_agents`), ADK automatically enables audio transcription regardless of your `RunConfig` settings. This automatic behavior is required for agent transfer functionality, where text transcriptions are used to pass conversation context between agents.

**Automatic Enablement Behavior:**

When an agent has `sub_agents` defined, ADK's `run_live()` method automatically enables both input and output audio transcription **even if you explicitly set them to `None`**. This ensures that agent transfers work correctly by providing text context to the next agent.

**Why This Matters:**

1. **Cannot be disabled**: You cannot turn off transcription in multi-agent scenarios
2. **Required for functionality**: Agent transfer breaks without text context
3. **Transparent to developers**: Transcription events are automatically available
4. **Plan for data handling**: Your application will receive transcription events that must be processed

**Implementation Details:**

The automatic enablement happens in `Runner.run_live()` when both conditions are met:
- The agent has `sub_agents` defined
- A `LiveRequestQueue` is provided (bidirectional streaming mode)

!!! note "Source"

    [`runners.py:1391-1400`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/runners.py#L1391-L1400)

## Voice Configuration (Speech Config)

The Live API provides voice configuration capabilities that allow you to customize how the model sounds when generating audio responses. ADK supports voice configuration at two levels: **agent-level** (per-agent voice settings) and **session-level** (global voice settings via RunConfig). This enables sophisticated multi-agent scenarios where different agents can speak with different voices, as well as single-agent applications with consistent voice characteristics.

!!! note "Source"

    [Gemini Live API - Capabilities Guide](https://ai.google.dev/gemini-api/docs/live-guide)

### Agent-Level Configuration

You can configure `speech_config` on a per-agent basis by creating a custom `Gemini` LLM instance with voice settings, then passing that instance to the `Agent`. This is particularly useful in multi-agent workflows where different agents represent different personas or roles.

**Configuration:**

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

# Create a Gemini instance with custom speech config
custom_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"
            )
        ),
        language_code="en-US"
    )
)

# Pass the Gemini instance to the agent
agent = Agent(
    model=custom_llm,
    tools=[google_search],
    instruction="You are a helpful assistant."
)
```

### RunConfig-Level Configuration

You can also set `speech_config` in RunConfig to apply a default voice configuration for all agents in the session. This is useful for single-agent applications or when you want a consistent voice across all agents.

**Configuration:**

=== "Python"

    ```python
    from google.genai import types
    from google.adk.agents.run_config import RunConfig

    run_config = RunConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"
                )
            ),
            language_code="en-US"
        )
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.genai.types.PrebuiltVoiceConfig;
    import com.google.genai.types.SpeechConfig;
    import com.google.genai.types.VoiceConfig;

    VoiceConfig voiceConfig =
        VoiceConfig.builder()
            .prebuiltVoiceConfig(PrebuiltVoiceConfig.builder().voiceName("Kore").build())
            .build();
    SpeechConfig speechConfig = SpeechConfig.builder().voiceConfig(voiceConfig).build();
    RunConfig runConfig = RunConfig.builder().setSpeechConfig(speechConfig).build();

    runner.runLive(
        // ...,
        runConfig);
    ```

### Configuration Precedence

When both agent-level (via `Gemini` instance) and session-level (via `RunConfig`) `speech_config` are provided, **agent-level configuration takes precedence**. This allows you to set a default voice in RunConfig while overriding it for specific agents.

**Precedence Rules:**

1. **Gemini instance has `speech_config`**: Use the Gemini's voice configuration (highest priority)
2. **RunConfig has `speech_config`**: Use RunConfig's voice configuration
3. **Neither specified**: Use Live API default voice (lowest priority)

**Example:**

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.agents.run_config import RunConfig
from google.adk.tools import google_search

# Create Gemini instance with custom voice
custom_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"  # Agent-level: highest priority
            )
        )
    )
)

# Agent uses the Gemini instance with custom voice
agent = Agent(
    model=custom_llm,
    tools=[google_search],
    instruction="You are a helpful assistant."
)

# RunConfig with default voice (will be overridden by agent's Gemini config)
run_config = RunConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Kore"  # This is overridden for the agent above
            )
        )
    )
)
```

### Multi-Agent Voice Configuration

For multi-agent workflows, you can assign different voices to different agents by creating separate `Gemini` instances with distinct `speech_config` values. This creates more natural and distinguishable conversations where each agent has its own voice personality.

**Multi-Agent Example:**

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.agents.run_config import RunConfig

# Customer service agent with a friendly voice
customer_service_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Aoede"  # Friendly, warm voice
            )
        )
    )
)

customer_service_agent = Agent(
    name="customer_service",
    model=customer_service_llm,
    instruction="You are a friendly customer service representative."
)

# Technical support agent with a professional voice
technical_support_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Charon"  # Professional, authoritative voice
            )
        )
    )
)

technical_support_agent = Agent(
    name="technical_support",
    model=technical_support_llm,
    instruction="You are a technical support specialist."
)

# Root agent that coordinates the workflow
root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    instruction="Coordinate customer service and technical support.",
    sub_agents=[customer_service_agent, technical_support_agent]
)

# RunConfig without speech_config - each agent uses its own voice
run_config = RunConfig(
    response_modalities=["AUDIO"]
)
```

In this example, when the customer service agent speaks, users hear the "Aoede" voice. When the technical support agent takes over, users hear the "Charon" voice. This creates a more engaging and natural multi-agent experience.

### Configuration Parameters

**`voice_config`**: Specifies which prebuilt voice to use for audio generation
- Configured through nested `VoiceConfig` and `PrebuiltVoiceConfig` objects
- `voice_name`: String identifier for the prebuilt voice (e.g., "Kore", "Puck", "Charon")

**`language_code`**: ISO 639 language code for speech synthesis (e.g., "en-US", "ja-JP")
- Determines the language and regional accent for synthesized speech
- **Native audio models** may ignore `language_code` and automatically determine the language from conversation context. Consult the model-specific documentation for support.

### Supported voices

[Native audio models](models.md#native-audio-models) support these eight prebuilt Live API
voices:

- Puck
- Charon
- Kore
- Fenrir
- Aoede
- Leda
- Orus
- Zephyr

They also support an extended list of additional voices from the Text-to-Speech (TTS)
service, which gives you more options for voice characteristics, accents, and languages:

- See the [Gemini Live API documentation](https://ai.google.dev/gemini-api/docs/live-guide#available-voices)
- Or check the [Text-to-Speech voice list](https://cloud.google.com/text-to-speech/docs/voices), which native audio models also support

To verify which voices are available for your specific model, test voice configurations in
development before deploying to production. If a voice is not supported, the Live API
returns an error.

### Platform Availability

Voice configuration is supported on both platforms, but voice availability may vary:

**Gemini Live API:**

- ✅ Fully supported with documented voice options
- ✅ The eight prebuilt voices plus the extended TTS voice list (see [documentation](https://ai.google.dev/gemini-api/docs/live-guide))

**Gemini Live API (Agent Platform):**

- ✅ Voice configuration supported
- ⚠️ **Platform-specific difference**: Voice availability may differ from Gemini Live API
- ⚠️ **Verification required**: Check [Agent Platform documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api) for the current list of supported voices

**Best practice**: Always test your chosen voice configuration on your target platform during development. If a voice is not supported on your platform/model combination, the Live API will return an error at connection time.

### Important Notes

- **Model compatibility**: Voice configuration is only available for Live API models with audio output capabilities
- **Configuration levels**: You can set `speech_config` at the agent level (via `Gemini(speech_config=...)`) or session level (`RunConfig(speech_config=...)`). Agent-level configuration takes precedence.
- **Agent-level usage**: To configure voice per agent, create a `Gemini` instance with `speech_config` and pass it to `Agent(model=gemini_instance)`
- **Default behavior**: If `speech_config` is not specified at either level, the Live API uses a default voice
- **Native audio models**: Automatically determine language based on conversation context; explicit `language_code` may not be supported
- **Voice availability**: Specific voice names may vary by model; refer to the current Live API documentation for supported voices on your chosen model

!!! note "Learn More"

    For complete RunConfig reference, see [Part 4: Understanding RunConfig](part4.md).

## Voice Activity Detection (VAD)

Voice Activity Detection (VAD) is a Live API feature that automatically detects when users start and stop speaking, enabling natural turn-taking without manual control. VAD is **enabled by default** on all Live API models, allowing the model to automatically manage conversation turns based on detected speech activity.

!!! note "Source"

    [Gemini Live API - Voice Activity Detection](https://ai.google.dev/gemini-api/docs/live-guide#voice-activity-detection-vad)

### How VAD Works

When VAD is enabled (the default), the Live API automatically:

1. **Detects speech start**: Identifies when a user begins speaking
2. **Detects speech end**: Recognizes when a user stops speaking (natural pauses)
3. **Manages turn-taking**: Allows the model to respond when the user finishes speaking
4. **Handles interruptions**: Enables natural conversation flow with back-and-forth exchanges

This creates a hands-free, natural conversation experience where users don't need to manually signal when they're speaking or done speaking.

### When to Disable VAD

You should disable automatic VAD in these scenarios:

- **Push-to-talk implementations**: Your application manually controls when audio should be sent (e.g., audio interaction apps in noisy environments or rooms with cross-talk)
- **Client-side voice detection**: Your application uses client-side VAD that sends activity signals to your server to reduce CPU and network overhead from continuous audio streaming
- **Specific UX patterns**: Your design requires users to manually indicate when they're done speaking

When you disable VAD (which is enabled by default), you must use manual activity signals (`ActivityStart`/`ActivityEnd`) to control conversation turns. See [Part 2: Activity Signals](part2.md#activity-signals) for details on manual turn control.

### VAD Configurations

**Default behavior (VAD enabled, no configuration needed):**

```python
from google.adk.agents.run_config import RunConfig

# VAD is enabled by default - no explicit configuration needed
run_config = RunConfig(
    response_modalities=["AUDIO"]
)
```

**Disable automatic VAD (enables manual turn control):**

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=True  # Disable automatic VAD
        )
    )
)
```

### Client-Side VAD Example

When building voice-enabled applications, you may want to implement client-side Voice Activity Detection (VAD) to reduce CPU and network overhead. This pattern combines browser-based VAD with manual activity signals to control when audio is sent to the server.

**The architecture:**

1. **Client-side**: Browser detects voice activity using Web Audio API (AudioWorklet with RMS-based VAD)
2. **Signal coordination**: Send `activity_start` when voice detected, `activity_end` when voice stops
3. **Audio streaming**: Send audio chunks only during active speech periods
4. **Server configuration**: Disable automatic VAD since client handles detection

#### Server-Side Configuration

**Configuration:**

```python
from fastapi import FastAPI, WebSocket
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.genai import types

# Configure RunConfig to disable automatic VAD
run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=True  # Client handles VAD
        )
    )
)
```

#### WebSocket Upstream Task

**Implementation:**

```python
async def upstream_task(websocket: WebSocket, live_request_queue: LiveRequestQueue):
    """Receives audio and activity signals from client."""
    try:
        while True:
            # Receive JSON message from WebSocket
            message = await websocket.receive_json()

            if message.get("type") == "activity_start":
                # Client detected voice - signal the model
                live_request_queue.send_activity_start()

            elif message.get("type") == "activity_end":
                # Client detected silence - signal the model
                live_request_queue.send_activity_end()

            elif message.get("type") == "audio":
                # Stream audio chunk to the model
                import base64
                audio_data = base64.b64decode(message["data"])
                audio_blob = types.Blob(
                    mime_type="audio/pcm;rate=16000",
                    data=audio_data
                )
                live_request_queue.send_realtime(audio_blob)

    except WebSocketDisconnect:
        live_request_queue.close()
```

#### Client-Side VAD Implementation

**Implementation:**

```javascript
// vad-processor.js - AudioWorklet processor for voice detection
class VADProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.threshold = 0.05;  // Adjust based on environment
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input && input.length > 0) {
            const channelData = input[0];
            let sum = 0;

            // Calculate RMS (Root Mean Square)
            for (let i = 0; i < channelData.length; i++) {
                sum += channelData[i] ** 2;
            }
            const rms = Math.sqrt(sum / channelData.length);

            // Signal voice detection status
            this.port.postMessage({
                voice: rms > this.threshold,
                rms: rms
            });
        }
        return true;
    }
}
registerProcessor('vad-processor', VADProcessor);
```

#### Client-Side Coordination

**Coordinating VAD Signals:**

```javascript
// Main application logic
let isSilence = true;
let lastVoiceTime = 0;
const SILENCE_TIMEOUT = 2000;  // 2 seconds of silence before sending activity_end

// Set up VAD processor
const vadNode = new AudioWorkletNode(audioContext, 'vad-processor');
vadNode.port.onmessage = (event) => {
    const { voice, rms } = event.data;

    if (voice) {
        // Voice detected
        if (isSilence) {
            // Transition from silence to speech - send activity_start
            websocket.send(JSON.stringify({ type: "activity_start" }));
            isSilence = false;
        }
        lastVoiceTime = Date.now();
    } else {
        // No voice detected - check if silence timeout exceeded
        if (!isSilence && Date.now() - lastVoiceTime > SILENCE_TIMEOUT) {
            // Sustained silence - send activity_end
            websocket.send(JSON.stringify({ type: "activity_end" }));
            isSilence = true;
        }
    }
};

// Set up audio recorder to stream chunks
audioRecorderNode.port.onmessage = (event) => {
    const audioData = event.data;  // Float32Array

    // Only send audio when voice is detected
    if (!isSilence) {
        // Convert to PCM16 and send to server
        const pcm16 = convertFloat32ToPCM(audioData);
        const base64Audio = arrayBufferToBase64(pcm16);

        websocket.send(JSON.stringify({
            type: "audio",
            mime_type: "audio/pcm;rate=16000",
            data: base64Audio
        }));
    }
};
```

**Key Implementation Details:**

1. **RMS-Based Voice Detection**: The AudioWorklet processor calculates Root Mean Square (RMS) of audio samples to detect voice activity. RMS provides a simple but effective measure of audio energy that can distinguish speech from silence.

2. **Adjustable Threshold**: The `threshold` value (0.05 in the example) can be tuned based on the environment. Lower thresholds are more sensitive (detect quieter speech but may trigger on background noise), higher thresholds require louder speech.

3. **Silence Timeout**: Use a timeout (e.g., 2000ms) before sending `activity_end` to avoid prematurely ending a turn during natural pauses in speech. This creates a more natural conversation flow.

4. **State Management**: Track `isSilence` state to detect transitions between silence and speech. Send `activity_start` only on silence→speech transitions, and `activity_end` only after sustained silence.

5. **Conditional Audio Streaming**: Only send audio chunks when `!isSilence` to reduce bandwidth. This can save ~50-90% of network traffic depending on the conversation's speech-to-silence ratio.

6. **AudioWorklet Thread Separation**: The VAD processor runs on the audio rendering thread, ensuring real-time performance without being affected by main thread JavaScript execution or network delays.

#### Benefits of Client-Side VAD

This pattern provides several advantages:

- **Reduced CPU and network overhead**: Only send audio during active speech, not continuous silence
- **Faster response**: Immediate local detection without server round-trip
- **Better control**: Fine-tune VAD sensitivity based on client environment

!!! note "Activity Signal Timing"

    When using manual activity signals with client-side VAD:

    - Always send `activity_start` **before** sending the first audio chunk
    - Always send `activity_end` **after** sending the last audio chunk
    - The model will only process audio between `activity_start` and `activity_end` signals
    - Incorrect timing may cause the model to ignore audio or produce unexpected behavior

## Proactivity and Affective Dialog

The Live API offers advanced conversational features that enable more natural and context-aware interactions. **Proactive audio** allows the model to intelligently decide when to respond, offer suggestions without explicit prompts, or ignore irrelevant input. **Affective dialog** enables the model to detect and adapt to emotional cues in voice tone and content, adjusting its response style for more empathetic interactions. These features are currently supported only on native audio models.

!!! note "Source"

    [Gemini Live API - Proactive audio](https://ai.google.dev/gemini-api/docs/live-guide#proactive-audio) | [Affective dialog](https://ai.google.dev/gemini-api/docs/live-guide#affective-dialog)

**Configuration:**

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    # Model can initiate responses without explicit prompts
    proactivity=types.ProactivityConfig(proactive_audio=True),

    # Model adapts to user emotions
    enable_affective_dialog=True
)
```

**Proactivity:**

When enabled, the model can:

- Offer suggestions without being asked
- Provide follow-up information proactively
- Ignore irrelevant or off-topic input
- Anticipate user needs based on context

**Affective Dialog:**

The model analyzes emotional cues in voice tone and content to:

- Detect user emotions (frustrated, happy, confused, etc.)
- Adapt response style and tone accordingly
- Provide empathetic responses in customer service scenarios
- Adjust formality based on detected sentiment

**Practical Example - Customer Service Bot**:

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode

# Configure for empathetic customer service
run_config = RunConfig(
    response_modalities=["AUDIO"],
    streaming_mode=StreamingMode.BIDI,

    # Model can proactively offer help
    proactivity=types.ProactivityConfig(proactive_audio=True),

    # Model adapts to customer emotions
    enable_affective_dialog=True
)

# Example interaction (illustrative - actual model behavior may vary):
# Customer: "I've been waiting for my order for three weeks..."
# [Model may detect frustration in tone and adapt response]
# Model: "I'm really sorry to hear about this delay. Let me check your order
#        status right away. Can you provide your order number?"
#
# [Proactivity in action]
# Model: "I see you previously asked about shipping updates. Would you like
#        me to set up notifications for future orders?"
#
# Note: Proactive and affective behaviors are probabilistic. The model's
# emotional awareness and proactive suggestions will vary based on context,
# conversation history, and inherent model variability.
```

### Platform Compatibility

These features are **model-specific** and have platform implications:

**Gemini Live API:**

- ✅ Supported on `gemini-2.5-flash-native-audio-preview-12-2025`

**Gemini Live API (Agent Platform):**

- ⚠️ **Platform-specific difference**: Proactivity and affective dialog are not currently available on Agent Platform models

**Key insight**: If your application requires proactive audio or affective dialog, use Gemini Live API with one of the [native audio models](models.md#native-audio-models) that support these features.

**Testing Proactivity**:

To verify proactive behavior is working:

1. **Create open-ended context**: Provide information without asking questions
    ```text
    User: "I'm planning a trip to Japan next month."
    Expected: Model offers suggestions, asks follow-up questions
    ```

2. **Test emotional response**:
    ```text
    User: [frustrated tone] "This isn't working at all!"
    Expected: Model acknowledges emotion, adjusts response style
    ```

3. **Monitor for unprompted responses**:
    - Model should occasionally offer relevant information
    - Should ignore truly irrelevant input
    - Should anticipate user needs based on context

**When to Disable**:

Consider disabling proactivity/affective dialog for:
- **Formal/professional contexts** where emotional adaptation is inappropriate
- **High-precision tasks** where predictability is critical
- **Accessibility applications** where consistent behavior is expected
- **Testing/debugging** where deterministic behavior is needed

