// Pseudocode: Handling final responses in application (TypeScript)
import {
    Event,
    getFunctionResponses,
    isFinalResponse,
    stringifyContent
} from '@google/adk';

async function handleFinalResponses(runnerEvents: AsyncIterable<Event>) {
    let fullResponseText = '';

    for await (const event of runnerEvents) {
        // Accumulate streaming text if needed...
        if (event.partial) {
            fullResponseText += stringifyContent(event);
        }

        // Check if it's a final, displayable event
        if (isFinalResponse(event)) {
            console.log('\n--- Final Output Detected ---');

            const eventText = stringifyContent(event);
            if (fullResponseText || eventText) {
                // If it's the final part of a stream (or a single message), use accumulated text
                const finalText = fullResponseText + (event.partial ? '' : eventText);
                console.log(`Display to user: ${finalText.trim()}`);
                fullResponseText = ''; // Reset accumulator
            } else if (
                event.actions?.skipSummarization &&
                getFunctionResponses(event).length > 0
            ) {
                // Handle displaying the raw tool result if needed
                const responseData = getFunctionResponses(event)[0].response;
                console.log(`Display raw tool result: ${JSON.stringify(responseData)}`);
            } else if (event.longRunningToolIds && event.longRunningToolIds.length > 0) {
                console.log('Display message: Tool is running in background...');
            } else {
                // Handle other types of final responses if applicable
                console.log('Display: Final non-textual response or signal.');
            }
        }
    }
}