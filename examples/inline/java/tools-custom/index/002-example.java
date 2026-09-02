// Analyzes a document using context from memory.
// You can also list, load and save artifacts using Callback Context or LoadArtifacts tool.
public static @NonNull Maybe<ImmutableMap<String, Object>> processDocument(
    @Annotations.Schema(description = "The name of the document to analyze.") String documentName,
    @Annotations.Schema(description = "The query for the analysis.") String analysisQuery,
    ToolContext toolContext) {

  // 1. List all available artifacts
  System.out.printf(
      "Listing all available artifacts %s:", toolContext.listArtifacts().blockingGet());

  // 2. Load an artifact to memory
  System.out.println("Tool: Attempting to load artifact: " + documentName);
  Part documentPart = toolContext.loadArtifact(documentName, Optional.empty()).blockingGet();
  if (documentPart == null) {
    System.out.println("Tool: Document '" + documentName + "' not found.");
    return Maybe.just(
        ImmutableMap.<String, Object>of(
            "status", "error", "message", "Document '" + documentName + "' not found."));
  }
  String documentText = documentPart.text().orElse("");
  System.out.println(
      "Tool: Loaded document '" + documentName + "' (" + documentText.length() + " chars).");

  // 3. Perform analysis (placeholder)
  String analysisResult =
      "Analysis of '"
          + documentName
          + "' regarding '"
          + analysisQuery
          + " [Placeholder Analysis Result]";
  System.out.println("Tool: Performed analysis.");

  // 4. Save the analysis result as a new artifact
  Part analysisPart = Part.fromText(analysisResult);
  String newArtifactName = "analysis_" + documentName;

  toolContext.saveArtifact(newArtifactName, analysisPart);

  return Maybe.just(
      ImmutableMap.<String, Object>builder()
          .put("status", "success")
          .put("analysis_artifact", newArtifactName)
          .build());
}
// FunctionTool processDocumentTool =
//      FunctionTool.create(ToolContextArtifactExample.class, "processDocument");
// In the Agent, include this function tool.
// LlmAgent agent = LlmAgent().builder().tools(processDocumentTool).build();