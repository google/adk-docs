// Example: In the Summarizer tool function
import com.google.adk.tools.ToolContext;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.Map;
import java.util.Optional;
import java.io.FileNotFoundException;

public Map<String, String> summarizeDocumentTool(ToolContext toolContext) {
    String artifactName = (String) toolContext.state().get("temp:doc_artifact_name");
    if (artifactName == null || artifactName.isEmpty()) {
        return Map.of("error", "Document artifact name not found in state.");
    }
    try {
        // 1. Load the artifact part containing the path/URI
        Optional<Part> artifactPart = toolContext.loadArtifact(artifactName);
        if (!artifactPart.isPresent() || !artifactPart.get().text().isPresent() || artifactPart.get().text().get().isEmpty()) {
            return Map.of("error", "Could not load artifact or artifact has no text path: " + artifactName);
        }
        String filePath = artifactPart.get().text().get();
        System.out.println("Loaded document reference: " + filePath);

        // 2. Read the actual document content (outside ADK context)
        String documentContent = "";
        if (filePath.startsWith("gs://")) {
            // Example: Use GCS client library to download/read into documentContent
            // Replace with actual GCS reading logic
        } else if (filePath.startsWith("/")) {
            // Example: Use local file system to download/read into documentContent
        } else {
            return Map.of("error", "Unsupported file path scheme: " + filePath);
        }

        // 3. Summarize the content
        if (documentContent.isEmpty()) {
            return Map.of("error", "Failed to read document content.");
        }

        // summary = summarizeText(documentContent) // Call your summarization logic
        String summary = "Summary of content from " + filePath; // Placeholder

        return Map.of("summary", summary);
    } catch (IllegalArgumentException e) {
        return Map.of("error", "Artifact service error " + e);
    } catch (Exception e) {
        return Map.of("error", "Error reading document " + e);
    }
}