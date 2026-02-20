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

Demo implementation: [main.py:181-184](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L181-L184)

```python
audio_blob = types.Blob(
    mime_type="audio/pcm;rate=16000",
    data=audio_data
)
live_request_queue.send_realtime(audio_blob)
```

#### Best Practices for Sending Audio Input

1. **Chunked Streaming**: Send audio in small chunks for low latency. Choose chunk size based on your latency requirements:

   - **Ultra-low latency** (real-time conversation): 10-20ms chunks (~320-640 bytes @ 16kHz)
   - **Balanced** (recommended): 50-100ms chunks (~1600-3200 bytes @ 16kHz)
   - **Lower overhead**: 100-200ms chunks (~3200-6400 bytes @ 16kHz)

   Use consistent chunk sizes throughout the session for optimal performance. Example: 100ms @ 16kHz = 16000 samples/sec × 0.1 sec × 2 bytes/sample = 3200 bytes.

1. **Prompt Forwarding**: ADK's `LiveRequestQueue` forwards each chunk promptly without coalescing or batching. Choose chunk sizes that meet your latency and bandwidth requirements. Don't wait for model responses before sending next chunks.

1. **Continuous Processing**: The model processes audio continuously, not turn-by-turn. With automatic VAD enabled (the default), just stream continuously and let the API detect speech.

1. **Activity Signals**: Use `send_activity_start()` / `send_activity_end()` only when you explicitly disable VAD for manual turn-taking control. VAD is enabled by default, so activity signals are not needed for most applications.

#### Handling Audio Input at the Client

In browser-based applications, capturing microphone audio and sending it to the server requires using the Web Audio API with AudioWorklet processors. The bidi-demo demonstrates how to capture microphone input, convert it to the required 16-bit PCM format at 16kHz, and stream it continuously to the WebSocket server.

**Architecture:**

1. **Audio capture**: Use Web Audio API to access microphone with 16kHz sample rate
1. **Audio processing**: AudioWorklet processor captures audio frames in real-time
1. **Format conversion**: Convert Float32Array samples to 16-bit PCM
1. **WebSocket streaming**: Send PCM chunks to server via WebSocket

