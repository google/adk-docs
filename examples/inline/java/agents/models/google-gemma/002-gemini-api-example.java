// Set GEMINI_API_KEY environment variable to your API key
// export GEMINI_API_KEY="YOUR_API_KEY"

import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;

LlmAgent weatherAgent = LlmAgent.builder()
    .model("gemma-4-31b-it")
    .name("weather_agent")
    .instruction("""
        You are a helpful assistant that can provide current weather.
    """)
    .tools(FunctionTool.create(this, "getWeather")]    
    .build();

@Schema(name = "getWeather", 
        description = "Retrieve the weather forecast for a given location")
public Map<String, String> getWeather(
    @Schema(name = "location",
            description = "The location for the weather forecast")
    String location) {
    return Map.of("forecast", "Location: " + location 
        + ". Weather: sunny, 76 degrees Fahrenheit, 8 mph wind.");
}