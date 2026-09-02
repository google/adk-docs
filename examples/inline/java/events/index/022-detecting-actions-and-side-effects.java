import java.util.concurrent.ConcurrentMap;
import com.google.adk.events.EventActions;

EventActions actions = event.actions(); // Assuming event.actions() is not null
if (actions != null && actions.stateDelta() != null && !actions.stateDelta().isEmpty()) {
    ConcurrentMap<String, Object> stateChanges = actions.stateDelta();
    System.out.println("  State changes: " + stateChanges);
    // Update local UI or application state if necessary
}