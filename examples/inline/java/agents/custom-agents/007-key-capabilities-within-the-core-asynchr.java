// Example: Running one sub-agent
// return someSubAgent.runAsync(ctx);

// Example: Running sub-agents sequentially
Flowable<Event> firstAgentEvents = someSubAgent1.runAsync(ctx)
    .doOnNext(event -> System.out.println("Event from agent 1: " + event.id()));

Flowable<Event> secondAgentEvents = Flowable.defer(() ->
    someSubAgent2.runAsync(ctx)
        .doOnNext(event -> System.out.println("Event from agent 2: " + event.id()))
);

return firstAgentEvents.concatWith(secondAgentEvents);