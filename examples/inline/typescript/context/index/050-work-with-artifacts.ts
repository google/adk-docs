// Pseudocode: In a tool function
import { Context } from '@google/adk';

async function checkAvailableDocs(context: Context): Promise<Record<string, string[] | string>> {
  try {
    const artifactKeys = await context.listArtifacts();
    console.log(`Available artifacts: ${artifactKeys}`);
    return { available_docs: artifactKeys };
  } catch (e) {
    return { error: `Artifact service error: ${e}` };
  }
}