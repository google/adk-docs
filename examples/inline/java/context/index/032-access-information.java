// Example: In a Callback
import com.google.adk.agents.CallbackContext;
import com.google.genai.types.Content;

public void checkInitialIntent(CallbackContext callbackContext) {
    String initialText = "N/A";
    if (callbackContext.userContent().isPresent() && callbackContext.userContent().get().parts() != null && !callbackContext.userContent().get().parts().get().isEmpty()) {
        initialText = callbackContext.userContent().get().parts().get().get(0).text().orElse("Non-text input");
        // ...
        System.out.println("This invocation started with user input: " + initialText);
    }
}