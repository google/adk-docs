package artifacts;

// --8<-- [start:full_code]

import com.google.genai.types.Blob;
import com.google.genai.types.Part;
import java.nio.charset.StandardCharsets;

public class ArtifactDataExample {
  public static void main(String[] args) {
    // Example: Creating an artifact Part from raw bytes
    byte[] pdfBytes = "%PDF-1.4...".getBytes(StandardCharsets.UTF_8); // Your raw PDF data
    String pdfMimeType = "application/pdf";

    // Using the Part.fromBlob() constructor with a Blob
    Blob pdfBlob = Blob.builder()
        .data(pdfBytes)
        .mimeType(pdfMimeType)
        .build();
    Part pdfArtifactJava = Part.builder().inlineData(pdfBlob).build();

    // Using the convenience static method Part.fromBytes() (equivalent)
    Part pdfArtifactAltJava = Part.fromBytes(pdfBytes, pdfMimeType);

    // Accessing mimeType, note the use of Optional
    String mimeType = pdfArtifactJava.inlineData()
        .flatMap(Blob::mimeType)
        .orElse("unknown");
    System.out.println("Created Java artifact with MIME type: " + mimeType);

    // Accessing data
    byte[] data = pdfArtifactJava.inlineData()
        .flatMap(Blob::data)
        .orElse(new byte[0]);
    System.out.println("Java artifact data (first 10 bytes): "
        + new String(data, 0, Math.min(data.length, 10), StandardCharsets.UTF_8) + "...");
  }
}
// --8<-- [end:full_code]