Demo implementation: [audio-recorder.js:7-58](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/audio-recorder.js#L7-L58)

```javascript
// Start audio recorder worklet
export async function startAudioRecorderWorklet(audioRecorderHandler) {
    // Create an AudioContext with 16kHz sample rate
    // This matches the Live API's required input format (16-bit PCM @ 16kHz)
    const audioRecorderContext = new AudioContext({ sampleRate: 16000 });

    // Load the AudioWorklet module that will process audio in real-time
    // AudioWorklet runs on a separate thread for low-latency, glitch-free audio processing
    const workletURL = new URL("./pcm-recorder-processor.js", import.meta.url);
    await audioRecorderContext.audioWorklet.addModule(workletURL);

    // Request access to the user's microphone
    // channelCount: 1 requests mono audio (single channel) as required by Live API
    micStream = await navigator.mediaDevices.getUserMedia({
        audio: { channelCount: 1 }
    });
    const source = audioRecorderContext.createMediaStreamSource(micStream);

    // Create an AudioWorkletNode that uses our custom PCM recorder processor
    // This node will capture audio frames and send them to our handler
    const audioRecorderNode = new AudioWorkletNode(
        audioRecorderContext,
        "pcm-recorder-processor"
    );

    // Connect the microphone source to the worklet processor
    // The processor will receive audio frames and post them via port.postMessage
    source.connect(audioRecorderNode);
    audioRecorderNode.port.onmessage = (event) => {
        // Convert Float32Array to 16-bit PCM format required by Live API
        const pcmData = convertFloat32ToPCM(event.data);

        // Send the PCM data to the handler (which will forward to WebSocket)
        audioRecorderHandler(pcmData);
    };
    return [audioRecorderNode, audioRecorderContext, micStream];
}

// Convert Float32 samples to 16-bit PCM
function convertFloat32ToPCM(inputData) {
    // Create an Int16Array of the same length
    const pcm16 = new Int16Array(inputData.length);
    for (let i = 0; i < inputData.length; i++) {
        // Web Audio API provides Float32 samples in range [-1.0, 1.0]
        // Multiply by 0x7fff (32767) to convert to 16-bit signed integer range [-32768, 32767]
        pcm16[i] = inputData[i] * 0x7fff;
    }
    // Return the underlying ArrayBuffer (binary data) for efficient transmission
    return pcm16.buffer;
}
```

Demo implementation: [pcm-recorder-processor.js:1-18](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/pcm-recorder-processor.js#L1-L18)

```javascript
// pcm-recorder-processor.js - AudioWorklet processor for capturing audio
class PCMProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
    }

    process(inputs, outputs, parameters) {
        if (inputs.length > 0 && inputs[0].length > 0) {
            // Use the first channel (mono)
            const inputChannel = inputs[0][0];
            // Copy the buffer to avoid issues with recycled memory
            const inputCopy = new Float32Array(inputChannel);
            this.port.postMessage(inputCopy);
        }
        return true;
    }
}

registerProcessor("pcm-recorder-processor", PCMProcessor);
```

Demo implementation: [app.js:977-986](https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L979-L988)

```javascript
// Audio recorder handler - called for each audio chunk
function audioRecorderHandler(pcmData) {
    if (websocket && websocket.readyState === WebSocket.OPEN && is_audio) {
        // Send audio as binary WebSocket frame (more efficient than base64 JSON)
        websocket.send(pcmData);
        console.log("[CLIENT TO AGENT] Sent audio chunk: %s bytes", pcmData.byteLength);
    }
}
```

**Key Implementation Details:**

1. **16kHz Sample Rate**: The AudioContext must be created with `sampleRate: 16000` to match Live API requirements. Modern browsers support this rate.
1. **Mono Audio**: Request single-channel audio (`channelCount: 1`) since Live API expects mono input. This reduces bandwidth and processing overhead.
1. **AudioWorklet Processing**: AudioWorklet runs on a separate thread from the main JavaScript thread, ensuring low-latency, glitch-free audio processing without blocking the UI.
1. **Float32 to PCM16 Conversion**: Web Audio API provides audio as Float32Array values in range [-1.0, 1.0]. Multiply by 32767 (0x7fff) to convert to 16-bit signed integer PCM.
1. **Binary WebSocket Frames**: Send PCM data directly as ArrayBuffer via WebSocket binary frames instead of base64-encoding in JSON. This reduces bandwidth by ~33% and eliminates encoding/decoding overhead.
1. **Continuous Streaming**: The AudioWorklet `process()` method is called automatically at regular intervals (typically 128 samples at a time for 16kHz). This provides consistent chunk sizes for streaming.

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
from google.adk.agents.run_config import RunConfig, StreamingMode

# Configure for audio output
run_config = RunConfig(
    response_modalities=["AUDIO"],  # Required for audio responses
    streaming_mode=StreamingMode.BIDI
)

# Process audio output from the model
async for event in runner.run_live(
    user_id="user_123",
    session_id="session_456",
    live_request_queue=live_request_queue,
    run_config=run_config
):
    # Events may contain multiple parts (text, audio, etc.)
    if event.content and event.content.parts:
        for part in event.content.parts:
            # Audio data arrives as inline_data with audio/pcm MIME type
            if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                # The data is already decoded to raw bytes (24kHz, 16-bit PCM, mono)
                audio_bytes = part.inline_data.data

                # Your logic to stream audio to client
                await stream_audio_to_client(audio_bytes)

                # Or save to file
                # with open("output.pcm", "ab") as f:
                #     f.write(audio_bytes)
```

Automatic Base64 Decoding

The Live API wire protocol transmits audio data as base64-encoded strings. The google.genai types system uses Pydantic's base64 serialization feature (`val_json_bytes='base64'`) to automatically decode base64 strings into bytes when deserializing API responses. When you access `part.inline_data.data`, you receive ready-to-use bytes—no manual base64 decoding needed.

#### Handling Audio Events at the Client

The bidi-demo uses a different architectural approach: instead of processing audio on the server, it forwards all events (including audio data) to the WebSocket client and handles audio playback in the browser. This pattern separates concerns—the server focuses on ADK event streaming while the client handles media playback using Web Audio API.

Demo implementation: [main.py:225-233](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L225-L233)

```python
# The bidi-demo forwards all events (including audio) to the WebSocket client
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config
):
    event_json = event.model_dump_json(exclude_none=True, by_alias=True)
    await websocket.send_text(event_json)
```

**Demo Implementation (Client - JavaScript):**

The client-side implementation involves three components: WebSocket message handling, audio player setup with AudioWorklet, and the AudioWorklet processor itself.

Demo implementation: [app.js:638-688](https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L640-L690)

```javascript
// 1. WebSocket Message Handler
// Handle content events (text or audio)
if (adkEvent.content && adkEvent.content.parts) {
    const parts = adkEvent.content.parts;

    for (const part of parts) {
        // Handle inline data (audio)
        if (part.inlineData) {
            const mimeType = part.inlineData.mimeType;
            const data = part.inlineData.data;

            // Check if this is audio PCM data and the audio player is ready
            if (mimeType && mimeType.startsWith("audio/pcm") && audioPlayerNode) {
                // Decode base64 to ArrayBuffer and send to AudioWorklet for playback
                audioPlayerNode.port.postMessage(base64ToArray(data));
            }
        }
    }
}

// Decode base64 audio data to ArrayBuffer
function base64ToArray(base64) {
    // Convert base64url to standard base64 (RFC 4648 compliance)
    // base64url uses '-' and '_' instead of '+' and '/', which are URL-safe
    let standardBase64 = base64.replace(/-/g, '+').replace(/_/g, '/');

    // Add padding '=' characters if needed
    // Base64 strings must be multiples of 4 characters
    while (standardBase64.length % 4) {
        standardBase64 += '=';
    }

    // Decode base64 string to binary string using browser API
    const binaryString = window.atob(standardBase64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    // Convert each character code (0-255) to a byte
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    // Return the underlying ArrayBuffer (binary data)
    return bytes.buffer;
}
```

Demo implementation: [audio-player.js:5-24](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/audio-player.js#L5-L24)

```javascript
// 2. Audio Player Setup
// Start audio player worklet
export async function startAudioPlayerWorklet() {
    // Create an AudioContext with 24kHz sample rate
    // This matches the Live API's output audio format (16-bit PCM @ 24kHz)
    // Note: Different from input rate (16kHz) - Live API outputs at higher quality
    const audioContext = new AudioContext({
        sampleRate: 24000
    });

    // Load the AudioWorklet module that will handle audio playback
    // AudioWorklet runs on audio rendering thread for smooth, low-latency playback
    const workletURL = new URL('./pcm-player-processor.js', import.meta.url);
    await audioContext.audioWorklet.addModule(workletURL);

    // Create an AudioWorkletNode using our custom PCM player processor
    // This node will receive audio data via postMessage and play it through speakers
    const audioPlayerNode = new AudioWorkletNode(audioContext, 'pcm-player-processor');

    // Connect the player node to the audio destination (speakers/headphones)
    // This establishes the audio graph: AudioWorklet → AudioContext.destination
    audioPlayerNode.connect(audioContext.destination);

    return [audioPlayerNode, audioContext];
}
```

Demo implementation: [pcm-player-processor.js:5-76](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/pcm-player-processor.js#L5-L76)

```javascript
// 3. AudioWorklet Processor (Ring Buffer)
// AudioWorklet processor that buffers and plays PCM audio
class PCMPlayerProcessor extends AudioWorkletProcessor {
    constructor() {
        super();

        // Initialize ring buffer (24kHz x 180 seconds = ~4.3 million samples)
        // Ring buffer absorbs network jitter and ensures smooth playback
        this.bufferSize = 24000 * 180;
        this.buffer = new Float32Array(this.bufferSize);
        this.writeIndex = 0;  // Where we write new audio data
        this.readIndex = 0;   // Where we read for playback

        // Handle incoming messages from main thread
        this.port.onmessage = (event) => {
            // Reset buffer on interruption (e.g., user interrupts model response)
            if (event.data.command === 'endOfAudio') {
                this.readIndex = this.writeIndex; // Clear the buffer by jumping read to write position
                return;
            }

            // Decode Int16 array from incoming ArrayBuffer
            // The Live API sends 16-bit PCM audio data
            const int16Samples = new Int16Array(event.data);

            // Add audio data to ring buffer for playback
            this._enqueue(int16Samples);
        };
    }

    // Push incoming Int16 data into ring buffer
    _enqueue(int16Samples) {
        for (let i = 0; i < int16Samples.length; i++) {
            // Convert 16-bit integer to float in [-1.0, 1.0] required by Web Audio API
            // Divide by 32768 (max positive value for signed 16-bit int)
            const floatVal = int16Samples[i] / 32768;

            // Store in ring buffer at current write position
            this.buffer[this.writeIndex] = floatVal;
            // Move write index forward, wrapping around at buffer end (circular buffer)
            this.writeIndex = (this.writeIndex + 1) % this.bufferSize;

            // Overflow handling: if write catches up to read, move read forward
            // This overwrites oldest unplayed samples (rare, only under extreme network delay)
            if (this.writeIndex === this.readIndex) {
                this.readIndex = (this.readIndex + 1) % this.bufferSize;
            }
        }
    }

    // Called by Web Audio system automatically ~128 samples at a time
    // This runs on the audio rendering thread for precise timing
    process(inputs, outputs, parameters) {
        const output = outputs[0];
        const framesPerBlock = output[0].length;

        for (let frame = 0; frame < framesPerBlock; frame++) {
            // Write samples to output buffer (mono to stereo)
            output[0][frame] = this.buffer[this.readIndex]; // left channel
            if (output.length > 1) {
                output[1][frame] = this.buffer[this.readIndex]; // right channel (duplicate for stereo)
            }

            // Move read index forward unless buffer is empty (underflow protection)
            if (this.readIndex != this.writeIndex) {
                this.readIndex = (this.readIndex + 1) % this.bufferSize;
            }
            // If readIndex == writeIndex, we're out of data - output silence (0.0)
        }

        return true; // Keep processor alive (return false to terminate)
    }
}

registerProcessor('pcm-player-processor', PCMPlayerProcessor);
```

**Key Implementation Patterns:**

1. **Base64 Decoding**: The server sends audio data as base64-encoded strings in JSON. The client must decode to ArrayBuffer before passing to AudioWorklet. Handle both standard base64 and base64url encoding.
1. **24kHz Sample Rate**: The AudioContext must be created with `sampleRate: 24000` to match Live API output format (different from 16kHz input).
1. **Ring Buffer Architecture**: Use a circular buffer to handle variable network latency and ensure smooth playback. The buffer stores Float32 samples and handles overflow by overwriting oldest data.
1. **PCM16 to Float32 Conversion**: Live API sends 16-bit signed integers. Divide by 32768 to convert to Float32 in range [-1.0, 1.0] required by Web Audio API.
1. **Mono to Stereo**: The processor duplicates mono audio to both left and right channels for stereo output, ensuring compatibility with all audio devices.
1. **Interruption Handling**: On interruption events, send `endOfAudio` command to clear the buffer by setting `readIndex = writeIndex`, preventing playback of stale audio.

This architecture ensures smooth, low-latency audio playback while handling network jitter and interruptions gracefully.

## How to Use Image and Video

Both images and video in ADK Bidi-streaming are processed as JPEG frames. Rather than typical video streaming using HLS, mp4, or H.264, ADK uses a straightforward frame-by-frame image processing approach where both static images and video frames are sent as individual JPEG images.

**Image/Video Specifications:**

- **Format**: JPEG (`image/jpeg`)
- **Frame rate**: 1 frame per second (1 FPS) recommended maximum
- **Resolution**: 768x768 pixels (recommended)

Demo implementation: [main.py:202-217](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L202-L217)

```python
# Decode base64 image data
image_data = base64.b64decode(json_message["data"])
mime_type = json_message.get("mimeType", "image/jpeg")

# Send image as blob
image_blob = types.Blob(
    mime_type=mime_type,
    data=image_data
)
live_request_queue.send_realtime(image_blob)
```

**Not Suitable For**:

- **Real-time video action recognition** - 1 FPS is too slow to capture rapid movements or actions
- **Live sports analysis or motion tracking** - Insufficient temporal resolution for fast-moving subjects

**Example Use Case for Image Processing**:

In the [Shopper's Concierge demo](https://youtu.be/LwHPYyw7u6U?si=lG9gl9aSIuu-F4ME&t=40), the application uses `send_realtime()` to send the user-uploaded image. The agent recognizes the context from the image and searches for relevant items on the e-commerce site.

### Handling Image Input at the Client

In browser-based applications, capturing images from the user's webcam and sending them to the server requires using the MediaDevices API to access the camera, capturing frames to a canvas, and converting to JPEG format. The bidi-demo demonstrates how to open a camera preview modal, capture a single frame, and send it as base64-encoded JPEG to the WebSocket server.

**Architecture:**

1. **Camera access**: Use `navigator.mediaDevices.getUserMedia()` to access webcam
1. **Video preview**: Display live camera feed in a `<video>` element
1. **Frame capture**: Draw video frame to `<canvas>` and convert to JPEG
1. **Base64 encoding**: Convert canvas to base64 data URL for transmission
1. **WebSocket transmission**: Send as JSON message to server

Demo implementation: [app.js:801-843](https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L803-L845)

```javascript
// 1. Opening Camera Preview
// Open camera modal and start preview
async function openCameraPreview() {
    try {
        // Request access to the user's webcam with 768x768 resolution
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 768 },
                height: { ideal: 768 },
                facingMode: 'user'
            }
        });

        // Set the stream to the video element
        cameraPreview.srcObject = cameraStream;

        // Show the modal
        cameraModal.classList.add('show');

    } catch (error) {
        console.error('Error accessing camera:', error);
        addSystemMessage(`Failed to access camera: ${error.message}`);
    }
}

