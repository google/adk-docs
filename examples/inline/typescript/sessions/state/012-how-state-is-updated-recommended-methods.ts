import { InMemorySessionService, createEvent, createEventActions } from "@google/adk";

// --- Setup ---
const sessionService = new InMemorySessionService();
const appName = "state_app_manual";
const userId = "user2";
const sessionId = "session2";
const session = await sessionService.createSession({
    appName,
    userId,
    sessionId,
    state: { "user:login_count": 0, "task_status": "idle" }
});
console.log(`Initial state: ${JSON.stringify(session.state)}`);

// --- Define State Changes ---
const currentTime = Date.now();
const stateChanges = {
    "task_status": "active",              // Update session state
    "user:login_count": (session.state["user:login_count"] as number || 0) + 1, // Update user state
    "user:last_login_ts": currentTime,   // Add user state
    "temp:validation_needed": true        // Add temporary state (will be discarded)
};

// --- Create Event with Actions ---
const actionsWithUpdate = createEventActions({
    stateDelta: stateChanges,
});
// This event might represent an internal system action, not just an agent response
const systemEvent = createEvent({
    invocationId: "inv_login_update",
    author: "system", // Or 'agent', 'tool' etc.
    actions: actionsWithUpdate,
    timestamp: currentTime
    // content might be null or represent the action taken
});

// --- Append the Event (This updates the state) ---
await sessionService.appendEvent({ session, event: systemEvent });
console.log("`appendEvent` called with explicit state delta.");

// --- Check Updated State ---
const updatedSession = await sessionService.getSession({
    appName,
    userId,
    sessionId
});
console.log(`State after event: ${JSON.stringify(updatedSession?.state)}`);
// Expected: {"user:login_count":1,"task_status":"active","user:last_login_ts":<timestamp>}
// Note: 'temp:validation_needed' is NOT present.