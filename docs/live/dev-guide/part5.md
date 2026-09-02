# Part 5: How to Use Audio, Image and Video

This section covers audio, image and video capabilities in ADK's Live API integration, including supported models, audio model architectures, specifications, and best practices for implementing voice and video features.

## How to Use Audio

Live API's audio capabilities enable natural voice conversations with sub-second latency through bidirectional audio streaming. This section covers how to send audio input to the model and receive audio responses, including format requirements, streaming best practices, and client-side implementation patterns.

### Sending Audio Input

**Audio Format Requirements:**

Before calling `send_realtime()`, ensure your audio data is already in the correct format:

- **Format**: 16-bit PCM (signed integer)
- **Sample Rate**: 16,000 Hz (16kHz)
- **Channels**: Mono (single channel)

ADK does not perform audio format conversion. Sending audio in incorrect formats will result in poor quality or errors.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L181-L184" target="_blank">main.py:181-184</a>'
--8<-- "examples/inline/python/live/dev-guide/part5/001-sending-audio-input.py"
```

#### Best Practices for Sending Audio Input

1. **Chunked Streaming**: Send audio in small chunks for low latency. Choose chunk size based on your latency requirements:

    - **Ultra-low latency** (real-time conversation): 10-20ms chunks (~320-640 bytes @ 16kHz)
    - **Balanced** (recommended): 50-100ms chunks (~1600-3200 bytes @ 16kHz)
    - **Lower overhead**: 100-200ms chunks (~3200-6400 bytes @ 16kHz)

    Use consistent chunk sizes throughout the session for optimal performance. Example: 100ms @ 16kHz = 16000 samples/sec × 0.1 sec × 2 bytes/sample = 3200 bytes.

2. **Prompt Forwarding**: ADK's `LiveRequestQueue` forwards each chunk promptly without coalescing or batching. Choose chunk sizes that meet your latency and bandwidth requirements. Don't wait for model responses before sending next chunks.

3. **Continuous Processing**: The model processes audio continuously, not turn-by-turn. With automatic VAD enabled (the default), just stream continuously and let the API detect speech.

4. **Activity Signals**: Use `send_activity_start()` / `send_activity_end()` only when you explicitly disable VAD for manual turn-taking control. VAD is enabled by default, so activity signals are not needed for most applications.

#### Handling Audio Input at the Client

In browser-based applications, capturing microphone audio and sending it to the server requires using the Web Audio API with AudioWorklet processors. The bidi-demo demonstrates how to capture microphone input, convert it to the required 16-bit PCM format at 16kHz, and stream it continuously to the WebSocket server.

**Architecture:**

1. **Audio capture**: Use Web Audio API to access microphone with 16kHz sample rate
2. **Audio processing**: AudioWorklet processor captures audio frames in real-time
3. **Format conversion**: Convert Float32Array samples to 16-bit PCM
4. **WebSocket streaming**: Send PCM chunks to server via WebSocket

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/audio-recorder.js#L7-L58" target="_blank">audio-recorder.js:7-58</a>'
--8<-- "examples/inline/javascript/live/dev-guide/part5/002-handling-audio-input-at-the-client.js"
```

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/pcm-recorder-processor.js#L1-L18" target="_blank">pcm-recorder-processor.js:1-18</a>'
--8<-- "examples/inline/javascript/live/dev-guide/part5/003-handling-audio-input-at-the-client.js"
```

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L979-L988" target="_blank">app.js:977-986</a>'
--8<-- "examples/inline/javascript/live/dev-guide/part5/004-handling-audio-input-at-the-client.js"
```

**Key Implementation Details:**

1. **16kHz Sample Rate**: The AudioContext must be created with `sampleRate: 16000` to match Live API requirements. Modern browsers support this rate.

2. **Mono Audio**: Request single-channel audio (`channelCount: 1`) since Live API expects mono input. This reduces bandwidth and processing overhead.