// Close camera modal and stop preview
function closeCameraPreview() {
    // Stop the camera stream
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }

    // Clear the video source
    cameraPreview.srcObject = null;

    // Hide the modal
    cameraModal.classList.remove('show');
}
```

Demo implementation: [app.js:846-914](https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L848-L916)

```javascript
// 2. Capturing and Sending Image
// Capture image from the live preview
function captureImageFromPreview() {
    if (!cameraStream) {
        addSystemMessage('No camera stream available');
        return;
    }

    try {
        // Create canvas to capture the frame
        const canvas = document.createElement('canvas');
        canvas.width = cameraPreview.videoWidth;
        canvas.height = cameraPreview.videoHeight;
        const context = canvas.getContext('2d');

        // Draw current video frame to canvas
        context.drawImage(cameraPreview, 0, 0, canvas.width, canvas.height);

        // Convert canvas to data URL for display
        const imageDataUrl = canvas.toDataURL('image/jpeg', 0.85);

        // Display the captured image in the chat
        const imageBubble = createImageBubble(imageDataUrl, true);
        messagesDiv.appendChild(imageBubble);

        // Convert canvas to blob for sending to server
        canvas.toBlob((blob) => {
            // Convert blob to base64 for sending to server
            const reader = new FileReader();
            reader.onloadend = () => {
                // Remove data:image/jpeg;base64, prefix
                const base64data = reader.result.split(',')[1];
                sendImage(base64data);
            };
            reader.readAsDataURL(blob);
        }, 'image/jpeg', 0.85);

        // Close the camera modal
        closeCameraPreview();

    } catch (error) {
        console.error('Error capturing image:', error);
        addSystemMessage(`Failed to capture image: ${error.message}`);
    }
}

