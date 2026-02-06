# Core Concepts

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Understanding artifacts involves grasping a few key components: the service that manages them, the data structure used to hold them, and how they are identified and versioned.

## Artifact Service (`BaseArtifactService`)

* **Role:** The central component responsible for the actual storage and retrieval logic for artifacts. It defines *how* and *where* artifacts are persisted.

* **Interface:** Defined by the abstract base class `BaseArtifactService`. Any concrete implementation must provide methods for:

    * `Save Artifact`: Stores the artifact data and returns its assigned version number.
    * `Load Artifact`: Retrieves a specific version (or the latest) of an artifact.
    * `List Artifact keys`: Lists the unique filenames of artifacts within a given scope.
    * `Delete Artifact`: Removes an artifact (and potentially all its versions, depending on implementation).
    * `List versions`: Lists all available version numbers for a specific artifact filename.

* **Configuration:** You provide an instance of an artifact service (e.g., `InMemoryArtifactService`, `GcsArtifactService`) when initializing the `Runner`. The `Runner` then makes this service available to agents and tools via the `InvocationContext`.

=== "Python"

    ```py
    from google.adk.runners import Runner
    from google.adk.artifacts import InMemoryArtifactService # Or GcsArtifactService
    from google.adk.agents import LlmAgent # Any agent
    from google.adk.sessions import InMemorySessionService

    # Example: Configuring the Runner with an Artifact Service
    my_agent = LlmAgent(name="artifact_user_agent", model="gemini-2.0-flash")
    artifact_service = InMemoryArtifactService() # Choose an implementation
    session_service = InMemorySessionService()

    runner = Runner(
        agent=my_agent,
        app_name="my_artifact_app",
        session_service=session_service,
        artifact_service=artifact_service # Provide the service instance here
    )
    # Now, contexts within runs managed by this runner can use artifact methods
    ```

=== "Typescript"

    ```typescript
    import { InMemoryRunner } from '@google/adk';
    import { LlmAgent } from '@google/adk';
    import { InMemoryArtifactService } from '@google/adk';

    // Example: Configuring the Runner with an Artifact Service
    const myAgent = new LlmAgent({name: "artifact_user_agent", model: "gemini-2.5-flash"});
    const artifactService = new InMemoryArtifactService(); // Choose an implementation
    const sessionService = new InMemoryArtifactService();

    const runner = new InMemoryRunner({
        agent: myAgent,
        appName: "my_artifact_app",
        sessionService: sessionService,
        artifactService: artifactService, // Provide the service instance here
    });
    // Now, contexts within runs managed by this runner can use artifact methods
    ```

=== "Go"

    ```go
    import (
      "context"
      "log"

      "google.golang.org/adk/agent/llmagent"
      "google.golang.org/adk/artifactservice"
      "google.golang.org/adk/llm/gemini"
      "google.golang.org/adk/runner"
      "google.golang.org/adk/sessionservice"
      "google.golang.org/genai"
	)

	--8<-- "examples/go/snippets/artifacts/main.go:configure-runner"
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.runner.Runner;
    import com.google.adk.sessions.InMemorySessionService;
    import com.google.adk.artifacts.InMemoryArtifactService;

    // Example: Configuring the Runner with an Artifact Service
    LlmAgent myAgent =  LlmAgent.builder()
      .name("artifact_user_agent")
      .model("gemini-2.0-flash")
      .build();
    InMemoryArtifactService artifactService = new InMemoryArtifactService(); // Choose an implementation
    InMemorySessionService sessionService = new InMemorySessionService();

    Runner runner = new Runner(myAgent, "my_artifact_app", artifactService, sessionService); // Provide the service instance here
    // Now, contexts within runs managed by this runner can use artifact methods
    ```

## Artifact Data

* **Standard Representation:** Artifact content is universally represented using the `google.genai.types.Part` object, the same structure used for parts of LLM messages.

* **Key Attribute (`inline_data`):** For artifacts, the most relevant attribute is `inline_data`, which is a `google.genai.types.Blob` object containing:

    * `data` (`bytes`): The raw binary content of the artifact.
    * `mime_type` (`str`): A standard MIME type string (e.g., `'application/pdf'`, `'image/png'`, `'audio/mpeg'`) describing the nature of the binary data. **This is crucial for correct interpretation when loading the artifact.**

=== "Python"

    ```python
    import google.genai.types as types

    # Example: Creating an artifact Part from raw bytes
    pdf_bytes = b'%PDF-1.4...' # Your raw PDF data
    pdf_mime_type = "application/pdf"

    # Using the constructor
    pdf_artifact_py = types.Part(
        inline_data=types.Blob(data=pdf_bytes, mime_type=pdf_mime_type)
    )

    # Using the convenience class method (equivalent)
    pdf_artifact_alt_py = types.Part.from_bytes(data=pdf_bytes, mime_type=pdf_mime_type)

    print(f"Created Python artifact with MIME type: {pdf_artifact_py.inline_data.mime_type}")
    ```

