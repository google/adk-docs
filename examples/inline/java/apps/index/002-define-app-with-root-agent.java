import com.google.adk.agents.LlmAgent;
import com.google.adk.apps.App;

LlmAgent rootAgent = LlmAgent.builder()
    .model("gemini-flash-latest")
    .name("greeter_agent")
    .description("An agent that provides a friendly greeting.")
    .instruction("Reply with Hello, World!")
    .build();

App app = App.builder()
    .name("agents")
    .rootAgent(rootAgent)
    // Optionally include App-level features:
    // .plugins(plugins)
    // .contextCacheConfig(contextCacheConfig)
    // .eventsCompactionConfig(eventsCompactionConfig)
    .build();