// Send image to server
function sendImage(base64Image) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        const jsonMessage = JSON.stringify({
            type: "image",
            data: base64Image,
            mimeType: "image/jpeg"
        });
        websocket.send(jsonMessage);
        console.log("[CLIENT TO AGENT] Sent image");
    }
}
```

**Key Implementation Details:**

1. **768x768 Resolution**: Request ideal resolution of 768x768 to match the recommended specification. The browser will provide the closest available resolution.
1. **User-Facing Camera**: The `facingMode: 'user'` constraint selects the front-facing camera on mobile devices, appropriate for self-portrait captures.
1. **Canvas Frame Capture**: Use `canvas.getContext('2d').drawImage()` to capture a single frame from the live video stream. This creates a static snapshot of the current video frame.
1. **JPEG Compression**: The second parameter to `toDataURL()` and `toBlob()` is the quality (0.0 to 1.0). Using 0.85 provides good quality while keeping file size manageable.
1. **Dual Output**: The code creates both a data URL for immediate UI display and a blob for efficient base64 encoding, demonstrating a pattern for responsive user feedback.
1. **Resource Cleanup**: Always call `getTracks().forEach(track => track.stop())` when closing the camera to release the hardware resource and turn off the camera indicator light.
1. **Base64 Encoding**: The FileReader converts the blob to a data URL (`data:image/jpeg;base64,<data>`). Split on comma and take the second part to get just the base64 data without the prefix.

This implementation provides a user-friendly camera interface with preview, single-frame capture, and efficient transmission to the server for processing by the Live API.

### Custom Video Streaming Tools Support

ADK provides special tool support for processing video frames during streaming sessions. Unlike regular tools that execute synchronously, streaming tools can yield video frames asynchronously while the model continues to generate responses.

**Streaming Tool Lifecycle:**

1. **Start**: ADK invokes your async generator function when the model calls it
1. **Stream**: Your function yields results continuously via `AsyncGenerator`
1. **Stop**: ADK cancels the generator task when:
1. The model calls a `stop_streaming()` function you provide
1. The session ends
1. An error occurs

**Important**: You must provide a `stop_streaming(function_name: str)` function as a tool to allow the model to explicitly stop streaming operations.

For implementing custom video streaming tools that process and yield video frames to the model, see the [Streaming Tools documentation](https://google.github.io/adk-docs/streaming/streaming-tools/).

## Understanding Audio Model Architectures

When building voice applications with the Live API, one of the most important decisions is selecting the right audio model architecture. The Live API supports two fundamentally different type of models for audio processing: **Native Audio** and **Half-Cascade**. These model architectures differ in how they process audio input and generate audio output, which directly impacts response naturalness, tool execution reliability, latency characteristics, and overall use case suitability.

Understanding these architectures helps you make informed model selection decisions based on your application's requirements—whether you prioritize natural conversational AI, production reliability, or specific feature availability.

### Native Audio Models

A fully integrated end-to-end audio model architecture where the model processes audio input and generates audio output directly, without intermediate text conversion. This approach enables more human-like speech with natural prosody.

| Audio Model Architecture | Platform           | Model                                                                                                                        | Notes              |
| ------------------------ | ------------------ | ---------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| Native Audio             | Gemini Live API    | [gemini-2.5-flash-native-audio-preview-12-2025](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash-live)          | Publicly available |
| Native Audio             | Vertex AI Live API | [gemini-live-2.5-flash-native-audio](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api) | Public preview     |

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

| Audio Model Architecture | Platform           | Model                                                                                                            | Notes                              |
| ------------------------ | ------------------ | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Half-Cascade             | Gemini Live API    | [gemini-2.0-flash-live-001](https://ai.google.dev/gemini-api/docs/models#gemini-2.0-flash-live)                  | Deprecated on December 09, 2025    |
| Half-Cascade             | Vertex AI Live API | [gemini-live-2.5-flash](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash#2.5-flash) | Private GA, not publicly available |

**Key Characteristics:**

- **Hybrid architecture**: Combines native audio input processing with TTS-based audio output generation
- **TEXT response modality support**: Supports TEXT response modality with `RunConfig` in addition to AUDIO, enabling much faster responses for text-only use cases
- **Explicit language control**: Supports manual language code configuration via `speech_config.language_code`
- **Established TTS quality**: Leverages proven text-to-speech technology for consistent audio output
- **Supported voices**: Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr (8 prebuilt voices)

### How to Handle Model Names

When building ADK applications, you'll need to specify which model to use. The recommended approach is to use environment variables for model configuration, which provides flexibility as model availability and naming change over time.

**Recommended Pattern:**

```python
import os
from google.adk.agents import Agent

