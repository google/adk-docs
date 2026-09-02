// Conceptual Example: Loop with Condition
// Custom agent to check state and potentially escalate
public static class CheckConditionAgent extends BaseAgent {
  public CheckConditionAgent(String name, String description) {
    super(name, description, List.of(), null, null);
  }

  @Override
  protected Flowable<Event> runAsyncImpl(InvocationContext ctx) {
    String status = (String) ctx.session().state().getOrDefault("status", "pending");
    boolean isDone = "completed".equalsIgnoreCase(status);

    // Emit an event that signals to escalate (exit the loop) if the condition is met.
    // If not done, the escalate flag will be false or absent, and the loop continues.
    Event checkEvent = Event.builder()
            .author(name())
            .id(Event.generateEventId()) // Important to give events unique IDs
            .actions(EventActions.builder().escalate(isDone).build()) // Escalate if done
            .build();
    return Flowable.just(checkEvent);
  }
}

// Agent that might update state.put("status")
LlmAgent processingStepAgent = LlmAgent.builder().name("ProcessingStep").build();
// Custom agent instance for checking the condition
CheckConditionAgent conditionCheckerAgent = new CheckConditionAgent(
    "ConditionChecker",
    "Checks if the status is 'completed'."
);
LoopAgent poller = LoopAgent.builder().name("StatusPoller").maxIterations(10).subAgents(processingStepAgent, conditionCheckerAgent).build();
// When poller runs, it executes processingStepAgent then conditionCheckerAgent repeatedly
// until Checker escalates (state.get("status") == "completed") or 10 iterations pass.