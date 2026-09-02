// Pseudocode: In a callback or initial tool
import { Context } from '@google/adk';
import type { Part } from '@google/genai';

async function saveDocumentReference(context: Context, filePath: string) {
  // Assume filePath is something like "gs://my-bucket/docs/report.pdf" or "/local/path/to/report.pdf"
  try {
    // Create a Part containing the path/URI text
    const artifactPart: Part = { text: filePath };
    const version = await context.saveArtifact('document_to_summarize.txt', artifactPart);
    console.log(`Saved document reference '${filePath}' as artifact version ${version}`);
    // Store the filename in state if needed by other tools
    context.state.set('temp:doc_artifact_name', 'document_to_summarize.txt');
  } catch (e) {
    console.error(`Unexpected error saving artifact reference: ${e}`);
  }
}

// Example usage:
// saveDocumentReference(context, "gs://my-bucket/docs/report.pdf");