# Use environment variable with fallback to a sensible default
agent = Agent(
    name="my_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[...],
    instruction="..."
)
```

**Why use environment variables:**

- **Model availability changes**: Models are released, updated, and deprecated regularly (e.g., `gemini-2.0-flash-live-001` was deprecated on December 09, 2025)
- **Platform-specific names**: Gemini Live API and Vertex AI Live API use different model naming conventions for the same functionality
- **Easy switching**: Change models without modifying code by updating the `.env` file
- **Environment-specific configuration**: Use different models for development, staging, and production

**Configuration in `.env` file:**

```bash
# For Gemini Live API (publicly available)
DEMO_AGENT_MODEL=gemini-2.5-flash-native-audio-preview-12-2025

# For Vertex AI Live API (if using Vertex AI)
# DEMO_AGENT_MODEL=gemini-live-2.5-flash-native-audio
```

Environment Variable Loading Order

When using `.env` files with `python-dotenv`, you must call `load_dotenv()` **before** importing any modules that read environment variables. Otherwise, `os.getenv()` will return `None` and fall back to the default value, ignoring your `.env` configuration.

**Correct order in `main.py`:**

```python
from dotenv import load_dotenv
from pathlib import Path

# Load .env file BEFORE importing agent
load_dotenv(Path(__file__).parent / ".env")

