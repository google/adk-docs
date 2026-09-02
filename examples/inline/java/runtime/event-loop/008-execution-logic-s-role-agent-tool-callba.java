// Simplified view of logic inside Agent.runAsync, callbacks, or tools
// ... previous code runs based on current state ...

// 1. Determine a change or output is needed, construct the event
// Example: Updating state
ConcurrentMap<String, Object> updateData = new ConcurrentHashMap<>();
updateData.put("field_1", "value_2");

EventActions actions = EventActions.builder().stateDelta(updateData).build();
Content eventContent = Content.builder().parts(Part.fromText("State updated.")).build();

Event eventWithStateChange = Event.builder()
    .author(self.name())
    .actions(actions)
    .content(Optional.of(eventContent))
    // ... other event fields ...
    .build();

// 2. "Yield" the event. In RxJava, this means emitting it into the stream.
//    The Runner (or upstream consumer) will subscribe to this Flowable.
//    When the Runner receives this event, it will process it (e.g., call sessionService.appendEvent).
//    The 'appendEvent' in Java ADK mutates the 'Session' object held within 'ctx' (InvocationContext).

// <<<<<<<<<<<< CONCEPTUAL PAUSE POINT >>>>>>>>>>>>
// In RxJava, the emission of 'eventWithStateChange' happens, and then the stream
// might continue with a 'flatMap' or 'concatMap' operator that represents
// the logic *after* the Runner has processed this event.

// To model the "resume execution ONLY after Runner is done processing":
// The Runner's `appendEvent` is usually an async operation itself (returns Single<Event>).
// The agent's flow needs to be structured such that subsequent logic
// that depends on the committed state runs *after* that `appendEvent` completes.

// This is how the Runner typically orchestrates it:
// Runner:
//   agent.runAsync(ctx)
//     .concatMapEager(eventFromAgent ->
//         sessionService.appendEvent(ctx.session(), eventFromAgent) // This updates ctx.session().state()
//             .toFlowable() // Emits the event after it's processed
//     )
//     .subscribe(processedEvent -> { /* UI renders processedEvent */ });

// So, within the agent's own logic, if it needs to do something *after* an event it yielded
// has been processed and its state changes are reflected in ctx.session().state(),
// that subsequent logic would typically be in another step of its reactive chain.

// For this conceptual example, we'll emit the event, and then simulate the "resume"
// as a subsequent operation in the Flowable chain.

return Flowable.just(eventWithStateChange) // Step 2: Yield the event
    .concatMap(yieldedEvent -> {
        // <<<<<<<<<<<< RUNNER CONCEPTUALLY PROCESSES & COMMITS THE EVENT >>>>>>>>>>>>
        // At this point, in a real runner, ctx.session().appendEvent(yieldedEvent) would have been called
        // by the Runner, and ctx.session().state() would be updated.
        // Since we are *inside* the agent's conceptual logic trying to model this,
        // we assume the Runner's action has implicitly updated our 'ctx.session()'.

        // 3. Resume execution.
        // Now, the state committed by the Runner (via sessionService.appendEvent)
        // is reliably reflected in ctx.session().state().
        Object val = ctx.session().state().get("field_1");
        // here `val` is guaranteed to be "value_2" because the `sessionService.appendEvent`
        // called by the Runner would have updated the session state within the `ctx` object.

        System.out.println("Resumed execution. Value of field_1 is now: " + val);

        // ... subsequent code continues ...
        // If this subsequent code needs to yield another event, it would do so here.