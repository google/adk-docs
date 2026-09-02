import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.Collections;
import java.util.List;
import java.util.Map;

// Import the plugin.
// import com.example.CountInvocationPlugin;

public class Main {

  public static class HelloTool {
    @Schema(name = "hello_world", description = "Prints hello world with user query.")
    public static Map<String, Object> helloWorld(
        @Schema(name = "query", description = "The query string to print.") String query) {
      String output = "Hello world: query is [" + query + "]";
      System.out.println(output);
      return Map.of("result", output);
    }
  }

  public static void main(String[] args) {
    LlmAgent rootAgent = LlmAgent.builder()
        .model("gemini-flash-latest")
        .name("hello_world")
        .description("Prints hello world with user query.")
        .instruction("Use hello_world tool to print hello world and user query.")
        .tools(FunctionTool.create(HelloTool.class, "helloWorld"))
        .build();

    // Add your plugin here. You can add multiple plugins.
    InMemoryRunner runner = new InMemoryRunner(
        rootAgent,
        "test_app_with_plugin",
        Collections.singletonList(new CountInvocationPlugin())
    );

    // The rest is the same as starting a regular ADK runner.
    Session session = runner.sessionService().createSession(
        "test_app_with_plugin",
        "user"
    ).blockingGet();

    String prompt = "hello world";
    Content newContent = Content.builder()
        .role("user")
        .parts(List.of(Part.builder().text(prompt).build()))
        .build();

    runner.runAsync(
        "user",
        session.id(),
        newContent
    ).blockingForEach(event -> {
         if (event.author() != null) {
            System.out.println("** Got event from " + event.author());
        }
    });
  }
}