import com.google.adk.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin;
import com.google.adk.plugins.agentanalytics.BigQueryLoggerConfig;
import java.time.Duration;
import java.util.function.BiFunction;

// Custom formatter to redact dollar amounts
BiFunction<Object, String, Object> redactDollarAmounts = (content, eventType) -> {
  String textContent = content.toString();
  return textContent.replaceAll("\\$\\d+(?:,\\d{3})*(?:\\.\\d+)?", "xxx");
};

BigQueryLoggerConfig config = BigQueryLoggerConfig.builder()
    .enabled(true)
    .projectId("my-project")
    .datasetId("my_dataset")
    .tableName("agent_events")
    .batchSize(1)
    .batchFlushInterval(Duration.ofMillis(500))
    .contentFormatter(redactDollarAmounts)
    .autoSchemaUpgrade(true)
    .createViews(true)
    .build();

BigQueryAgentAnalyticsPlugin plugin = new BigQueryAgentAnalyticsPlugin(config);