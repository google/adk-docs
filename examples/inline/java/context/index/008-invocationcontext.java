// Example: Agent implementation receiving InvocationContext
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.InvocationContext;
import com.google.adk.events.Event;
import io.reactivex.rxjava3.core.Flowable;

public class MyAgent extends BaseAgent {
    @Override
    protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
        // Direct access example
        String agentName = invocationContext.agent().name();
        String sessionId = invocationContext.session().id();
        String invocationId = invocationContext.invocationId();
        System.out.println("Agent " + agentName + " running in session " + sessionId + " for invocation " + invocationId);
        // ... agent logic using invocationContext ...
        return Flowable.empty();
    }
}