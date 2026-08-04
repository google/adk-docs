package sessions;

// --8<-- [start:full_example]

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.LoadMemoryTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.Optional;

public class MemoryExample {

  public static void main(String[] args) {
    String appName = "memory_example_app";
    String userId = "mem_user";
    String model = "gemini-flash-latest";

    // An agent that can recall past information using the load_memory tool.
    LlmAgent agent =
        LlmAgent.builder()
            .model(model)
            .name("MemoryAgent")
            .instruction(
                "Answer the user's question. Use the 'load_memory' tool "
                    + "if the answer might be in past conversations.")
            .tools(new LoadMemoryTool())
            .build();

    // InMemoryRunner bundles in-memory session and memory services and shares
    // them across every session it creates.
    InMemoryRunner runner = new InMemoryRunner(agent, appName);

    // --- Turn 1: capture information in one session ---
    Session captureSession =
        runner.sessionService().createSession(appName, userId).blockingGet();
    Content statement =
        Content.fromParts(Part.fromText("My favorite project is Project Alpha."));
    runner
        .runAsync(userId, captureSession.id(), statement, RunConfig.builder().build())
        .blockingSubscribe();

    // Persist the finished session to memory.
    Session completedSession =
        runner
            .sessionService()
            .getSession(appName, userId, captureSession.id(), Optional.empty())
            .blockingGet();
    runner.memoryService().addSessionToMemory(completedSession).blockingAwait();

    // --- Turn 2: recall the information in a new session ---
    Session recallSession =
        runner.sessionService().createSession(appName, userId).blockingGet();
    Content question = Content.fromParts(Part.fromText("What is my favorite project?"));
    runner
        .runAsync(userId, recallSession.id(), question, RunConfig.builder().build())
        .blockingForEach(
            (Event event) -> {
              if (event.finalResponse()) {
                event
                    .content()
                    .flatMap(Content::parts)
                    .ifPresent(
                        parts ->
                            parts.forEach(part -> part.text().ifPresent(System.out::println)));
              }
            });
  }
}
// --8<-- [end:full_example]
