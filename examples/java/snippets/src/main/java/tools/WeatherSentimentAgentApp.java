package tools;

// --8<-- [start:full_code]

import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext; // Ensure this import is correct
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

public class WeatherSentimentAgentApp {

  private static final String APP_NAME = "weather_sentiment_agent";
  private static final String USER_ID = "user1234";
  private static final String SESSION_ID = "1234";
  private static final String MODEL_ID = "gemini-2.0-flash";

  /**
   * Retrieves the current weather report for a specified city.
   *
   * @param city The city for which to retrieve the weather report.
   * @param toolContext The context for the tool.
   * @return A dictionary containing the weather information.
   */
  public static Map<String, Object> getWeatherReport(
      @Schema(name = "city")
      String city,
      @Schema(name = "toolContext")
      ToolContext toolContext) {
    Map<String, Object> response = new HashMap<>();

    if (city.toLowerCase(Locale.ROOT).equals("london")) {
      response.put("status", "success");
      response.put(
          "report",
          "The current weather in London is cloudy with a temperature of 18 degrees Celsius and a"
              + " chance of rain.");
    } else if (city.toLowerCase(Locale.ROOT).equals("paris")) {
      response.put("status", "success");
      response.put(
          "report", "The weather in Paris is sunny with a temperature of 25 degrees Celsius.");
    } else {
      response.put("status", "error");
      response.put(
          "error_message", String.format("Weather information for '%s' is not available.", city));
    }
    return response;
  }

  /**
   * Analyzes the sentiment of the given text.
   *
   * @param text The text to analyze.
   * @param toolContext The context for the tool.
   * @return A dictionary with sentiment and confidence score.
   */
  public static Map<String, Object> analyzeSentiment(
      @Schema(name = "text")
      String text,
      @Schema(name = "toolContext")
      ToolContext toolContext) {
    Map<String, Object> response = new HashMap<>();
    String lowerText = text.toLowerCase(Locale.ROOT);
    if (lowerText.contains("good") || lowerText.contains("sunny")) {
      response.put("sentiment", "positive");
      response.put("confidence", 0.8);
    } else if (lowerText.contains("rain") || lowerText.contains("bad")) {
      response.put("sentiment", "negative");
      response.put("confidence", 0.7);
    } else {
      response.put("sentiment", "neutral");
      response.put("confidence", 0.6);
    }
    return response;
  }

  /**
   * Calls the agent with the given query and prints the final response.
   *
   * @param runner The runner to use.
   * @param query The query to send to the agent.
   */
  public static void callAgent(Runner runner, String query) {
    Content content = Content.fromParts(Part.fromText(query));

    InMemorySessionService sessionService = (InMemorySessionService) runner.sessionService();
    Session session =
        sessionService
            .createSession(APP_NAME, USER_ID, /* state= */ null, SESSION_ID)
            .blockingGet();

    runner
        .runAsync(session.userId(), session.id(), content)
        .forEach(
            event -> {
              if (event.finalResponse()
                  && event.content().isPresent()
                  && event.content().get().parts().isPresent()
                  && !event.content().get().parts().get().isEmpty()
                  && event.content().get().parts().get().get(0).text().isPresent()) {
                String finalResponse = event.content().get().parts().get().get(0).text().get();
                System.out.println("Agent Response: " + finalResponse);
              }
            });
  }

  public static void main(String[] args) throws NoSuchMethodException {
    FunctionTool weatherTool =
        FunctionTool.create(
            WeatherSentimentAgentApp.class.getMethod(
                "getWeatherReport", String.class, ToolContext.class));
    FunctionTool sentimentTool =
        FunctionTool.create(
            WeatherSentimentAgentApp.class.getMethod(
                "analyzeSentiment", String.class, ToolContext.class));

    BaseAgent weatherSentimentAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("weather_sentiment_agent")
            .description("Weather Sentiment Agent")
            .instruction("""
                    You are a helpful assistant that provides weather information and analyzes the
                    sentiment of user feedback
                    **If the user asks about the weather in a specific city, use the
                    'get_weather_report' tool to retrieve the weather details.**
                    **If the 'get_weather_report' tool returns a 'success' status, provide the
                    weather report to the user.**
                    **If the 'get_weather_report' tool returns an 'error' status, inform the
                    user that the weather information for the specified city is not available
                    and ask if they have another city in mind.**
                    **After providing a weather report, if the user gives feedback on the
                    weather (e.g., 'That's good' or 'I don't like rain'), use the
                    'analyze_sentiment' tool to understand their sentiment.** Then, briefly
                    acknowledge their sentiment.
                    You can handle these tasks sequentially if needed.
                    """)
            .tools(ImmutableList.of(weatherTool, sentimentTool))
            .build();

    InMemorySessionService sessionService = new InMemorySessionService();
    Runner runner = new Runner(weatherSentimentAgent, APP_NAME, null, sessionService);

    // Change the query to ensure the tool is called with a valid city that triggers a "success"
    // response from the tool, like "london" (without the question mark).
    callAgent(runner, "weather in paris");
  }
}
// --8<-- [end:full_code]
