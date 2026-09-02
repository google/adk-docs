// Code in beforeAgentCallback
callbackContext.state.set('field_1', 'value_1');
// State is locally set to 'value_1', but not yet committed by Runner

// --- agent runs ... ---

// --- Code in a tool called later *within the same invocation* ---
// Readable (dirty read), but 'value_1' isn't guaranteed persistent yet.
const val = toolContext.state.get('field_1'); // 'val' will likely be 'value_1' here
console.log(`Dirty read value in tool: ${val}`);

// Assume the event carrying the state_delta={'field_1': 'value_1'}
// is yielded *after* this tool runs and is processed by the Runner.