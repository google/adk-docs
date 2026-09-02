import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.GoogleSearchTool;

LlmAgent rootAgent = LlmAgent.builder()
    .name("google_search_agent")
    .model("gemini-flash-latest")
    .instruction("Answer questions using Google Search when needed. Always cite sources.")
    .description("Professional search assistant with Google Search capabilities")
    .tools(GoogleSearchTool.INSTANCE)
    .build();