3. **AudioWorklet Processing**: AudioWorklet runs on a separate thread from the main JavaScript thread, ensuring low-latency, glitch-free audio processing without blocking the UI.

4. **Float32 to PCM16 Conversion**: Web Audio API provides audio as Float32Array values in range [-1.0, 1.0]. Multiply by 32767 (0x7fff) to convert to 16-bit signed integer PCM.

5. **Binary WebSocket Frames**: Send PCM data directly as ArrayBuffer via WebSocket binary frames instead of base64-encoding in JSON. This reduces bandwidth by ~33% and eliminates encoding/decoding overhead.

6. **Continuous Streaming**: The AudioWorklet `process()` method is called automatically at regular intervals (typically 128 samples at a time for 16kHz). This provides consistent chunk sizes for streaming.

This architecture ensures low-latency audio capture and efficient transmission to the server, which then forwards it to the ADK Live API via `LiveRequestQueue.send_realtime()`.

### Receiving Audio Output

When `response_modalities=["AUDIO"]` is configured, the model returns audio data in the event stream as `inline_data` parts.

**Audio Format Requirements:**

The model outputs audio in the following format:

- **Format**: 16-bit PCM (signed integer)
- **Sample Rate**: 24,000 Hz (24kHz) for native audio models
- **Channels**: Mono (single channel)
- **MIME Type**: `audio/pcm;rate=24000`

The audio data arrives as raw PCM bytes, ready for playback or further processing. No additional conversion is required unless you need a different sample rate or format.

**Receiving Audio Output:**

```python
--8<-- "examples/inline/python/live/dev-guide/part5/005-receiving-audio-output.py"
```

!!! note "Automatic Base64 Decoding"

    The Live API wire protocol transmits audio data as base64-encoded strings. The google.genai types system uses Pydantic's base64 serialization feature (`val_json_bytes='base64'`) to automatically decode base64 strings into bytes when deserializing API responses. When you access `part.inline_data.data`, you receive ready-to-use bytes—no manual base64 decoding needed.

#### Handling Audio Events at the Client

The bidi-demo uses a different architectural approach: instead of processing audio on the server, it forwards all events (including audio data) to the WebSocket client and handles audio playback in the browser. This pattern separates concerns—the server focuses on ADK event streaming while the client handles media playback using Web Audio API.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L225-L233" target="_blank">main.py:225-233</a>'
--8<-- "examples/inline/python/live/dev-guide/part5/006-handling-audio-events-at-the-client.py"
```

**Demo Implementation (Client - JavaScript):**

The client-side implementation involves three components: WebSocket message handling, audio player setup with AudioWorklet, and the AudioWorklet processor itself.

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L640-L690" target="_blank">app.js:638-688</a>'
--8<-- "examples/inline/javascript/live/dev-guide/part5/007-the-bidi-demo-forwards-all-events-includ.js"
```

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/audio-player.js#L5-L24" target="_blank">audio-player.js:5-24</a>'
--8<-- "examples/inline/javascript/live/dev-guide/part5/008-the-bidi-demo-forwards-all-events-includ.js"
```

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/pcm-player-processor.js#L5-L76" target="_blank">pcm-player-processor.js:5-76</a>'
--8<-- "examples/inline/javascript/live/dev-guide/part5/009-the-bidi-demo-forwards-all-events-includ.js"
```

**Key Implementation Patterns:**

1. **Base64 Decoding**: The server sends audio data as base64-encoded strings in JSON. The client must decode to ArrayBuffer before passing to AudioWorklet. Handle both standard base64 and base64url encoding.

2. **24kHz Sample Rate**: The AudioContext must be created with `sampleRate: 24000` to match Live API output format (different from 16kHz input).

3. **Ring Buffer Architecture**: Use a circular buffer to handle variable network latency and ensure smooth playback. The buffer stores Float32 samples and handles overflow by overwriting oldest data.

