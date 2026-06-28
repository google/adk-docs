package callbacks;

// --8<-- [start:init]
import com.google.adk.agents.CallbackContext;
import com.google.adk.agents.Callbacks;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.LlmRequest;
import java.util.Optional;

public class AgentWithBeforeModelCallback {

  public static void main(String[] args) {
    // --- Define your callback logic ---
    Callbacks.BeforeModelCallbackSync myBeforeModelLogic =
        (CallbackContext callbackContext, LlmRequest llmRequest) -> {
          System.out.println(
              "Callback running before model call for agent: " + callbackContext.agentName());
          // ... your custom logic here ...

          // Return Optional.empty() to allow the model call to proceed,
          // similar to returning None in the Python example.
          // If you wanted to return a response and skip the model call,
          // you would return Optional.of(yourLlmResponse).
          return Optional.empty();
        };

    // --- Register it during Agent creation ---
    LlmAgent myAgent =
        LlmAgent.builder()
            .name("MyCallbackAgent")
            .model("gemini-2.0-flash") // Or your desired model
            .instruction("Be helpful.")
            // Other agent parameters...
            .beforeModelCallbackSync(myBeforeModelLogic) // Pass the callback implementation here
            .build();
  }
}
// --8<-- [end:init]
