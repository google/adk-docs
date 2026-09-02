import com.google.adk.agents.CallbackContext;
import com.google.adk.artifacts.BaseArtifactService;
import com.google.adk.artifacts.InMemoryArtifactService;
import com.google.genai.types.Part;
import java.nio.charset.StandardCharsets;

public class SaveArtifactExample {

public void saveGeneratedReport(CallbackContext callbackContext, byte[] reportBytes) {
// Saves generated PDF report bytes as an artifact.
Part reportArtifact = Part.fromBytes(reportBytes, "application/pdf");
String filename = "generatedReport.pdf";

    callbackContext.saveArtifact(filename, reportArtifact);
    System.out.println("Successfully saved Java artifact '" + filename);
    // The event generated after this callback will contain:
    // event().actions().artifactDelta == {"generated_report.pdf": version}
}

// --- Example Usage Concept (Java) ---
public static void main(String[] args) {
    BaseArtifactService service = new InMemoryArtifactService(); // Or GcsArtifactService
    SaveArtifactExample myTool = new SaveArtifactExample();
    byte[] reportData = "...".getBytes(StandardCharsets.UTF_8); // PDF bytes
    CallbackContext callbackContext; // ... obtain callback context from your app
    myTool.saveGeneratedReport(callbackContext, reportData);
    // Due to async nature, in a real app, ensure program waits or handles completion.
  }
}