4. **PCM16 to Float32 Conversion**: Live API sends 16-bit signed integers. Divide by 32768 to convert to Float32 in range [-1.0, 1.0] required by Web Audio API.

5. **Mono to Stereo**: The processor duplicates mono audio to both left and right channels for stereo output, ensuring compatibility with all audio devices.

6. **Interruption Handling**: On interruption events, send `endOfAudio` command to clear the buffer by setting `readIndex = writeIndex`, preventing playback of stale audio.

This architecture ensures smooth, low-latency audio playback while handling network jitter and interruptions gracefully.

## How to Use Image and Video

Both images and video in ADK Gemini Live API Toolkit are processed as JPEG frames. Rather than typical video streaming using HLS, mp4, or H.264, ADK uses a straightforward frame-by-frame image processing approach where both static images and video frames are sent as individual JPEG images.

**Image/Video Specifications:**

- **Format**: JPEG (`image/jpeg`)
- **Frame rate**: 1 frame per second (1 FPS) recommended maximum
- **Resolution**: 768x768 pixels (recommended)

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L202-L217" target="_blank">main.py:202-217</a>'
--8<-- "examples/inline/python/live/dev-guide/part5/010-how-to-use-image-and-video.py"
```

**Not Suitable For**:

- **Real-time video action recognition** - 1 FPS is too slow to capture rapid movements or actions
- **Live sports analysis or motion tracking** - Insufficient temporal resolution for fast-moving subjects

**Example Use Case for Image Processing**:

In the [Shopper's Concierge demo](https://youtu.be/LwHPYyw7u6U?si=lG9gl9aSIuu-F4ME&t=40), the application uses `send_realtime()` to send the user-uploaded image. The agent recognizes the context from the image and searches for relevant items on the e-commerce site.

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
<iframe width="560" height="315" src="https://www.youtube.com/embed/LwHPYyw7u6U?si=lG9gl9aSIuu-F4ME&amp;start=40" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>
</div>

### Handling Image Input at the Client

In browser-based applications, capturing images from the user's webcam and sending them to the server requires using the MediaDevices API to access the camera, capturing frames to a canvas, and converting to JPEG format. The bidi-demo demonstrates how to open a camera preview modal, capture a single frame, and send it as base64-encoded JPEG to the WebSocket server.

**Architecture:**

1. **Camera access**: Use `navigator.mediaDevices.getUserMedia()` to access webcam
2. **Video preview**: Display live camera feed in a `<video>` element
3. **Frame capture**: Draw video frame to `<canvas>` and convert to JPEG
4. **Base64 encoding**: Convert canvas to base64 data URL for transmission
5. **WebSocket transmission**: Send as JSON message to server

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L803-L845" target="_blank">app.js:801-843</a>'
--8<-- "examples/inline/javascript/live/dev-guide/part5/011-handling-image-input-at-the-client.js"
```

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L848-L916" target="_blank">app.js:846-914</a>'
--8<-- "examples/inline/javascript/live/dev-guide/part5/012-handling-image-input-at-the-client.js"
```

**Key Implementation Details:**

1. **768x768 Resolution**: Request ideal resolution of 768x768 to match the recommended specification. The browser will provide the closest available resolution.

2. **User-Facing Camera**: The `facingMode: 'user'` constraint selects the front-facing camera on mobile devices, appropriate for self-portrait captures.

3. **Canvas Frame Capture**: Use `canvas.getContext('2d').drawImage()` to capture a single frame from the live video stream. This creates a static snapshot of the current video frame.

4. **JPEG Compression**: The second parameter to `toDataURL()` and `toBlob()` is the quality (0.0 to 1.0). Using 0.85 provides good quality while keeping file size manageable.

5. **Dual Output**: The code creates both a data URL for immediate UI display and a blob for efficient base64 encoding, demonstrating a pattern for responsive user feedback.

6. **Resource Cleanup**: Always call `getTracks().forEach(track => track.stop())` when closing the camera to release the hardware resource and turn off the camera indicator light.

7. **Base64 Encoding**: The FileReader converts the blob to a data URL (`data:image/jpeg;base64,<data>`). Split on comma and take the second part to get just the base64 data without the prefix.

This implementation provides a user-friendly camera interface with preview, single-frame capture, and efficient transmission to the server for processing by the Live API.

### Custom Video Streaming Tools Support

ADK provides special tool support for processing video frames during streaming sessions. Unlike regular tools that execute synchronously, streaming tools can yield video frames asynchronously while the model continues to generate responses.

**Streaming Tool Lifecycle:**

1. **Start**: ADK invokes your async generator function when the model calls it
2. **Stream**: Your function yields results continuously via `AsyncGenerator`
3. **Stop**: ADK cancels the generator task when:
   - The model calls a `stop_streaming()` function you provide
   - The session ends
   - An error occurs

**Important**: You must provide a `stop_streaming(function_name: str)` function as a tool to allow the model to explicitly stop streaming operations.

For implementing custom video streaming tools that process and yield video frames to the model, see the [Streaming Tools documentation](/live/streaming-tools/).

## Understanding Audio Model Architectures

When building voice applications with the Live API, one of the most important decisions is selecting the right audio model architecture. The Live API supports two fundamentally different type of models for audio processing: **Native Audio** and **Half-Cascade**. These model architectures differ in how they process audio input and generate audio output, which directly impacts response naturalness, tool execution reliability, latency characteristics, and overall use case suitability.

Understanding these architectures helps you make informed model selection decisions based on your application's requirements—whether you prioritize natural conversational AI, production reliability, or specific feature availability.

### Native Audio Models

A fully integrated end-to-end audio model architecture where the model processes audio input and generates audio output directly, without intermediate text conversion. This approach enables more human-like speech with natural prosody.

| Audio Model Architecture | Platform | Model | Notes |
|-------------------|----------|-------|-------|
| Native Audio | Gemini Live API | [gemini-2.5-flash-native-audio-preview-12-2025](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash-live) |Publicly available|
| Native Audio | Gemini Live API | [gemini-live-2.5-flash-native-audio](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api) | Public preview |

**Key Characteristics:**

- **End-to-end audio processing**: Processes audio input and generates audio output directly without converting to text intermediately
- **Natural prosody**: Produces more human-like speech patterns, intonation, and emotional expressiveness
- **Extended voice library**: Supports all half-cascade voices plus additional voices from Text-to-Speech (TTS) service
- **Automatic language detection**: Determines language from conversation context without explicit configuration
- **Advanced conversational features**:
  - **[Affective dialog](#proactivity-and-affective-dialog)**: Adapts response style to input expression and tone, detecting emotional cues
  - **[Proactive audio](#proactivity-and-affective-dialog)**: Can proactively decide when to respond, offer suggestions, or ignore irrelevant input
  - **Dynamic thinking**: Supports thought summaries and dynamic thinking budgets
- **AUDIO-only response modality**: Does not support TEXT response modality with `RunConfig`, resulting in slower initial response times

### Half-Cascade Models

A hybrid architecture that combines native audio input processing with text-to-speech (TTS) output generation. Also referred to as "Cascaded" models in some documentation.

Audio input is processed natively, but responses are first generated as text then converted to speech. This separation provides better reliability and more robust tool execution in production environments.

| Audio Model Architecture | Platform | Model | Notes |
|-------------------|----------|-------|-------|
| Half-Cascade | Gemini Live API | [gemini-2.0-flash-live-001](https://ai.google.dev/gemini-api/docs/models#gemini-2.0-flash-live) | Deprecated on December 09, 2025 |
| Half-Cascade | Gemini Live API | [gemini-live-2.5-flash](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash#2.5-flash) | Private GA, not publicly available |

**Key Characteristics:**

- **Hybrid architecture**: Combines native audio input processing with TTS-based audio output generation
- **TEXT response modality support**: Supports TEXT response modality  with `RunConfig` in addition to AUDIO, enabling much faster responses for text-only use cases
- **Explicit language control**: Supports manual language code configuration via `speech_config.language_code`
- **Established TTS quality**: Leverages proven text-to-speech technology for consistent audio output
- **Supported voices**: Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr (8 prebuilt voices)

### How to Handle Model Names

When building ADK applications, you'll need to specify which model to use. The recommended approach is to use environment variables for model configuration, which provides flexibility as model availability and naming change over time.

**Recommended Pattern:**

```python
--8<-- "examples/inline/python/live/dev-guide/part5/013-how-to-handle-model-names.py"
```

**Why use environment variables:**

- **Model availability changes**: Models are released, updated, and deprecated regularly (e.g., `gemini-2.0-flash-live-001` was deprecated on December 09, 2025)
- **Platform-specific names**: Gemini Live API and Gemini Live API on Agent Platform use different model naming conventions for the same functionality
- **Easy switching**: Change models without modifying code by updating the `.env` file
- **Environment-specific configuration**: Use different models for development, staging, and production

**Configuration in `.env` file:**

```bash
# For Gemini Live API (publicly available)
DEMO_AGENT_MODEL=gemini-2.5-flash-native-audio-preview-12-2025

