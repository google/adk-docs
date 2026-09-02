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