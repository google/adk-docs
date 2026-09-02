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