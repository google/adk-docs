// Handle incoming messages
websocket.onmessage = function (event) {
    // Parse the incoming ADK Event
    const adkEvent = JSON.parse(event.data);

    // Handle turn complete event
    if (adkEvent.turnComplete === true) {
        // Remove typing indicator from current message
        if (currentBubbleElement) {
            const textElement = currentBubbleElement.querySelector(".bubble-text");
            const typingIndicator = textElement.querySelector(".typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }
        currentMessageId = null;
        currentBubbleElement = null;
        return;
    }

    // Handle interrupted event
    if (adkEvent.interrupted === true) {
        // Stop audio playback if it's playing
        if (audioPlayerNode) {
            audioPlayerNode.port.postMessage({ command: "endOfAudio" });
        }

        // Keep the partial message but mark it as interrupted
        if (currentBubbleElement) {
            const textElement = currentBubbleElement.querySelector(".bubble-text");

            // Remove typing indicator
            const typingIndicator = textElement.querySelector(".typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }

            // Add interrupted marker
            currentBubbleElement.classList.add("interrupted");
        }

        currentMessageId = null;
        currentBubbleElement = null;
        return;
    }

    // Handle content events (text or audio)
    if (adkEvent.content && adkEvent.content.parts) {
        const parts = adkEvent.content.parts;

        for (const part of parts) {
            // Handle text
            if (part.text) {
                // Add a new message bubble for a new turn
                if (currentMessageId == null) {
                    currentMessageId = Math.random().toString(36).substring(7);
                    currentBubbleElement = createMessageBubble(part.text, false, true);
                    currentBubbleElement.id = currentMessageId;
                    messagesDiv.appendChild(currentBubbleElement);
                } else {
                    // Update the existing message bubble with accumulated text
                    const existingText = currentBubbleElement.querySelector(".bubble-text").textContent;
                    const cleanText = existingText.replace(/\.\.\.$/, '');
                    updateMessageBubble(currentBubbleElement, cleanText + part.text, true);
                }

                scrollToBottom();
            }
        }
    }
};