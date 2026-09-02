// Conceptual Code: Iterative Code Refinement
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.LoopAgent;
import com.google.adk.events.Event;
import com.google.adk.events.EventActions;
import com.google.adk.agents.InvocationContext;
import io.reactivex.rxjava3.core.Flowable;
import java.util.List;


// Agent to generate/refine code based on state['current_code'] and state['requirements']
LlmAgent codeRefiner = LlmAgent.builder()
    .name("CodeRefiner")
    .instruction("Read state['current_code'] (if exists) and state['requirements']. Generate/refine Java code to meet requirements. Save to state['current_code'].")
    .outputKey("current_code") // Overwrites previous code in state
    .build();


// Agent to check if the code meets quality standards
LlmAgent qualityChecker = LlmAgent.builder()
    .name("QualityChecker")
    .instruction("Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.")
    .outputKey("quality_status")
    .build();


BaseAgent checkStatusAndEscalate = new BaseAgent(
    "StopChecker","Checks quality_status and escalates if 'pass'.", List.of(), null, null) {


  @Override
  protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
    String status = (String) invocationContext.session().state().getOrDefault("quality_status", "fail");
    boolean shouldStop = "pass".equals(status);


    EventActions actions = EventActions.builder().escalate(shouldStop).build();
    Event event = Event.builder()
        .author(this.name())
        .actions(actions)
        .build();
    return Flowable.just(event);
  }
};


LoopAgent refinementLoop = LoopAgent.builder()
    .name("CodeRefinementLoop")
    .maxIterations(5)
    .subAgents(codeRefiner, qualityChecker, checkStatusAndEscalate)
    .build();


// Loop runs: Refiner -> Checker -> StopChecker
// State['current_code'] is updated each iteration.
// Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5
// iterations.