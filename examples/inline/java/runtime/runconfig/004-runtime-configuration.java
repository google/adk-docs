import com.google.adk.agents.RunConfig;
import com.google.adk.agents.RunConfig.StreamingMode;

RunConfig config = RunConfig.builder()
    .streamingMode(StreamingMode.SSE)
    .maxLlmCalls(200)
    .build();