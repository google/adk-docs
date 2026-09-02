import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Gemini;
import com.google.genai.types.GenerateContentConfig;

// ...

// Replace with your actual Agent Platform Endpoint resource name
String llama3Endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID";

LlmAgent agentLlama3Vertex = LlmAgent.builder()
    .model(Gemini.builder()
        .modelName(llama3Endpoint)
        .build())
    .name("llama3_vertex_agent")
    .instruction("You are a helpful assistant based on Llama 3, hosted on Agent Platform.")
    .generateContentConfig(GenerateContentConfig.builder()
        .maxOutputTokens(2048)
        .build())
    // ... other agent parameters
    .build();