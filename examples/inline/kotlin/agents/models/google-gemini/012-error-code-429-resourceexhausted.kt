import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.genai.Client
import com.google.genai.types.HttpOptions
import com.google.genai.types.HttpRetryOptions

val client = Client.builder()
    .apiKey("YOUR_API_KEY")
    .httpOptions(HttpOptions.builder()
        .retryOptions(HttpRetryOptions.builder().initialDelay(1.0).attempts(2).build())
        .build())
    .build()

val model = Gemini(client = client, name = "gemini-flash-latest")

val agent = LlmAgent(
    name = "my_agent",
    model = model
    // ...
)