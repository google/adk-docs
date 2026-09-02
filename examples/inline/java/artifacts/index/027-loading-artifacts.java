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