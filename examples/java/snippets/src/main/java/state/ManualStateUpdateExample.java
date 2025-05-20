package state;

// --8<-- [start:full_code]

import com.google.adk.events.Event;
import com.google.adk.events.EventActions;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class ManualStateUpdateExample {

  public static void main(String[] args) {
    // --- Setup ---
    InMemorySessionService sessionService = new InMemorySessionService();
    String appName = "state_app_manual";
    String userId = "user2";
    String sessionId = "session2";

    ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>();
    initialState.put("user:login_count", 0);
    initialState.put("task_status", "idle");

    Session session =
        sessionService.createSession(appName, userId, initialState, sessionId).blockingGet();
    System.out.println("Initial state: " + session.state().entrySet());

    // --- Define State Changes ---
    long currentTimeMillis = Instant.now().toEpochMilli(); // Use milliseconds for Java Event

    ConcurrentMap<String, Object> stateChanges = new ConcurrentHashMap<>();
    stateChanges.put("task_status", "active"); // Update session state

    // Retrieve and increment login_count
    Object loginCountObj = session.state().get("user:login_count");
    int currentLoginCount = 0;
    if (loginCountObj instanceof Number) {
      currentLoginCount = ((Number) loginCountObj).intValue();
    }
    stateChanges.put("user:login_count", currentLoginCount + 1); // Update user state

    stateChanges.put("user:last_login_ts", currentTimeMillis); // Add user state (as long milliseconds)
    stateChanges.put("temp:validation_needed", true); // Add temporary state

    // --- Create Event with Actions ---
    EventActions actionsWithUpdate = EventActions.builder().stateDelta(stateChanges).build();

    // This event might represent an internal system action, not just an agent response
    Event systemEvent =
        Event.builder()
            .invocationId("inv_login_update")
            .author("system") // Or 'agent', 'tool' etc.
            .actions(actionsWithUpdate)
            .timestamp(currentTimeMillis)
            // content might be None or represent the action taken
            .build();

    // --- Append the Event (This updates the state) ---
    sessionService.appendEvent(session, systemEvent).blockingGet();
    System.out.println("`appendEvent` called with explicit state delta.");

    // --- Check Updated State ---
    Session updatedSession =
        sessionService.getSession(appName, userId, sessionId, Optional.empty()).blockingGet();
    assert updatedSession != null;
    System.out.println("State after event: " + updatedSession.state().entrySet());
    // Expected: {'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp_millis>}
    // Note: 'temp:validation_needed' is NOT present because InMemorySessionService's appendEvent
    // applies delta to its internal user/app state maps IF keys have prefixes,
    // and to the session's own state map (which is then merged on getSession).
  }
}
// --8<-- [end:full_code]