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