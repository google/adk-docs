plugin = BigQueryAgentAnalyticsPlugin(
    project_id="my-project",
    dataset_id="my_dataset",
    batch_size=10,           # forwarded to BigQueryLoggerConfig
    shutdown_timeout=5.0,    # forwarded to BigQueryLoggerConfig
)