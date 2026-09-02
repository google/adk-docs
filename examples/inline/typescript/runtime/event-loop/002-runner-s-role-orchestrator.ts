// Simplified view of Runner's main loop logic
async * runAsync(newQuery: Content, ...): AsyncGenerator<Event, void, void> {
    // 1. Append newQuery to session event history (via SessionService)
    await sessionService.appendEvent({
        session,
        event: createEvent({author: 'user', content: newQuery})
    });

    // 2. Kick off event loop by calling the agent
    const agentEventGenerator = agentToRun.runAsync(context);

    for await (const event of agentEventGenerator) {
        // 3. Process the generated event and commit changes
        // Commits state/artifact deltas etc.
        await sessionService.appendEvent({session, event});
        // memoryService.updateMemory(...) // If applicable
        // artifactService might have already been called via context during agent run

        // 4. Yield event for upstream processing (e.g., UI rendering)
        yield event;
        // Runner implicitly signals agent generator can continue after yielding
    }
}