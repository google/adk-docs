// Simplified view of logic inside Agent.runAsync, callbacks, or tools

// ... previous code runs based on current state ...

// 1. Determine a change or output is needed, construct the event
// Example: Updating state
const updateData = {'field_1': 'value_2'};
const eventWithStateChange = createEvent({
    author: this.name,
    actions: createEventActions({stateDelta: updateData}),
    content: {parts: [{text: "State updated."}]}
    // ... other event fields ...
});

// 2. Yield the event to the Runner for processing & commit
yield eventWithStateChange;
// <<<<<<<<<<<< EXECUTION PAUSES HERE >>>>>>>>>>>>

// <<<<<<<<<<<< RUNNER PROCESSES & COMMITS THE EVENT >>>>>>>>>>>>

// 3. Resume execution ONLY after Runner is done processing the above event.
// Now, the state committed by the Runner is reliably reflected.
// Subsequent code can safely assume the change from the yielded event happened.
const val = ctx.session.state['field_1'];
// here `val` is guaranteed to be "value_2" (assuming Runner committed successfully)
console.log(`Resumed execution. Value of field_1 is now: ${val}`);

// ... subsequent code continues ...
// Maybe yield another event later...