=== "Typescript"

    ```typescript
    import type { Part } from '@google/genai';
    import { createPartFromBase64 } from '@google/genai';

    // Example: Creating an artifact Part from raw bytes
    const pdfBytes = new Uint8Array([0x25, 0x50, 0x44, 0x46, 0x2d, 0x31, 0x2e, 0x34]); // Your raw PDF data
    const pdfMimeType = "application/pdf";

    const pdfArtifact: Part = createPartFromBase64(pdfBytes.toString('base64'), pdfMimeType);
    console.log(`Created TypeScript artifact with MIME Type: ${pdfArtifact.inlineData?.mimeType}`);
    ```

=== "Go"

    ```go
    import (
      "log"
      "os"

      "google.golang.org/genai"
    )

    --8<-- "examples/go/snippets/artifacts/main.go:artifact-data"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/artifacts/ArtifactDataExample.java:full_code"
    ```

## Filename

* **Identifier:** A simple string used to name and retrieve an artifact within its specific namespace.
* **Uniqueness:** Filenames must be unique within their scope (either the session or the user namespace).
* **Best Practice:** Use descriptive names, potentially including file extensions (e.g., `"monthly_report.pdf"`, `"user_avatar.jpg"`), although the extension itself doesn't dictate behavior – the `mime_type` does.

## Versioning

* **Automatic Versioning:** The artifact service automatically handles versioning. When you call `save_artifact`, the service determines the next available version number (typically starting from 0 and incrementing) for that specific filename and scope.
* **Returned by `save_artifact`:** The `save_artifact` method returns the integer version number that was assigned to the newly saved artifact.
* **Retrieval:**
  * `load_artifact(..., version=None)` (default): Retrieves the *latest* available version of the artifact.
  * `load_artifact(..., version=N)`: Retrieves the specific version `N`.
* **Listing Versions:** The `list_versions` method (on the service, not context) can be used to find all existing version numbers for an artifact.

## Namespacing (Session vs. User)

* **Concept:** Artifacts can be scoped either to a specific session or more broadly to a user across all their sessions within the application. This scoping is determined by the `filename` format and handled internally by the `ArtifactService`.

* **Default (Session Scope):** If you use a plain filename like `"report.pdf"`, the artifact is associated with the specific `app_name`, `user_id`, *and* `session_id`. It's only accessible within that exact session context.


* **User Scope (`"user:"` prefix):** If you prefix the filename with `"user:"`, like `"user:profile.png"`, the artifact is associated only with the `app_name` and `user_id`. It can be accessed or updated from *any* session belonging to that user within the app.


=== "Python"

    ```python
    # Example illustrating namespace difference (conceptual)

    # Session-specific artifact filename
    session_report_filename = "summary.txt"

    # User-specific artifact filename
    user_config_filename = "user:settings.json"

    # When saving 'summary.txt' via context.save_artifact,
    # it's tied to the current app_name, user_id, and session_id.

    # When saving 'user:settings.json' via context.save_artifact,
    # the ArtifactService implementation should recognize the "user:" prefix
    # and scope it to app_name and user_id, making it accessible across sessions for that user.
    ```

=== "Typescript"

    ```typescript
    // Example illustrating namespace difference (conceptual)

    // Session-specific artifact filename
    const sessionReportFilename = "summary.txt";

    // User-specific artifact filename
    const userConfigFilename = "user:settings.json";

    // When saving 'summary.txt' via context.saveArtifact, it's tied to the current appName, userId, and sessionId.
    // When saving 'user:settings.json' via context.saveArtifact, the ArtifactService implementation recognizes the "user:" prefix and scopes it to appName and userId, making it accessible across sessions for that user.
    ```

=== "Go"

    ```go
    import (
      "log"
    )

    --8<-- "examples/go/snippets/artifacts/main.go:namespacing"
    ```

=== "Java"

    ```java
    // Example illustrating namespace difference (conceptual)

    // Session-specific artifact filename
    String sessionReportFilename = "summary.txt";

    // User-specific artifact filename
    String userConfigFilename = "user:settings.json"; // The "user:" prefix is key

    // When saving 'summary.txt' via context.save_artifact,
    // it's tied to the current app_name, user_id, and session_id.
    // artifactService.saveArtifact(appName, userId, sessionId1, sessionReportFilename, someData);

    // When saving 'user:settings.json' via context.save_artifact,
    // the ArtifactService implementation should recognize the "user:" prefix
    // and scope it to app_name and user_id, making it accessible across sessions for that user.
    // artifactService.saveArtifact(appName, userId, sessionId1, userConfigFilename, someData);
    ```

These core concepts work together to provide a flexible system for managing binary data within the ADK framework.

