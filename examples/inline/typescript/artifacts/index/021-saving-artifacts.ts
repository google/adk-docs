import {Context} from '@google/adk';
import {createPartFromBase64, type Part} from '@google/genai';

async function saveGeneratedReport(context: Context, reportBytes: Uint8Array): Promise<void> {
  /** Saves generated PDF report bytes as an artifact. */
  const reportArtifact: Part = createPartFromBase64(
    Buffer.from(reportBytes).toString('base64'),
    'application/pdf',
  );

  const filename = 'generated_report.pdf';

  try {
    const version = await context.saveArtifact(filename, reportArtifact);
    console.log(`Successfully saved TypeScript artifact '${filename}' as version ${version}.`);
  } catch (e: any) {
    console.error(
      `Error saving TypeScript artifact: ${e.message}. Is ArtifactService configured in Runner?`,
    );
  }
}