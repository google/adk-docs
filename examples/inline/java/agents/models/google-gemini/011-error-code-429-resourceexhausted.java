import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Gemini;
import com.google.genai.Client;
import com.google.genai.types.HttpOptions;
import com.google.genai.types.HttpRetryOptions;

// ...

LlmAgent agent = LlmAgent.builder()
    .model(Gemini.builder()
        .modelName("gemini-flash-latest")
        .apiClient(Client.builder()
            .httpOptions(HttpOptions.builder()
                .retryOptions(HttpRetryOptions.builder().initialDelay(1.0).attempts(2).build())
                .build())
            .build())
        .build())
    .build();