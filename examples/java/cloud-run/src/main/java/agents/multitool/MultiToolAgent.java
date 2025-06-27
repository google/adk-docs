// --8<-- [start:full_code]

package agents.multitool;

import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.Scanner;

public class MultiToolAgent {

    private static String USER_ID = "student";
    private static String NAME = "multi_tool_agent";

    // The run your agent with Dev UI, the ROOT_AGENT should be a global public static variable.
    public static BaseAgent ROOT_AGENT = initAgent();

    public static BaseAgent initAgent() {
        return LlmAgent.builder()
            .name(NAME)
            .model("gemini-2.0-flash")
            .description("Agent to answer questions about the time and weather in a city.")
            .instruction(
                "You are a helpful agent who can answer user questions about the time and weather"
                    + " in a city.")
            .tools(
                FunctionTool.create(MultiToolAgent.class, "getCurrentTime"),
                FunctionTool.create(MultiToolAgent.class, "getWeather"))
            .build();
    }

    public static Map<String, String> getCurrentTime(
        @Schema(name = "city",
                description = "The name of the city for which to retrieve the current time")
        String city) {
        String normalizedCity =
            Normalizer.normalize(city, Normalizer.Form.NFD)
                .trim()
                .toLowerCase()
                .replaceAll("(\\p{IsM}+|\\p{IsP}+)", "")
                .replaceAll("\\s+", "_");

        return ZoneId.getAvailableZoneIds().stream()
            .filter(zid -> zid.toLowerCase().endsWith("/" + normalizedCity))
            .findFirst()
            .map(
                zid ->
                    Map.of(
                        "status",
                        "success",
                        "report",
                        "The current time in "
                            + city
                            + " is "
                            + ZonedDateTime.now(ZoneId.of(zid))
                            .format(DateTimeFormatter.ofPattern("HH:mm"))
                            + "."))
            .orElse(
                Map.of(
                    "status",
                    "error",
                    "report",
                    "Sorry, I don't have timezone information for " + city + "."));
    }

    public static Map<String, String> getWeather(
        @Schema(name = "city",
                description = "The name of the city for which to retrieve the weather report")
        String city) {
        if (city.toLowerCase().equals("new york")) {
            return Map.of(
                "status",
                "success",
                "report",
                "The weather in New York is sunny with a temperature of 25 degrees Celsius (77 degrees"
                    + " Fahrenheit).");

        } else {
            return Map.of(
                "status", "error", "report", "Weather information for " + city + " is not available.");
        }
    }

    public static void main(String[] args) throws Exception {
        InMemoryRunner runner = new InMemoryRunner(ROOT_AGENT);

        Session session =
            runner
                .sessionService()
                .createSession(NAME, USER_ID)
                .blockingGet();

        try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
            while (true) {
                System.out.print("\nYou > ");
                String userInput = scanner.nextLine();

                if ("quit".equalsIgnoreCase(userInput)) {
                    break;
                }

                Content userMsg = Content.fromParts(Part.fromText(userInput));
                Flowable<Event> events = runner.runAsync(USER_ID, session.id(), userMsg);

                System.out.print("\nAgent > ");
                events.blockingForEach(event -> System.out.println(event.stringifyContent()));
            }
        }
    }
}
// --8<-- [end:full_code]
