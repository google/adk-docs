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