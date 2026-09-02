// Example: In a callback or initial tool
import com.google.adk.agents.CallbackContext;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.Optional;

public void saveDocumentReference(CallbackContext context, String filePath) {
    // Assume file_path is something like "gs://my-bucket/docs/report.pdf" or "/local/path/to/report.pdf"
    try {
        // Create a Part containing the path/URI text
        Part artifactPart = Part.fromText(filePath);
        Optional<Integer> version = context.saveArtifact("document_to_summarize.txt", artifactPart);
        System.out.println("Saved document reference" + filePath + " as artifact version " + version.orElse(-1));
        // Store the filename in state if needed by other tools
        context.state().put("temp:doc_artifact_name", "document_to_summarize.txt");
    } catch (Exception e) {
        System.out.println("Unexpected error saving artifact reference: " + e);
    }
}

// Example usage:
// saveDocumentReference(context, "gs://my-bucket/docs/report.pdf")