# Now safe to import modules that use environment variables
from google_search_agent.agent import agent
```

**Incorrect order (will not work):**

```python
from dotenv import load_dotenv
from google_search_agent.agent import agent  # Agent reads env var here

# Too late! Agent already initialized with default model
load_dotenv(Path(__file__).parent / ".env")
```

This is a Python import behavior: when you import a module, its top-level code executes immediately. If your agent module calls `os.getenv("DEMO_AGENT_MODEL")` at import time, the `.env` file must already be loaded.

**Selecting the right model:**

1. **Choose platform**: Decide between Gemini Live API (public) or Vertex AI Live API (enterprise)
1. **Choose architecture**:
1. Native Audio for natural conversational AI with advanced features
1. Half-Cascade for production reliability with tool execution
1. **Check current availability**: Refer to the model tables above and official documentation
1. **Configure environment variable**: Set `DEMO_AGENT_MODEL` in your `.env` file (see [`agent.py:11-16`](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/google_search_agent/agent.py#L11-L16) and [`main.py:99-152`](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L99-L152))

### Live API Models Compatibility and Availability

For the latest information on Live API model compatibility and availability:

- **Gemini Live API models**: See the [Gemini models documentation](https://ai.google.dev/gemini-api/docs/models/gemini)
- **Vertex AI Live API models**: See the [Vertex AI model documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

Always verify model availability and feature support in the official documentation before deploying to production.

## Audio Transcription

The Live API provides built-in audio transcription capabilities that automatically convert speech to text for both user input and model output. This eliminates the need for external transcription services and enables real-time captions, conversation logging, and accessibility features. ADK exposes these capabilities through `RunConfig`, allowing you to enable transcription for either or both audio directions.

Source

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

Learn More

For complete Event structure, see [Part 3: The Event Class](https://google.github.io/adk-docs/streaming/dev-guide/part3/#the-event-class).

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

Best Practice for Transcription Null Checking

Always use two-level null checking for transcriptions:

1. Check if the transcription object exists (`if event.input_transcription`)
1. Check if the text is not empty (`if user_text and user_text.strip()`)

This pattern prevents errors from `None` values and handles partial transcriptions that may be empty.

### Handling Audio Transcription at the Client

In web applications, transcription events need to be forwarded from the server to the browser and rendered in the UI. The bidi-demo demonstrates a pattern where the server forwards all ADK events (including transcription events) to the WebSocket client, and the client handles displaying transcriptions as speech bubbles with visual indicators for partial vs. finished transcriptions.

**Architecture:**

1. **Server side**: Forward transcription events through WebSocket (already shown in previous section)
1. **Client side**: Process `inputTranscription` and `outputTranscription` events from the WebSocket
1. **UI rendering**: Display partial transcriptions with typing indicators, finalize when `finished: true`

Demo implementation: [app.js:530-653](https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L532-L655)

```javascript
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

