import com.google.adk.agents.Content;
import com.google.adk.runner.Runner;

public class AppMain {

  public static void main(String[] args) throws Exception {
    // Set a Runner using the application object

    App app = ...;

    Runner runner = Runner.builder()
        .app(app) // Use the 'app' object defined previously
        .build();

    runner.runAsync("user", "session-1", Content.fromParts(Part.fromText("Hello there!")))
        .filter(event -> event.finalResponse() && event.content().isPresent())
        .blockingSubscribe(event -> System.out.println("Response: " + event.stringifyContent()));
  }
}