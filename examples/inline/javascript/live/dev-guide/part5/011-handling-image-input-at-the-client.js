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