1. **Partial vs Finished States**: Use the `finished` flag to determine whether to show typing indicators:

1. `finished: false` → Show typing indicator (e.g., "...")

1. `finished: true` → Remove typing indicator, finalize bubble

1. **Bubble State Management**: Track current transcription bubbles separately for input and output using IDs. Create new bubbles only when starting fresh transcriptions:

   ```javascript
   if (currentInputTranscriptionId == null) {
       // Create new bubble
   } else {
       // Update existing bubble
   }
   ```

1. **Turn Coordination**: When the model starts responding (first output transcription arrives), finalize any active input transcription to prevent overlapping updates.

This pattern ensures smooth real-time transcription display with proper handling of streaming updates, turn transitions, and visual feedback for users.

### Multi-Agent Transcription Requirements

For multi-agent scenarios (agents with `sub_agents`), ADK automatically enables audio transcription regardless of your `RunConfig` settings. This automatic behavior is required for agent transfer functionality, where text transcriptions are used to pass conversation context between agents.

**Automatic Enablement Behavior:**

When an agent has `sub_agents` defined, ADK's `run_live()` method automatically enables both input and output audio transcription **even if you explicitly set them to `None`**. This ensures that agent transfers work correctly by providing text context to the next agent.

**Why This Matters:**

1. **Cannot be disabled**: You cannot turn off transcription in multi-agent scenarios
1. **Required for functionality**: Agent transfer breaks without text context
1. **Transparent to developers**: Transcription events are automatically available
1. **Plan for data handling**: Your application will receive transcription events that must be processed

**Implementation Details:**

The automatic enablement happens in `Runner.run_live()` when both conditions are met:

- The agent has `sub_agents` defined
- A `LiveRequestQueue` is provided (bidirectional streaming mode)

Source

