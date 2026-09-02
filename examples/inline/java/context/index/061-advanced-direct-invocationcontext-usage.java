// Example: Inside agent's runAsyncImpl
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.InvocationContext;
import com.google.adk.events.Event;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.List;

public class MyControllingAgent extends BaseAgent {

  @Override
  protected Flowable<Event> runAsyncImpl(InvocationContext ctx) {
    // Example: Check if a specific service is available
    if (ctx.memoryService() == null) {
      System.out.println("Memory service is not available for this invocation.");
      // Potentially change agent behavior
    }

    // Example: Early termination based on some condition
    Boolean criticalError = (Boolean) ctx.session().state().getOrDefault("critical_error_flag", false);
    if (criticalError != null && criticalError) {
      System.out.println("Critical error detected, ending invocation.");
      ctx.setEndInvocation(true); // Signal framework to stop processing

      Event errorEvent = Event.builder()
          .author(name())
          .invocationId(ctx.invocationId())
          .content(Content.builder().parts(List.of(Part.builder().text("Stopping due to critical error.").build())).build())
          .build();

      return Flowable.just(errorEvent); // Stop this agent's execution
    }

    // ... Normal agent processing ...
    // return Flowable.just(normalEvent);
    return Flowable.empty();
  }
}