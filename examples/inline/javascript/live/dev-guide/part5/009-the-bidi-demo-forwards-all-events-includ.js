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