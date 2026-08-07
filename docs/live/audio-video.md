# Audio and video

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">Experimental</span>
</div>

Audio and video are what make a live agent feel live, and they are also where the exact
formats matter. The Live API expects specific PCM sample rates for input and output, and
images and video frames must be sent through a different method than text.

This page covers sending microphone audio upstream, receiving and playing model audio,
and streaming images and video frames — including the client-side handling each one
implies. For the models that support these modalities see [Supported models](models.md);
for voices, transcription, and turn detection see [Voice](voice.md).

## How to Use Audio

Live API's audio capabilities enable natural voice conversations with sub-second latency through bidirectional audio streaming. This section covers how to send audio input to the model and receive audio responses, including format requirements, streaming best practices, and client-side implementation patterns.

### Sending Audio Input

**Audio Format Requirements:**

Before calling `send_realtime()`, ensure your audio data is already in the correct format:

- **Format**: 16-bit PCM (signed integer)
- **Sample Rate**: 16,000 Hz (16kHz)
- **Channels**: Mono (single channel)

ADK does not perform audio format conversion. Sending audio in incorrect formats will result in poor quality or errors.

```python title='Demo implementation: <a href="https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/main.py#L173-L176" target="_blank">main.py:173-176</a>'
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

```javascript title='Demo implementation: <a href="https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/static/js/audio-recorder.js#L7-L58" target="_blank">audio-recorder.js:7-58</a>'
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

```javascript title='Demo implementation: <a href="https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/static/js/pcm-recorder-processor.js#L1-L18" target="_blank">pcm-recorder-processor.js:1-18</a>'
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

```javascript title='Demo implementation: <a href="https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/static/js/app.js#L994-L1003" target="_blank">app.js:994-1003</a>'
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
from google.adk.agents.run_config import RunConfig

# Configure for audio output
run_config = RunConfig(
    response_modalities=["AUDIO"],  # Required for audio responses
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

!!! note "Automatic Base64 Decoding"

    The Live API wire protocol transmits audio data as base64-encoded strings. The google.genai types system uses Pydantic's base64 serialization feature (`val_json_bytes='base64'`) to automatically decode base64 strings into bytes when deserializing API responses. When you access `part.inline_data.data`, you receive ready-to-use bytes—no manual base64 decoding needed.

#### Handling Audio Events at the Client

The bidi-demo uses a different architectural approach: instead of processing audio on the server, it forwards all events (including audio data) to the WebSocket client and handles audio playback in the browser. This pattern separates concerns—the server focuses on ADK event streaming while the client handles media playback using Web Audio API.

```python title='Demo implementation: <a href="https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/main.py#L213-L222" target="_blank">main.py:213-222</a>'
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

```javascript title='Demo implementation: <a href="https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/static/js/app.js#L645-L704" target="_blank">app.js:645-704</a>'
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

```javascript title='Demo implementation: <a href="https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/static/js/audio-player.js#L5-L24" target="_blank">audio-player.js:5-24</a>'
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

```javascript title='Demo implementation: <a href="https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/static/js/pcm-player-processor.js#L5-L75" target="_blank">pcm-player-processor.js:5-75</a>'
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

```python title='Demo implementation: <a href="https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/main.py#L191-L205" target="_blank">main.py:191-205</a>'
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

```javascript title='Demo implementation: <a href="https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/static/js/app.js#L818-L845" target="_blank">app.js:818-845</a>'
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

```javascript title='Demo implementation: <a href="https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/static/js/app.js#L863-L918" target="_blank">app.js:863-918</a>'
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

