// Example: Instruction provider receiving ReadonlyContext
import com.google.adk.agents.ReadonlyContext;

public String myInstructionProvider(ReadonlyContext context) {
    // Read-only access example
    // state() returns an unmodifiable view of the session state
    String userTier = (String) context.state().getOrDefault("user_tier", "standard");
    // context.state().put("new_key", "value"); // UnsupportedOperationException
    return "Process the request for a " + userTier + " user.";
}