[`runners.py:1395-1404`](https://github.com/google/adk-python/blob/fd2c0f556b786417a9f6add744827b07e7a06b7d/src/google/adk/runners.py#L1395-L1404)

## Voice Configuration (Speech Config)

The Live API provides voice configuration capabilities that allow you to customize how the model sounds when generating audio responses. ADK supports voice configuration at two levels: **agent-level** (per-agent voice settings) and **session-level** (global voice settings via RunConfig). This enables sophisticated multi-agent scenarios where different agents can speak with different voices, as well as single-agent applications with consistent voice characteristics.

Source

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

### Configuration Precedence

When both agent-level (via `Gemini` instance) and session-level (via `RunConfig`) `speech_config` are provided, **agent-level configuration takes precedence**. This allows you to set a default voice in RunConfig while overriding it for specific agents.

**Precedence Rules:**

1. **Gemini instance has `speech_config`**: Use the Gemini's voice configuration (highest priority)
1. **RunConfig has `speech_config`**: Use RunConfig's voice configuration
1. **Neither specified**: Use Live API default voice (lowest priority)

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

**Vertex AI Live API:**

- ✅ Voice configuration supported
- ⚠️ **Platform-specific difference**: Voice availability may differ from Gemini Live API
- ⚠️ **Verification required**: Check [Vertex AI documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api) for the current list of supported voices

**Best practice**: Always test your chosen voice configuration on your target platform during development. If a voice is not supported on your platform/model combination, the Live API will return an error at connection time.

### Important Notes

- **Model compatibility**: Voice configuration is only available for Live API models with audio output capabilities
- **Configuration levels**: You can set `speech_config` at the agent level (via `Gemini(speech_config=...)`) or session level (`RunConfig(speech_config=...)`). Agent-level configuration takes precedence.
- **Agent-level usage**: To configure voice per agent, create a `Gemini` instance with `speech_config` and pass it to `Agent(model=gemini_instance)`
- **Default behavior**: If `speech_config` is not specified at either level, the Live API uses a default voice
- **Native audio models**: Automatically determine language based on conversation context; explicit `language_code` may not be supported
- **Voice availability**: Specific voice names may vary by model; refer to the current Live API documentation for supported voices on your chosen model

Learn More

For complete RunConfig reference, see [Part 4: Understanding RunConfig](https://google.github.io/adk-docs/streaming/dev-guide/part4/index.md).

## Voice Activity Detection (VAD)

Voice Activity Detection (VAD) is a Live API feature that automatically detects when users start and stop speaking, enabling natural turn-taking without manual control. VAD is **enabled by default** on all Live API models, allowing the model to automatically manage conversation turns based on detected speech activity.

Source

[Gemini Live API - Voice Activity Detection](https://ai.google.dev/gemini-api/docs/live-guide#voice-activity-detection-vad)

### How VAD Works

When VAD is enabled (the default), the Live API automatically:

1. **Detects speech start**: Identifies when a user begins speaking
1. **Detects speech end**: Recognizes when a user stops speaking (natural pauses)
1. **Manages turn-taking**: Allows the model to respond when the user finishes speaking
1. **Handles interruptions**: Enables natural conversation flow with back-and-forth exchanges

This creates a hands-free, natural conversation experience where users don't need to manually signal when they're speaking or done speaking.

### When to Disable VAD

You should disable automatic VAD in these scenarios:

- **Push-to-talk implementations**: Your application manually controls when audio should be sent (e.g., audio interaction apps in noisy environments or rooms with cross-talk)
- **Client-side voice detection**: Your application uses client-side VAD that sends activity signals to your server to reduce CPU and network overhead from continuous audio streaming
- **Specific UX patterns**: Your design requires users to manually indicate when they're done speaking

When you disable VAD (which is enabled by default), you must use manual activity signals (`ActivityStart`/`ActivityEnd`) to control conversation turns. See [Part 2: Activity Signals](https://google.github.io/adk-docs/streaming/dev-guide/part2/#activity-signals) for details on manual turn control.

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
1. **Signal coordination**: Send `activity_start` when voice detected, `activity_end` when voice stops
1. **Audio streaming**: Send audio chunks only during active speech periods
1. **Server configuration**: Disable automatic VAD since client handles detection

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
1. **Adjustable Threshold**: The `threshold` value (0.05 in the example) can be tuned based on the environment. Lower thresholds are more sensitive (detect quieter speech but may trigger on background noise), higher thresholds require louder speech.
1. **Silence Timeout**: Use a timeout (e.g., 2000ms) before sending `activity_end` to avoid prematurely ending a turn during natural pauses in speech. This creates a more natural conversation flow.
1. **State Management**: Track `isSilence` state to detect transitions between silence and speech. Send `activity_start` only on silence→speech transitions, and `activity_end` only after sustained silence.
1. **Conditional Audio Streaming**: Only send audio chunks when `!isSilence` to reduce bandwidth. This can save ~50-90% of network traffic depending on the conversation's speech-to-silence ratio.
1. **AudioWorklet Thread Separation**: The VAD processor runs on the audio rendering thread, ensuring real-time performance without being affected by main thread JavaScript execution or network delays.

#### Benefits of Client-Side VAD

This pattern provides several advantages:

- **Reduced CPU and network overhead**: Only send audio during active speech, not continuous silence
- **Faster response**: Immediate local detection without server round-trip
- **Better control**: Fine-tune VAD sensitivity based on client environment

Activity Signal Timing

When using manual activity signals with client-side VAD:

- Always send `activity_start` **before** sending the first audio chunk
- Always send `activity_end` **after** sending the last audio chunk
- The model will only process audio between `activity_start` and `activity_end` signals
- Incorrect timing may cause the model to ignore audio or produce unexpected behavior

## Proactivity and Affective Dialog

The Live API offers advanced conversational features that enable more natural and context-aware interactions. **Proactive audio** allows the model to intelligently decide when to respond, offer suggestions without explicit prompts, or ignore irrelevant input. **Affective dialog** enables the model to detect and adapt to emotional cues in voice tone and content, adjusting its response style for more empathetic interactions. These features are currently supported only on native audio models.

Source

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

- ✅ Supported on `gemini-2.5-flash-native-audio-preview-12-2025` (native audio model)
- ❌ Not supported on `gemini-live-2.5-flash-preview` (half-cascade model)

**Vertex AI Live API:**

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

1. **Test emotional response**:

   ```text
   User: [frustrated tone] "This isn't working at all!"
   Expected: Model acknowledges emotion, adjusts response style
   ```

1. **Monitor for unprompted responses**:

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

In this part, you learned how to implement multimodal features in ADK Bidi-streaming applications, focusing on audio, image, and video capabilities. We covered audio specifications and format requirements, explored the differences between native audio and half-cascade architectures, examined how to send and receive audio streams through LiveRequestQueue and Events, and learned about advanced features like audio transcription, voice activity detection, and proactive/affective dialog. You now understand how to build natural voice-enabled AI experiences with proper audio handling, implement video streaming for visual context, and configure model-specific features based on platform capabilities. With this comprehensive understanding of ADK's multimodal streaming features, you're equipped to build production-ready applications that handle text, audio, image, and video seamlessly—creating rich, interactive AI experiences across diverse use cases.

**Congratulations!** You've completed the ADK Bidi-streaming Developer Guide. You now have a comprehensive understanding of how to build production-ready real-time streaming AI applications with Google's Agent Development Kit.

← [Previous: Part 4: Understanding RunConfig](https://google.github.io/adk-docs/streaming/dev-guide/part4/index.md)
