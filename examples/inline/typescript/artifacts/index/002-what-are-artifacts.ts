import {createPartFromBase64, type Part} from '@google/genai';

// Assume 'imageBytes' contains the binary data of a PNG image.
const imageBytes = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

// Using Buffer.from(bytes).toString('base64') for Node.js environments.
const imageArtifact: Part = createPartFromBase64(
  Buffer.from(imageBytes).toString('base64'),
  'image/png',
);

console.log(`Artifact MIME Type: ${imageArtifact.inlineData?.mimeType}`);
// Note: Accessing raw bytes would require decoding from base64.