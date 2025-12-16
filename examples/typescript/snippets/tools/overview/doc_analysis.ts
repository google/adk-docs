import { Part } from "@google/genai";
import { ToolContext } from "@google/adk";

// Analyzes a document using context from memory.
export async function processDocument(
  params: { documentName: string; analysisQuery: string },
  toolContext?: ToolContext
): Promise<Record<string, any>> {
  if (!toolContext) {
    throw new Error("ToolContext is required for this tool.");
  }

  // 1. List all available artifacts
  const artifacts = await toolContext.listArtifacts();
  console.log(`Listing all available artifacts: ${artifacts}`);

  // 2. Load an artifact
  console.log(`Tool: Attempting to load artifact: ${params.documentName}`);
  const documentPart = await toolContext.loadArtifact(params.documentName);
  if (!documentPart) {
    console.log(`Tool: Document '${params.documentName}' not found.`);
    return {
      status: "error",
      message: `Document '${params.documentName}' not found.`, 
    };
  }

  const documentText = documentPart.text ?? "";
  console.log(
    `Tool: Loaded document '${params.documentName}' (${documentText.length} chars).`
  );

  // 3. Search memory for related context
  console.log(`Tool: Searching memory for context related to '${params.analysisQuery}'`);
  const memory_results = await toolContext.searchMemory(params.analysisQuery);
  console.log(`Tool: Found ${memory_results.memories.length} relevant memories.`);
  const context_from_memory = memory_results.memories
    .map((m) => m.content.parts[0].text)
    .join("\n");

  // 4. Perform analysis (placeholder)
  const analysisResult =
    `Analysis of '${params.documentName}' regarding '${params.analysisQuery}':\n` +
    `Context from Memory:\n${context_from_memory}\n` +
    `[Placeholder Analysis Result]`;
  console.log("Tool: Performed analysis.");

  // 5. Save the analysis result as a new artifact
  const analysisPart: Part = { text: analysisResult };
  const newArtifactName = `analysis_${params.documentName}`;
  await toolContext.saveArtifact(newArtifactName, analysisPart);
  console.log(`Tool: Saved analysis result to '${newArtifactName}'.`);

  return {
    status: "success",
    analysis_artifact: newArtifactName,
  };
}
