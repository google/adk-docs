package state;

// --8<-- [start:full_code]

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.events.Event;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.List;
import java.util.Optional;

public class GreetingAgentExample {

  public static void main(String[] args) {
    // Define agent with output_key
    LlmAgent greetingAgent =
        LlmAgent.builder()
            .name("Greeter")
            .model("gemini-2.0-flash")
            .instruction("Generate a short, friendly greeting.")
            .description("Greeting agent")
            .outputKey("last_greeting") // Save response to state['last_greeting']
            .build();

    // --- Setup Runner and Session ---
    String appName = "state_app";
    String userId = "user1";
    String sessionId = "session1";

    InMemorySessionService sessionService = new InMemorySessionService();
    Runner runner = new Runner(greetingAgent, appName, null, sessionService); // artifactService can be null if not used

    Session session =
        sessionService.createSession(appName, userId, null, sessionId).blockingGet();
    System.out.println("Initial state: " + session.state().entrySet());

    // --- Run the Agent ---
    // Runner handles calling appendEvent, which uses the output_key
    // to automatically create the stateDelta.
    Content userMessage = Content.builder().parts(List.of(Part.fromText("Hello"))).build();

    // RunConfig is needed for runner.runAsync in Java
    RunConfig runConfig = RunConfig.builder().build();

    for (Event event : runner.runAsync(userId, sessionId, userMessage, runConfig).blockingIterable()) {
      if (event.finalResponse()) {
        System.out.println("Agent responded."); // Response text is also in event.content
      }
    }

    // --- Check Updated State ---
    Session updatedSession =
        sessionService.getSession(appName, userId, sessionId, Optional.empty()).blockingGet();
    assert updatedSession != null;
    System.out.println("State after agent run: " + updatedSession.state().entrySet());
    // Expected output might include: {'last_greeting': 'Hello there! How can I help you today?'}
  }
}
// --8<-- [end:full_code]