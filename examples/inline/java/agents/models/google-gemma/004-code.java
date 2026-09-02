import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.openai.OpenAiStreamingChatModel;

// Endpoint URL provided by your model deployment
String apiBaseUrl = "https://your-vllm-endpoint.run.app/v1";

// Model name as recognized by *your* vLLM endpoint configuration
String gemmaModelName = "gg-hf-gg/gemma-4-31b-it";

// First, define an OpenAI compatible chat model with LangChain4j
StreamingChatModel model =
    OpenAiStreamingChatModel.builder()
        .modelName(gemmaModelName)
        // If your endpoint requires an API key
        // .apiKey("YOUR_ENDPOINT_API_KEY")
        .baseUrl(apiBaseUrl)
        .customParameters(
            Map.of(
                "skip_special_tokens", false,
                "chat_template_kwargs", Map.of("enable_thinking", true)
            )
        )
        .build();

// Configure the agent with the LangChain4j wrapper model
LlmAgent weatherAgent = LlmAgent.builder()
    .model(new LangChain4j(model))
    .name("weather_agent")
    .instruction("""
        You are a helpful assistant that can provide the current weather.
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