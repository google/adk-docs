import com.google.adk.agents.LlmAgent;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.HttpOptions;
import com.google.genai.types.HttpRetryOptions;

// ...

LlmAgent rootAgent = LlmAgent.builder()
    .model("gemini-flash-latest")
    // ...
    .generateContentConfig(GenerateContentConfig.builder()
        // ...
        .httpOptions(HttpOptions.builder()
            // ...
            .retryOptions(HttpRetryOptions.builder().initialDelay(1.0).attempts(2).build())
            // ...
            .build())
        // ...
        .build())
    .build();