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