import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.models.Gemini;
import com.google.adk.plugins.Plugin;
import com.google.adk.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin;
import com.google.adk.plugins.agentanalytics.BigQueryLoggerConfig;
import com.google.adk.runner.InMemoryRunner;
import com.google.common.collect.ImmutableList;

public final class Agent {
  public static void main(String[] args) throws Exception {
    Plugin bqLoggingPlugin = new BigQueryAgentAnalyticsPlugin(
        BigQueryLoggerConfig.builder()
            .projectId("your-gcp-project-id")
            .datasetId("your-big-query-dataset-id")
            .tableName("agent_events") // Optional, defaults to "events" in Java
            .build());

    InMemoryRunner runner = new InMemoryRunner(
        LlmAgent.builder()
            .model(Gemini.builder().modelName("gemini-2.5-flash").build())
            .name("my_agent")
            .instruction("You are a helpful assistant.")
            .build(),
        "my_agent",
        ImmutableList.of(bqLoggingPlugin));

    // Use runner ...

    // Close runner to flush and close plugin
    runner.close().blockingAwait();
  }
}