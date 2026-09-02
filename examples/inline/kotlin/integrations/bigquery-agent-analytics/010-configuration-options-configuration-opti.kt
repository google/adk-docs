import com.google.adk.kt.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin
import com.google.adk.kt.plugins.agentanalytics.BigQueryLoggerConfig

val config =
    BigQueryLoggerConfig(
        projectId = "my-project",
        datasetId = "my_dataset",
        location = "EU",
        tableName = "agent_events",
    )

val plugin = BigQueryAgentAnalyticsPlugin(config = config)