// Simplified conceptual view of the Runner's main loop logic in Java.
public Flowable<Event> runConceptual(
    Session session,
    InvocationContext invocationContext,
    Content newQuery
    ) {

    // 1. Append new_query to session event history (via SessionService)
    // ...
    sessionService.appendEvent(session, userEvent).blockingGet();

    // 2. Kick off event stream by calling the agent
    Flowable<Event> agentEventStream = agentToRun.runAsync(invocationContext);

    // 3. Process each generated event, commit changes, and "yield" or "emit"
    return agentEventStream.map(event -> {
        // This mutates the session object (adds event, applies stateDelta).
        // The return value of appendEvent (a Single<Event>) is conceptually
        // just the event itself after processing.
        sessionService.appendEvent(session, event).blockingGet(); // Simplified blocking call

        // memory_service.update_memory(...) // If applicable - conceptual
        // artifact_service might have already been called via context during agent run

        // 4. "Yield" event for upstream processing
        //    In RxJava, returning the event in map effectively yields it to the next operator or subscriber.
        return event;
    });
}