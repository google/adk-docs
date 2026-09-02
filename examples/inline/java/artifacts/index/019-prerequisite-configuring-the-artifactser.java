import com.google.adk.agents.LlmAgent;
import com.google.adk.artifacts.InMemoryArtifactService; // Or GcsArtifactService
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;

public class SampleArtifactAgent {

  public static void main(String[] args) {

    // Your agent definition
    LlmAgent agent = LlmAgent.builder()
        .name("my_agent")
        .model("gemini-flash-latest")
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