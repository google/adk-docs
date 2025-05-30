package artifacts;

// --8<-- [start:full_code]

import com.google.adk.artifacts.BaseArtifactService;
import com.google.adk.artifacts.GcsArtifactService;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;

public class GcsServiceSetup {
  public static void main(String[] args) {
    // Specify the GCS bucket name
    String gcsBucketNameJava = "your-gcs-bucket-for-adk-artifacts"; // Replace with your bucket name

    try {
      // Initialize the GCS Storage client.
      // This will use Application Default Credentials by default.
      // Ensure the environment is configured correctly (e.g., GOOGLE_APPLICATION_CREDENTIALS).
      Storage storageClient = StorageOptions.getDefaultInstance().getService();

      // Instantiate the GcsArtifactService
      BaseArtifactService gcsServiceJava =
          new GcsArtifactService(gcsBucketNameJava, storageClient);

      System.out.println(
          "Java GcsArtifactService initialized for bucket: " + gcsBucketNameJava);

      // This instance would then be provided to your Runner.
      // Runner runner = new Runner(
      //     /* other services */,
      //     gcsServiceJava
      // );

    } catch (Exception e) {
      // Catch potential errors during GCS client initialization (e.g., auth, permissions)
      System.err.println("Error initializing Java GcsArtifactService: " + e.getMessage());
      e.printStackTrace();
      // Handle the error appropriately
    }
  }
}

// --8<-- [end:full_code]