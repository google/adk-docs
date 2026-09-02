import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.artifacts.InMemoryArtifactService;

// Example: Configuring the Runner with an Artifact Service
LlmAgent myAgent =  LlmAgent.builder()
  .name("artifact_user_agent")
  .model("gemini-flash-latest")
  .build();
InMemoryArtifactService artifactService = new InMemoryArtifactService(); // Choose an implementation
InMemorySessionService sessionService = new InMemorySessionService();

Runner runner = new Runner(myAgent, "my_artifact_app", artifactService, sessionService); // Provide the service instance here
// Now, contexts within runs managed by this runner can use artifact methods