import com.google.adk.events.EventActions;
import java.util.Optional;

EventActions actions = event.actions(); // Assuming event.actions() is not null
if (actions != null) {
    Optional<String> transferAgent = actions.transferToAgent();
    if (transferAgent.isPresent()) {
        System.out.println("  Signal: Transfer to " + transferAgent.get());
    }

    Optional<Boolean> escalate = actions.escalate();
    if (escalate.orElse(false)) { // or escalate.isPresent() && escalate.get()
        System.out.println("  Signal: Escalate (terminate loop)");
    }

    Optional<Boolean> skipSummarization = actions.skipSummarization();
    if (skipSummarization.orElse(false)) { // or skipSummarization.isPresent() && skipSummarization.get()
        System.out.println("  Signal: Skip summarization for tool result");
    }
}