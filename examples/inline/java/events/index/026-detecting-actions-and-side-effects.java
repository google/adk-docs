import java.util.concurrent.ConcurrentMap;
import com.google.genai.types.Part;
import com.google.adk.events.EventActions;

EventActions actions = event.actions(); // Assuming event.actions() is not null
if (actions != null && actions.artifactDelta() != null && !actions.artifactDelta().isEmpty()) {
    ConcurrentMap<String, Part> artifactChanges = actions.artifactDelta();
    System.out.println("  Artifacts saved: " + artifactChanges);
    // UI might refresh an artifact list
    // Iterate through artifactChanges.entrySet() to get filename and Part details
}