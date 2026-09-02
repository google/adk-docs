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