// Example: Tool function receiving ToolContext
import com.google.adk.tools.ToolContext;
import java.util.Map;

// Assume this function is wrapped by a FunctionTool
public Map<String, Object> searchExternalApi(String query, ToolContext toolContext) {
    String apiKey = (String) toolContext.state().getOrDefault("api_key", "");
    if (apiKey.isEmpty()) {
        // Define required auth config
        // authConfig = AuthConfig(...);
        // toolContext.requestCredential(authConfig); // Request credentials
        // Use the 'actions' property to signal the auth request has been made
        return Map.of("status", "Auth Required");
    }

    // Use the API key...
    System.out.println("Tool executing for query " + query + " using API key.");

    // Optionally list artifacts
    // Single<List<String>> availableFiles = toolContext.listArtifacts();

    return Map.of("result", "Data for " + query + " fetched");
}