# For Gemini Live API (if using Agent Platform)
# DEMO_AGENT_MODEL=gemini-live-2.5-flash-native-audio
```

!!! note "Environment Variable Loading Order"

    When using `.env` files with `python-dotenv`, you must call `load_dotenv()` **before** importing any modules that read environment variables. Otherwise, `os.getenv()` will return `None` and fall back to the default value, ignoring your `.env` configuration.

    **Correct order in `main.py`:**

    ```python
    --8<-- "examples/inline/python/live/dev-guide/part5/014-demoagentmodel-gemini-live-2-5-flash-nat.py"
    ```

    **Incorrect order (will not work):**

    ```python
    --8<-- "examples/inline/python/live/dev-guide/part5/015-demoagentmodel-gemini-live-2-5-flash-nat.py"
    ```

    This is a Python import behavior: when you import a module, its top-level code executes immediately. If your agent module calls `os.getenv("DEMO_AGENT_MODEL")` at import time, the `.env` file must already be loaded.

**Selecting the right model:**

1. **Choose platform**: Decide between Gemini Live API (public) or Gemini Live API on Agent Platform (enterprise)
2. **Choose architecture**:
   - Native Audio for natural conversational AI with advanced features
   - Half-Cascade for production reliability with tool execution
3. **Check current availability**: Refer to the model tables above and official documentation
4. **Configure environment variable**: Set `DEMO_AGENT_MODEL` in your `.env` file (see [`agent.py:11-16`](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/google_search_agent/agent.py#L11-L16) and [`main.py:99-152`](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L99-L152))

### Live API Models Compatibility and Availability

For the latest information on Live API model compatibility and availability:

- **Gemini Live API models**: See the [Gemini models documentation](https://ai.google.dev/gemini-api/docs/models/gemini)
- **Gemini Live API models (Agent Platform)**: See the [Agent Platform model documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

Always verify model availability and feature support in the official documentation before deploying to production.

## Audio Transcription

The Live API provides built-in audio transcription capabilities that automatically convert speech to text for both user input and model output. This eliminates the need for external transcription services and enables real-time captions, conversation logging, and accessibility features. ADK exposes these capabilities through `RunConfig`, allowing you to enable transcription for either or both audio directions.

!!! note "Source"

    [Gemini Live API - Audio transcriptions](https://ai.google.dev/gemini-api/docs/live-guide#audio-transcriptions)

**Configuration:**

```python
--8<-- "examples/inline/python/live/dev-guide/part5/016-audio-transcription.py"
```

**Event Structure**:

Transcriptions are delivered as `types.Transcription` objects on the `Event` object:

```python
--8<-- "examples/inline/python/live/dev-guide/part5/017-enable-only-output-transcription-disable.py"
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
--8<-- "examples/inline/python/live/dev-guide/part5/018-enable-only-output-transcription-disable.py"
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
--8<-- "examples/inline/javascript/live/dev-guide/part5/019-handling-audio-transcription-at-the-clie.js"
```

**Key Implementation Patterns:**

1. **Incremental Text Accumulation**: The Live API may send transcriptions in multiple chunks. Accumulate text by appending new pieces to existing content:
   ```javascript
   --8<-- "examples/inline/javascript/live/dev-guide/part5/020-handling-audio-transcription-at-the-clie.js"
   ```

2. **Partial vs Finished States**: Use the `finished` flag to determine whether to show typing indicators:
   - `finished: false` → Show typing indicator (e.g., "...")
   - `finished: true` → Remove typing indicator, finalize bubble

3. **Bubble State Management**: Track current transcription bubbles separately for input and output using IDs. Create new bubbles only when starting fresh transcriptions:
   ```javascript
   --8<-- "examples/inline/javascript/live/dev-guide/part5/021-handling-audio-transcription-at-the-clie.js"
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
--8<-- "examples/inline/python/live/dev-guide/part5/022-agent-level-configuration.py"
```

### RunConfig-Level Configuration

You can also set `speech_config` in RunConfig to apply a default voice configuration for all agents in the session. This is useful for single-agent applications or when you want a consistent voice across all agents.

**Configuration:**

```python
--8<-- "examples/inline/python/live/dev-guide/part5/023-runconfig-level-configuration.py"
```

### Configuration Precedence

When both agent-level (via `Gemini` instance) and session-level (via `RunConfig`) `speech_config` are provided, **agent-level configuration takes precedence**. This allows you to set a default voice in RunConfig while overriding it for specific agents.

**Precedence Rules:**

1. **Gemini instance has `speech_config`**: Use the Gemini's voice configuration (highest priority)
2. **RunConfig has `speech_config`**: Use RunConfig's voice configuration
3. **Neither specified**: Use Live API default voice (lowest priority)

**Example:**

```python
--8<-- "examples/inline/python/live/dev-guide/part5/024-configuration-precedence.py"
```

### Multi-Agent Voice Configuration

For multi-agent workflows, you can assign different voices to different agents by creating separate `Gemini` instances with distinct `speech_config` values. This creates more natural and distinguishable conversations where each agent has its own voice personality.

**Multi-Agent Example:**

```python
--8<-- "examples/inline/python/live/dev-guide/part5/025-multi-agent-voice-configuration.py"
```

In this example, when the customer service agent speaks, users hear the "Aoede" voice. When the technical support agent takes over, users hear the "Charon" voice. This creates a more engaging and natural multi-agent experience.

### Configuration Parameters

**`voice_config`**: Specifies which prebuilt voice to use for audio generation
- Configured through nested `VoiceConfig` and `PrebuiltVoiceConfig` objects
- `voice_name`: String identifier for the prebuilt voice (e.g., "Kore", "Puck", "Charon")

**`language_code`**: ISO 639 language code for speech synthesis (e.g., "en-US", "ja-JP")
- Determines the language and regional accent for synthesized speech
- **Model-specific behavior:**
  - **Half-Cascade models**: Use the specified `language_code` for TTS output
  - **Native audio models**: May ignore `language_code` and automatically determine language from conversation context. Consult model-specific documentation for support.

### Available Voices

The available voices vary by model architecture. To verify which voices are available for your specific model:
- Check the [Gemini Live API documentation](https://ai.google.dev/gemini-api/docs/live-guide) for the complete list
- Test voice configurations in development before deploying to production
- If a voice is not supported, the Live API will return an error

**Half-cascade models** support these voices:
- Puck
- Charon
- Kore
- Fenrir
- Aoede
- Leda
- Orus
- Zephyr

**Native audio models** support an extended voice list that includes all half-cascade voices plus additional voices from the Text-to-Speech (TTS) service. For the complete list of voices supported by native audio models:
- See the [Gemini Live API documentation](https://ai.google.dev/gemini-api/docs/live-guide#available-voices)
- Or check the [Text-to-Speech voice list](https://cloud.google.com/text-to-speech/docs/voices) which native audio models also support

The extended voice list provides more options for voice characteristics, accents, and languages compared to half-cascade models.

### Platform Availability

Voice configuration is supported on both platforms, but voice availability may vary:

**Gemini Live API:**

- ✅ Fully supported with documented voice options
- ✅ Half-cascade models: 8 voices (Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr)
- ✅ Native audio models: Extended voice list (see [documentation](https://ai.google.dev/gemini-api/docs/live-guide))

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
--8<-- "examples/inline/python/live/dev-guide/part5/026-vad-configurations.py"
```

