import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Gemini;

// ...

// Replace with your fine-tuned model's endpoint resource name
String finetunedGeminiEndpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID";

LlmAgent agentFinetunedGemini = LlmAgent.builder()
    .model(Gemini.builder()
        .modelName(finetunedGeminiEndpoint)
        .build())
    .name("finetuned_gemini_agent")
    .instruction("You are a specialized assistant trained on specific data.")
    // ... other agent parameters
    .build();