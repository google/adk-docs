// Inside agent logic (conceptual)

// 1. Modify state
// In TypeScript, you modify state via the context, which tracks the change.
ctx.state.set('status', 'processing');
// The framework will automatically populate actions with the state
// delta from the context. For illustration, it's shown here.
const event1 = createEvent({
    actions: createEventActions({stateDelta: {'status': 'processing'}}),
    // ... other event fields
});

// 2. Yield event with the delta
yield event1;
// --- PAUSE --- Runner processes event1, SessionService commits 'status' = 'processing' ---

// 3. Resume execution
// Now it's safe to rely on the committed state in the session object.
const currentStatus = ctx.session.state['status']; // Guaranteed to be 'processing'
console.log(`Status after resuming: ${currentStatus}`);