**Disable automatic VAD (enables manual turn control):**

```python
--8<-- "examples/inline/python/live/dev-guide/part5/027-vad-is-enabled-by-default-no-explicit-co.py"
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
--8<-- "examples/inline/python/live/dev-guide/part5/028-server-side-configuration.py"
```

#### WebSocket Upstream Task

**Implementation:**

```python
--8<-- "examples/inline/python/live/dev-guide/part5/029-websocket-upstream-task.py"
```

#### Client-Side VAD Implementation

**Implementation:**

```javascript
--8<-- "examples/inline/javascript/live/dev-guide/part5/030-client-side-vad-implementation.js"
```

#### Client-Side Coordination

**Coordinating VAD Signals:**

```javascript
--8<-- "examples/inline/javascript/live/dev-guide/part5/031-client-side-coordination.js"
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
--8<-- "examples/inline/python/live/dev-guide/part5/032-proactivity-and-affective-dialog.py"
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
--8<-- "examples/inline/python/live/dev-guide/part5/033-proactivity-and-affective-dialog.py"
```

### Platform Compatibility

These features are **model-specific** and have platform implications:

**Gemini Live API:**

- ✅ Supported on `gemini-2.5-flash-native-audio-preview-12-2025` (native audio model)
- ❌ Not supported on `gemini-live-2.5-flash-preview` (half-cascade model)

