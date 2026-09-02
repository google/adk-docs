import {createPartFromBase64, type Part} from '@google/genai';

// Example: Creating an artifact Part from raw bytes.
const pdfBytes = new Uint8Array([0x25, 0x50, 0x44, 0x46, 0x2d, 0x31, 0x2e, 0x34]);
const pdfMimeType = 'application/pdf';

// Using Buffer.from(bytes).toString('base64') for Node.js environments.
const pdfArtifact: Part = createPartFromBase64(
  Buffer.from(pdfBytes).toString('base64'),
  pdfMimeType,
);
console.log(`Created TypeScript artifact with MIME Type: ${pdfArtifact.inlineData?.mimeType}`);