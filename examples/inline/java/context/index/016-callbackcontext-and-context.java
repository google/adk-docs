// Example: Callback receiving CallbackContext
import com.google.adk.agents.CallbackContext;
import com.google.adk.models.LlmRequest;
import com.google.adk.models.LlmResponse;
import io.reactivex.rxjava3.core.Maybe;

public Maybe<LlmResponse> myBeforeModelCb(CallbackContext callbackContext, LlmRequest request) {
    // Read/Write state example
    int callCount = (int) callbackContext.state().getOrDefault("model_calls", 0);
    callbackContext.state().put("model_calls", callCount + 1); // Modify state (tracks delta)

    // Optionally load an artifact
    // Maybe<Part> configPart = callbackContext.loadArtifact("model_config.json");
    System.out.println("Preparing model call " + (callCount + 1) + " for invocation " + callbackContext.invocationId());
    return Maybe.empty(); // Allow model call to proceed
}