**Gemini Live API (Agent Platform):**

- ❌ Not currently supported on `gemini-live-2.5-flash` (half-cascade model)
- ⚠️ **Platform-specific difference**: Proactivity and affective dialog require native audio models, which are currently only available on Gemini Live API

**Key insight**: If your application requires proactive audio or affective dialog features, you must use Gemini Live API with a native audio model. Half-cascade models on either platform do not support these features.

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

## Summary

In this part, you learned how to implement multimodal features in ADK Gemini Live API Toolkit applications, focusing on audio, image, and video capabilities. We covered audio specifications and format requirements, explored the differences between native audio and half-cascade architectures, examined how to send and receive audio streams through LiveRequestQueue and Events, and learned about advanced features like audio transcription, voice activity detection, and proactive/affective dialog. You now understand how to build natural voice-enabled AI experiences with proper audio handling, implement video streaming for visual context, and configure model-specific features based on platform capabilities. With this comprehensive understanding of ADK's multimodal streaming features, you're equipped to build production-ready applications that handle text, audio, image, and video seamlessly—creating rich, interactive AI experiences across diverse use cases.

**Congratulations!** You've completed the ADK Gemini Live API Toolkit Developer Guide. You now have a comprehensive understanding of how to build production-ready real-time streaming AI applications with Google's Agent Development Kit.

← [Previous: Part 4: Understanding RunConfig](part4.md)
