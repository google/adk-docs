// Pseudocode: Handling final responses in application (Java)
import com.google.adk.events.Event;
import com.google.genai.types.Content;
import com.google.genai.types.FunctionResponse;
import java.util.Map;

StringBuilder fullResponseText = new StringBuilder();
runner.run(...).forEach(event -> { // Assuming a stream of events
     // Accumulate streaming text if needed...
     if (event.partial().orElse(false) && event.content().isPresent()) {
         event.content().flatMap(Content::parts).ifPresent(parts -> {
             if (!parts.isEmpty() && parts.get(0).text().isPresent()) {
                 fullResponseText.append(parts.get(0).text().get());
            }
         });
     }

     // Check if it's a final, displayable event
     if (event.finalResponse()) { // Using the method from Event.java
         System.out.println("\n--- Final Output Detected ---");
         if (event.content().isPresent() &&
             event.content().flatMap(Content::parts).map(parts -> !parts.isEmpty() && parts.get(0).text().isPresent()).orElse(false)) {
             // If it's the final part of a stream, use accumulated text
             String eventText = event.content().get().parts().get().get(0).text().get();
             String finalText = fullResponseText.toString() + (event.partial().orElse(false) ? "" : eventText);
             System.out.println("Display to user: " + finalText.trim());
             fullResponseText.setLength(0); // Reset accumulator
         } else if (event.actions() != null && event.actions().skipSummarization().orElse(false)
                    && !event.functionResponses().isEmpty()) {
             // Handle displaying the raw tool result if needed,
             // especially if finalResponse() was true due to other conditions
             // or if you want to display skipped summarization results regardless of finalResponse()
             Map<String, Object> responseData = event.functionResponses().get(0).response().get();
             System.out.println("Display raw tool result: " + responseData);
         } else if (event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()) {
             // This case is covered by event.finalResponse()
             System.out.println("Display message: Tool is running in background...");
         } else {
             // Handle other types of final responses if applicable
             System.out.println("Display: Final non-textual response or signal.");
         }
     }
 });