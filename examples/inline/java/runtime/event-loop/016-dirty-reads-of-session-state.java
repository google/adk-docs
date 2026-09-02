// Modify state - Code in BeforeAgentCallback
// AND stages this change in callbackContext.eventActions().stateDelta().
callbackContext.state().put("field_1", "value_1");

// --- agent runs ... ---

// --- Code in a tool called later *within the same invocation* ---
// Readable (dirty read), but 'value_1' isn't guaranteed persistent yet.
Object val = toolContext.state().get("field_1"); // 'val' will likely be 'value_1' here
System.out.println("Dirty read value in tool: " + val);
// Assume the event carrying the state_delta={'field_1': 'value_1'}
// is yielded *after* this tool runs and is processed by the Runner.