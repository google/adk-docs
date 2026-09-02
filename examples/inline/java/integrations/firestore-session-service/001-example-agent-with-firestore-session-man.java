import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.runner.FirestoreDatabaseRunner;
import com.google.cloud.firestore.Firestore;
import com.google.cloud.firestore.FirestoreOptions;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Map;
import com.google.adk.sessions.FirestoreSessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import com.google.adk.events.Event;
import java.util.Scanner;
import static java.nio.charset.StandardCharsets.UTF_8;

public class YourAgentApplication {

    public static void main(String[] args) {
        System.out.println("Starting YourAgentApplication...");

        RunConfig runConfig = RunConfig.builder().build();
        String appName = "hello-time-agent";

        BaseAgent timeAgent = initAgent();

        // Initialize Firestore
        FirestoreOptions firestoreOptions = FirestoreOptions.getDefaultInstance();
        Firestore firestore = firestoreOptions.getService();

        // Use FirestoreDatabaseRunner to persist session state
        FirestoreDatabaseRunner runner = new FirestoreDatabaseRunner(
                timeAgent,
                appName,
                firestore
        );

        // Create a new session or load an existing one
        Session session = new FirestoreSessionService(firestore)
                .createSession(appName, "user1234", null, "12345")
                .blockingGet();

        // Start interactive CLI
        try (Scanner scanner = new Scanner(System.in, UTF_8)) {
            while (true) {
                System.out.print("\\nYou > ");
                String userInput = scanner.nextLine();
                if ("quit".equalsIgnoreCase(userInput)) {
                    break;
                }

                Content userMsg = Content.fromParts(Part.fromText(userInput));
                Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg, runConfig);

                System.out.print("\\nAgent > ");
                events.blockingForEach(event -> {
                    if (event.finalResponse()) {
                        System.out.println(event.stringifyContent());
                    }
                });
            }
        }
    }

    /** Mock tool implementation */
    @Schema(description = "Get the current time for a given city")
    public static Map<String, String> getCurrentTime(
        @Schema(name = "city", description = "Name of the city to get the time for") String city) {
        return Map.of(
            "city", city,
            "time", "The time is 10:30am."
        );
    }

    private static BaseAgent initAgent() {
        return LlmAgent.builder()
            .name("hello-time-agent")
            .description("Tells the current time in a specified city")
            .instruction(\"""
                You are a helpful assistant that tells the current time in a city.
                Use the 'getCurrentTime' tool for this purpose.
                \""")
            .model("gemini-flash-latest")
            .tools(FunctionTool.create(YourAgentApplication.class, "getCurrentTime"))
            .build();
    }
}