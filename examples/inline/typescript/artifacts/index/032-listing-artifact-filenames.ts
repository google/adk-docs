import {Context} from '@google/adk';

async function listUserFiles(context: Context): Promise<string> {
  /** Tool to list available artifacts for the user. */
  try {
    const availableFiles = await context.listArtifacts();
    if (!availableFiles || availableFiles.length === 0) {
      return 'You have no saved artifacts.';
    } else {
      // Format the list for the user/LLM
      const fileListStr = availableFiles.map((fname) => `- ${fname}`).join('\n');
      return `Here are your available TypeScript artifacts:\n${fileListStr}`;
    }
  } catch (e: any) {
    console.error(
      `Error listing TypeScript artifacts: ${e.message}. Is ArtifactService configured?`,
    );
    return 'Error: Could not list TypeScript artifacts.';
  }
}