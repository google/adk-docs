import com.google.genai.types.Part;
import java.nio.charset.StandardCharsets;

public class ArtifactExample {
    public static void main(String[] args) {
        // Assume 'imageBytes' contains the binary data of a PNG image
        byte[] imageBytes = {(byte) 0x89, (byte) 0x50, (byte) 0x4E, (byte) 0x47, (byte) 0x0D, (byte) 0x0A, (byte) 0x1A, (byte) 0x0A, (byte) 0x01, (byte) 0x02}; // Placeholder for actual image bytes

        // Create an image artifact using Part.fromBytes
        Part imageArtifact = Part.fromBytes(imageBytes, "image/png");

        System.out.println("Artifact MIME Type: " + imageArtifact.inlineData().get().mimeType().get());
        System.out.println(
            "Artifact Data (first 10 bytes): "
                + new String(imageArtifact.inlineData().get().data().get(), 0, 10, StandardCharsets.UTF_8)
                + "...");
    }
}