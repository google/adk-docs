// Inside agent logic (conceptual)
// ... previous code runs based on current state ...

// 1. Prepare state modification and construct the event
ConcurrentHashMap<String, Object> stateChanges = new ConcurrentHashMap<>();
stateChanges.put("status", "processing");

EventActions actions = EventActions.builder().stateDelta(stateChanges).build();
Content content = Content.builder().parts(Part.fromText("Status update: processing")).build();

Event event1 = Event.builder()
    .actions(actions)
    // ...
    .build();

// 2. Yield event with the delta
return Flowable.just(event1)
    .map(
        emittedEvent -> {
            // --- CONCEPTUAL PAUSE & RUNNER PROCESSING ---
            // 3. Resume execution (conceptually)
            // Now it's safe to rely on the committed state.
            String currentStatus = (String) ctx.session().state().get("status");
            System.out.println("Status after resuming (inside agent logic): " + currentStatus); // Guaranteed to be 'processing'

            // The event itself (event1) is passed on.
            // If subsequent logic within this agent step produced *another* event,
            // you'd use concatMap to emit that new event.
            return emittedEvent;
        });

// ... subsequent agent logic might involve further reactive operators
// or emitting more events based on the now-updated `ctx.session().state()`.