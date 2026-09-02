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