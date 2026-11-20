package skills;

// --8<-- [start:full_example]
import com.google.adk.agents.LlmAgent;
import com.google.adk.skills.LocalSkillSource;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.skills.SkillToolset;
import java.nio.file.Path;
import java.util.Map;

public class SkillsGetStarted {

  @Schema(
      name = "get_weather",
      description = "Retrieves the current weather report for a specified city.")
  public static Map<String, Object> getWeather(
      @Schema(name = "city", description = "The city to get the weather report for.") String city) {
    return Map.of(
        "status", "success",
        "report", "The weather in " + city + " is sunny with a temperature of 25°C.");
  }

  public static LlmAgent createAgent() {
    // LocalSkillSource discovers every skill directory under the base directory.
    SkillToolset mySkillToolset = new SkillToolset(new LocalSkillSource(Path.of("skills")));
    FunctionTool getWeatherTool = FunctionTool.create(SkillsGetStarted.class, "getWeather");

    return LlmAgent.builder()
        .model("gemini-flash-latest")
        .name("skill_user_agent")
        .description("An agent that can use specialized skills.")
        .instruction("You are a helpful assistant that can leverage skills to perform tasks.")
        // Pass additional tools alongside SkillToolset in tools().
        .tools(mySkillToolset, getWeatherTool)
        .build();
  }
}
// --8<-- [end:full_example]
