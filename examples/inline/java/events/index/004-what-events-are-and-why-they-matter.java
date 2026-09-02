// Conceptual Structure of an Event (Java - See com.google.adk.events.Event.java)
// Simplified view based on the provided com.google.adk.events.Event.java
// public class Event extends JsonBaseModel {
//     // --- Fields analogous to LlmResponse ---
//     private Optional<Content> content;
//     private Optional<Boolean> partial;
//     // ... other response fields like errorCode, errorMessage ...

//     // --- ADK specific additions ---
//     private String author;         // 'user' or agent name
//     private String invocationId;   // ID for the whole interaction run
//     private String id;             // Unique ID for this specific event
//     private long timestamp;        // Creation time (epoch milliseconds)
//     private EventActions actions;  // Important for side-effects & control
//     private Optional<String> branch; // Hierarchy path
//     // ... other fields like turnComplete, longRunningToolIds etc.
// }