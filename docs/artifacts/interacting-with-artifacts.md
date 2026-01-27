# Interacting with Artifacts (via Context Objects)

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

The primary way you interact with artifacts within your agent's logic (specifically within callbacks or tools) is through methods provided by the `CallbackContext` and `ToolContext` objects. These methods abstract away the underlying storage details managed by the `ArtifactService`.

## Prerequisite: Configuring the `ArtifactService`

Before you can use any artifact methods via the context objects, you **must** provide an instance of a [`BaseArtifactService` implementation](#available-implementations) (like [`InMemoryArtifactService`](#inmemoryartifactservice) or [`GcsArtifactService`](#gcsartifactservice)) when initializing your `Runner`.

=== "Python"

    In Python, you provide this instance when initializing your `Runner`.

    ```python
    from google.adk.runners import Runner
    from google.adk.artifacts import InMemoryArtifactService # Or GcsArtifactService
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService

    # Your agent definition
    agent = LlmAgent(name="my_agent", model="gemini-2.0-flash")

    # Instantiate the desired artifact service
    artifact_service = InMemoryArtifactService()

    # Provide it to the Runner
    runner = Runner(
        agent=agent,
        app_name="artifact_app",
        session_service=InMemorySessionService(),
        artifact_service=artifact_service # Service must be provided here
    )
    ```
    If no `artifact_service` is configured in the `InvocationContext` (which happens if it's not passed to the `Runner`), calling `save_artifact`, `load_artifact`, or `list_artifacts` on the context objects will raise a `ValueError`.

=== "Typescript"

    ```typescript
    import { LlmAgent, InMemoryRunner, InMemoryArtifactService } from '@google/adk';

    // Your agent definition
    const agent = new LlmAgent({name: "my_agent", model: "gemini-2.5-flash"});

    // Instantiate the desired artifact service
    const artifactService = new InMemoryArtifactService();

    // Provide it to the Runner
    const runner = new InMemoryRunner({
        agent: agent,
        appName: "artifact_app",
        sessionService: new InMemoryArtifactService(),
        artifactService: artifactService, // Service must be provided here
    });
    // If no artifactService is configured, calling artifact methods on context objects will throw an error.
    ```
    In Java, if an `ArtifactService` instance is not available (e.g., `null`) when artifact operations are attempted, it would typically result in a `NullPointerException` or a custom error, depending on how your application is structured. Robust applications often use dependency injection frameworks to manage service lifecycles and ensure availability.

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

    --8<-- "examples/go/snippets/artifacts/main.go:prerequisite"
    ```

=== "Java"

    In Java, you would instantiate a `BaseArtifactService` implementation and then ensure it's accessible to the parts of your application that manage artifacts. This is often done through dependency injection or by explicitly passing the service instance.

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.artifacts.InMemoryArtifactService; // Or GcsArtifactService
    import com.google.adk.runner.Runner;
    import com.google.adk.sessions.InMemorySessionService;

    public class SampleArtifactAgent {

      public static void main(String[] args) {

        // Your agent definition
        LlmAgent agent = LlmAgent.builder()
            .name("my_agent")
            .model("gemini-2.0-flash")
            .build();

        // Instantiate the desired artifact service
        InMemoryArtifactService artifactService = new InMemoryArtifactService();

        // Provide it to the Runner
        Runner runner = new Runner(agent,
            "APP_NAME",
            artifactService, // Service must be provided here
            new InMemorySessionService());

      }
    }
    ```

## Accessing Methods

The artifact interaction methods are available directly on instances of `CallbackContext` (passed to agent and model callbacks) and `ToolContext` (passed to tool callbacks). Remember that `ToolContext` inherits from `CallbackContext`.

### Saving Artifacts

*   **Code Example:**

    === "Python"

        ```python
        import google.genai.types as types
        from google.adk.agents.callback_context import CallbackContext # Or ToolContext

        async def save_generated_report_py(context: CallbackContext, report_bytes: bytes):
            """Saves generated PDF report bytes as an artifact."""
            report_artifact = types.Part.from_bytes(
                data=report_bytes,
                mime_type="application/pdf"
            )
            filename = "generated_report.pdf"

            try:
                version = await context.save_artifact(filename=filename, artifact=report_artifact)
                print(f"Successfully saved Python artifact '{filename}' as version {version}.")
                # The event generated after this callback will contain:
                # event.actions.artifact_delta == {"generated_report.pdf": version}
            except ValueError as e:
                print(f"Error saving Python artifact: {e}. Is ArtifactService configured in Runner?")
            except Exception as e:
                # Handle potential storage errors (e.g., GCS permissions)
                print(f"An unexpected error occurred during Python artifact save: {e}")

        # --- Example Usage Concept (Python) ---
        # async def main_py():
        #   callback_context: CallbackContext = ... # obtain context
        #   report_data = b'...' # Assume this holds the PDF bytes
        #   await save_generated_report_py(callback_context, report_data)
        ```

    === "Typescript"

        ```typescript
        import type { Part } from '@google/genai';
        import { createPartFromBase64 } from '@google/genai';
        import { CallbackContext } from '@google/adk';

        async function saveGeneratedReport(context: CallbackContext, reportBytes: Uint8Array): Promise<void> {
            /**Saves generated PDF report bytes as an artifact.*/
            const reportArtifact: Part = createPartFromBase64(reportBytes.toString('base64'), "application/pdf");

            const filename = "generated_report.pdf";

            try {
                const version = await context.saveArtifact(filename, reportArtifact);
                console.log(`Successfully saved TypeScript artifact '${filename}' as version ${version}.`);
            } catch (e: any) {
                console.error(`Error saving TypeScript artifact: ${e.message}. Is ArtifactService configured in Runner?`);
            }
        }
        ```
    === "Go"

        ```go
        import (
          "log"

          "google.golang.org/adk/agent"
          "google.golang.org/adk/llm"
          "google.golang.org/genai"
        )

        --8<-- "examples/go/snippets/artifacts/main.go:saving-artifacts"
        ```

    === "Java"

        ```java
        import com.google.adk.agents.CallbackContext;
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.InMemoryArtifactService;
        import com.google.genai.types.Part;
        import java.nio.charset.StandardCharsets;

        public class SaveArtifactExample {

        public void saveGeneratedReport(CallbackContext callbackContext, byte[] reportBytes) {
        // Saves generated PDF report bytes as an artifact.
        Part reportArtifact = Part.fromBytes(reportBytes, "application/pdf");
        String filename = "generatedReport.pdf";

            callbackContext.saveArtifact(filename, reportArtifact);
            System.out.println("Successfully saved Java artifact '" + filename);
            // The event generated after this callback will contain:
            // event().actions().artifactDelta == {"generated_report.pdf": version}
        }

        // --- Example Usage Concept (Java) ---
        public static void main(String[] args) {
            BaseArtifactService service = new InMemoryArtifactService(); // Or GcsArtifactService
            SaveArtifactExample myTool = new SaveArtifactExample();
            byte[] reportData = "...".getBytes(StandardCharsets.UTF_8); // PDF bytes
            CallbackContext callbackContext; // ... obtain callback context from your app
            myTool.saveGeneratedReport(callbackContext, reportData);
            // Due to async nature, in a real app, ensure program waits or handles completion.
          }
        }
        ```

### Loading Artifacts

*   **Code Example:**

    === "Python"

        ```python
        import google.genai.types as types
        from google.adk.agents.callback_context import CallbackContext # Or ToolContext

        async def process_latest_report_py(context: CallbackContext):
            """Loads the latest report artifact and processes its data."""
            filename = "generated_report.pdf"
            try:
                # Load the latest version
                report_artifact = await context.load_artifact(filename=filename)

                if report_artifact and report_artifact.inline_data:
                    print(f"Successfully loaded latest Python artifact '{filename}'.")
                    print(f"MIME Type: {report_artifact.inline_data.mime_type}")
                    # Process the report_artifact.inline_data.data (bytes)
                    pdf_bytes = report_artifact.inline_data.data
                    print(f"Report size: {len(pdf_bytes)} bytes.")
                    # ... further processing ...
                else:
                    print(f"Python artifact '{filename}' not found.")

                # Example: Load a specific version (if version 0 exists)
                # specific_version_artifact = await context.load_artifact(filename=filename, version=0)
                # if specific_version_artifact:
                #     print(f"Loaded version 0 of '{filename}'.")

            except ValueError as e:
                print(f"Error loading Python artifact: {e}. Is ArtifactService configured?")
            except Exception as e:
                # Handle potential storage errors
                print(f"An unexpected error occurred during Python artifact load: {e}")

        # --- Example Usage Concept (Python) ---
        # async def main_py():
        #   callback_context: CallbackContext = ... # obtain context
        #   await process_latest_report_py(callback_context)
        ```

    === "Typescript"

        ```typescript
        import { CallbackContext } from '@google/adk';

        async function processLatestReport(context: CallbackContext): Promise<void> {
            /**Loads the latest report artifact and processes its data.*/
            const filename = "generated_report.pdf";
            try {
                // Load the latest version
                const reportArtifact = await context.loadArtifact(filename);

                if (reportArtifact?.inlineData) {
                    console.log(`Successfully loaded latest TypeScript artifact '${filename}'.`);
                    console.log(`MIME Type: ${reportArtifact.inlineData.mimeType}`);
                    // Process the reportArtifact.inlineData.data (base64 string)
                    const pdfData = Buffer.from(reportArtifact.inlineData.data, 'base64');
                    console.log(`Report size: ${pdfData.length} bytes.`);
                    // ... further processing ...
                } else {
                    console.log(`TypeScript artifact '${filename}' not found.`);
                }

            } catch (e: any) {
                console.error(`Error loading TypeScript artifact: ${e.message}. Is ArtifactService configured?`);
            }
        }
        ```

    === "Go"

        ```go
        import (
          "log"

          "google.golang.org/adk/agent"
          "google.golang.org/adk/llm"
        )

        --8<-- "examples/go/snippets/artifacts/main.go:loading-artifacts"
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.genai.types.Part;
        import io.reactivex.rxjava3.core.MaybeObserver;
        import io.reactivex.rxjava3.disposables.Disposable;
        import java.util.Optional;

        public class MyArtifactLoaderService {

            private final BaseArtifactService artifactService;
            private final String appName;

            public MyArtifactLoaderService(BaseArtifactService artifactService, String appName) {
                this.artifactService = artifactService;
                this.appName = appName;
            }

            public void processLatestReportJava(String userId, String sessionId, String filename) {
                // Load the latest version by passing Optional.empty() for the version
                artifactService
                        .loadArtifact(appName, userId, sessionId, filename, Optional.empty())
                        .subscribe(
                                new MaybeObserver<Part>() {
                                    @Override
                                    public void onSubscribe(Disposable d) {
                                        // Optional: handle subscription
                                    }

                                    @Override
                                    public void onSuccess(Part reportArtifact) {
                                        System.out.println(
                                                "Successfully loaded latest Java artifact '" + filename + "'.");
                                        reportArtifact
                                                .inlineData()
                                                .ifPresent(
                                                        blob -> {
                                                            System.out.println(
                                                                    "MIME Type: " + blob.mimeType().orElse("N/A"));
                                                            byte[] pdfBytes = blob.data().orElse(new byte[0]);
                                                            System.out.println("Report size: " + pdfBytes.length + " bytes.");
                                                            // ... further processing of pdfBytes ...
                                                        });
                                    }

                                    @Override
                                    public void onError(Throwable e) {
                                        // Handle potential storage errors or other exceptions
                                        System.err.println(
                                                "An error occurred during Java artifact load for '"
                                                        + filename
                                                        + "': "
                                                        + e.getMessage());
                                    }

                                    @Override
                                    public void onComplete() {
                                        // Called if the artifact (latest version) is not found
                                        System.out.println("Java artifact '" + filename + "' not found.");
                                    }
                                });

                // Example: Load a specific version (e.g., version 0)
                /*
                artifactService.loadArtifact(appName, userId, sessionId, filename, Optional.of(0))
                    .subscribe(part -> {
                        System.out.println("Loaded version 0 of Java artifact '" + filename + "'.");
                    }, throwable -> {
                        System.err.println("Error loading version 0 of '" + filename + "': " + throwable.getMessage());
                    }, () -> {
                        System.out.println("Version 0 of Java artifact '" + filename + "' not found.");
                    });
                */
            }

            // --- Example Usage Concept (Java) ---
            public static void main(String[] args) {
                // BaseArtifactService service = new InMemoryArtifactService(); // Or GcsArtifactService
                // MyArtifactLoaderService loader = new MyArtifactLoaderService(service, "myJavaApp");
                // loader.processLatestReportJava("user123", "sessionABC", "java_report.pdf");
                // Due to async nature, in a real app, ensure program waits or handles completion.
            }
        }
        ```

### Listing Artifact Filenames

*   **Code Example:**

    === "Python"

        ```python
        from google.adk.tools.tool_context import ToolContext

        def list_user_files_py(tool_context: ToolContext) -> str:
            """Tool to list available artifacts for the user."""
            try:
                available_files = await tool_context.list_artifacts()
                if not available_files:
                    return "You have no saved artifacts."
                else:
                    # Format the list for the user/LLM
                    file_list_str = "\n".join([f"- {fname}" for fname in available_files])
                    return f"Here are your available Python artifacts:\n{file_list_str}"
            except ValueError as e:
                print(f"Error listing Python artifacts: {e}. Is ArtifactService configured?")
                return "Error: Could not list Python artifacts."
            except Exception as e:
                print(f"An unexpected error occurred during Python artifact list: {e}")
                return "Error: An unexpected error occurred while listing Python artifacts."

        # This function would typically be wrapped in a FunctionTool
        # from google.adk.tools import FunctionTool
        # list_files_tool = FunctionTool(func=list_user_files_py)
        ```

    === "Typescript"

        ```typescript
        import { ToolContext } from '@google/adk';

        async function listUserFiles(toolContext: ToolContext): Promise<string> {
            /**Tool to list available artifacts for the user.*/
            try {
                const availableFiles = await toolContext.listArtifacts();
                if (!availableFiles || availableFiles.length === 0) {
                    return "You have no saved artifacts.";
                } else {
                    // Format the list for the user/LLM
                    const fileListStr = availableFiles.map(fname => `- ${fname}`).join("\n");
                    return `Here are your available TypeScript artifacts:\n${fileListStr}`;
                }
            } catch (e: any) {
                console.error(`Error listing TypeScript artifacts: ${e.message}. Is ArtifactService configured?`);
                return "Error: Could not list TypeScript artifacts.";
            }
        }
        ```

    === "Go"

        ```go
        import (
          "fmt"
          "log"
          "strings"

          "google.golang.org/adk/agent"
          "google.golang.org/adk/llm"
          "google.golang.org/genai"
        )

        --8<-- "examples/go/snippets/artifacts/main.go:listing-artifacts"
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.ListArtifactsResponse;
        import com.google.common.collect.ImmutableList;
        import io.reactivex.rxjava3.core.SingleObserver;
        import io.reactivex.rxjava3.disposables.Disposable;

        public class MyArtifactListerService {

            private final BaseArtifactService artifactService;
            private final String appName;

            public MyArtifactListerService(BaseArtifactService artifactService, String appName) {
                this.artifactService = artifactService;
                this.appName = appName;
            }

            // Example method that might be called by a tool or agent logic
            public void listUserFilesJava(String userId, String sessionId) {
                artifactService
                        .listArtifactKeys(appName, userId, sessionId)
                        .subscribe(
                                new SingleObserver<ListArtifactsResponse>() {
                                    @Override
                                    public void onSubscribe(Disposable d) {
                                        // Optional: handle subscription
                                    }

                                    @Override
                                    public void onSuccess(ListArtifactsResponse response) {
                                        ImmutableList<String> availableFiles = response.filenames();
                                        if (availableFiles.isEmpty()) {
                                            System.out.println(
                                                    "User "
                                                            + userId
                                                            + " in session "
                                                            + sessionId
                                                            + " has no saved Java artifacts.");
                                        } else {
                                            StringBuilder fileListStr =
                                                    new StringBuilder(
                                                            "Here are the available Java artifacts for user "
                                                                    + userId
                                                                    + " in session "
                                                                    + sessionId
                                                                    + ":\n");
                                            for (String fname : availableFiles) {
                                                fileListStr.append("- ").append(fname).append("\n");
                                            }
                                            System.out.println(fileListStr.toString());
                                        }
                                    }

                                    @Override
                                    public void onError(Throwable e) {
                                        System.err.println(
                                                "Error listing Java artifacts for user "
                                                        + userId
                                                        + " in session "
                                                        + sessionId
                                                        + ": "
                                                        + e.getMessage());
                                        // In a real application, you might return an error message to the user/LLM
                                    }
                                });
            }

            // --- Example Usage Concept (Java) ---
            public static void main(String[] args) {
                // BaseArtifactService service = new InMemoryArtifactService(); // Or GcsArtifactService
                // MyArtifactListerService lister = new MyArtifactListerService(service, "myJavaApp");
                // lister.listUserFilesJava("user123", "sessionABC");
                // Due to async nature, in a real app, ensure program waits or handles completion.
            }
        }
        ```

These methods for saving, loading, and listing provide a convenient and consistent way to manage binary data persistence within ADK, whether using Python's context objects or directly interacting with the `BaseArtifactService` in Java, regardless of the chosen backend storage implementation.