# Available Implementations

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK provides concrete implementations of the `BaseArtifactService` interface, offering different storage backends suitable for various development stages and deployment needs. These implementations handle the details of storing, versioning, and retrieving artifact data based on the `app_name`, `user_id`, `session_id`, and `filename` (including the `user:` namespace prefix).

## InMemoryArtifactService

*   **Storage Mechanism:**
    *   Python: Uses a Python dictionary (`self.artifacts`) held in the application's memory. The dictionary keys represent the artifact path, and the values are lists of `types.Part`, where each list element is a version.
    *   Java: Uses nested `HashMap` instances (`private final Map<String, Map<String, Map<String, Map<String, List<Part>>>>> artifacts;`) held in memory. The keys at each level are `appName`, `userId`, `sessionId`, and `filename` respectively. The innermost `List<Part>` stores the versions of the artifact, where the list index corresponds to the version number.
*   **Key Features:**
    *   **Simplicity:** Requires no external setup or dependencies beyond the core ADK library.
    *   **Speed:** Operations are typically very fast as they involve in-memory map/dictionary lookups and list manipulations.
    *   **Ephemeral:** All stored artifacts are **lost** when the application process terminates. Data does not persist between application restarts.
*   **Use Cases:**
    *   Ideal for local development and testing where persistence is not required.
    *   Suitable for short-lived demonstrations or scenarios where artifact data is purely temporary within a single run of the application.
*   **Instantiation:**

    === "Python"

        ```python
        from google.adk.artifacts import InMemoryArtifactService

        # Simply instantiate the class
        in_memory_service_py = InMemoryArtifactService()

        # Then pass it to the Runner
        # runner = Runner(..., artifact_service=in_memory_service_py)
        ```

    === "Typescript"

        ```typescript
        import { InMemoryArtifactService } from '@google/adk';

        // Simply instantiate the class
        const inMemoryService = new InMemoryArtifactService();

        // This instance would then be provided to your Runner.
        // const runner = new InMemoryRunner({
        //     /* other services */,
        //     artifactService: inMemoryService
        // });
        ```

    === "Go"

        ```go
        import (
          "google.golang.org/adk/artifactservice"
        )

        --8<-- "examples/go/snippets/artifacts/main.go:in-memory-service"
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.InMemoryArtifactService;

        public class InMemoryServiceSetup {
            public static void main(String[] args) {
                // Simply instantiate the class
                BaseArtifactService inMemoryServiceJava = new InMemoryArtifactService();

                System.out.println("InMemoryArtifactService (Java) instantiated: " + inMemoryServiceJava.getClass().getName());

                // This instance would then be provided to your Runner.
                // Runner runner = new Runner(
                //     /* other services */,
                //     inMemoryServiceJava
                // );
            }
        }
        ```

## GcsArtifactService


*   **Storage Mechanism:** Leverages Google Cloud Storage (GCS) for persistent artifact storage. Each version of an artifact is stored as a separate object (blob) within a specified GCS bucket.
*   **Object Naming Convention:** It constructs GCS object names (blob names) using a hierarchical path structure.
*   **Key Features:**
    *   **Persistence:** Artifacts stored in GCS persist across application restarts and deployments.
    *   **Scalability:** Leverages the scalability and durability of Google Cloud Storage.
    *   **Versioning:** Explicitly stores each version as a distinct GCS object. The `saveArtifact` method in `GcsArtifactService`.
    *   **Permissions Required:** The application environment needs appropriate credentials (e.g., Application Default Credentials) and IAM permissions to read from and write to the specified GCS bucket.
*   **Use Cases:**
    *   Production environments requiring persistent artifact storage.
    *   Scenarios where artifacts need to be shared across different application instances or services (by accessing the same GCS bucket).
    *   Applications needing long-term storage and retrieval of user or session data.
*   **Instantiation:**

    === "Python"

        ```python
        from google.adk.artifacts import GcsArtifactService

        # Specify the GCS bucket name
        gcs_bucket_name_py = "your-gcs-bucket-for-adk-artifacts" # Replace with your bucket name

        try:
            gcs_service_py = GcsArtifactService(bucket_name=gcs_bucket_name_py)
            print(f"Python GcsArtifactService initialized for bucket: {gcs_bucket_name_py}")
            # Ensure your environment has credentials to access this bucket.
            # e.g., via Application Default Credentials (ADC)

            # Then pass it to the Runner
            # runner = Runner(..., artifact_service=gcs_service_py)

        except Exception as e:
            # Catch potential errors during GCS client initialization (e.g., auth issues)
            print(f"Error initializing Python GcsArtifactService: {e}")
            # Handle the error appropriately - maybe fall back to InMemory or raise
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/artifacts/GcsServiceSetup.java:full_code"
        ```

Choosing the appropriate `ArtifactService` implementation depends on your application's requirements for data persistence, scalability, and operational environment.
