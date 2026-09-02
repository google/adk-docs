import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.LoadMemoryTool;

LlmAgent agent = new LlmAgent.Builder()
    .model(MODEL_ID)
    .name("weather_sentiment_agent")
    .instruction("...")
    .tools(new LoadMemoryTool())
    .build();