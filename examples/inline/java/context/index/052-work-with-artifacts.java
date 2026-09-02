// Example: In a tool function
import com.google.adk.tools.ToolContext;
import io.reactivex.rxjava3.core.Single;
import java.util.List;
import java.util.Map;

public Map<String, Object> checkAvailableDocs(ToolContext toolContext) {
    try {
        Single<List<String>> artifactKeys = toolContext.listArtifacts();
        System.out.println("Available artifacts: " + artifactKeys.blockingGet().toString());
        return Map.of("availableDocs", artifactKeys.blockingGet());
    } catch (IllegalArgumentException e) {
        return Map.of("error", "Artifact service error: " + e);
    }
}