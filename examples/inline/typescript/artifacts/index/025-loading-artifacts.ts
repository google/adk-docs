import {Context} from '@google/adk';

async function processLatestReport(context: Context): Promise<void> {
  /** Loads the latest report artifact and processes its data. */
  const filename = 'generated_report.pdf';
  try {
    // Load the latest version
    const reportArtifact = await context.loadArtifact(filename);

    if (reportArtifact?.inlineData) {
      console.log(`Successfully loaded latest TypeScript artifact '${filename}'.`);
      console.log(`MIME Type: ${reportArtifact.inlineData.mimeType}`);
      // Process the reportArtifact.inlineData.data (base64 string)
      const pdfData = Buffer.from(reportArtifact.inlineData.data || '', 'base64');
      console.log(`Report size: ${pdfData.length} bytes.`);
      // ... further processing ...
    } else {
      console.log(`TypeScript artifact '${filename}' not found.`);
    }
  } catch (e: any) {
    console.error(
      `Error loading TypeScript artifact: ${e.message}. Is ArtifactService configured?`,
    );
  }
}