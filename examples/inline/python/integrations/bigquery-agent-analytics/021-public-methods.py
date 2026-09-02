async with BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID
) as plugin:
    # plugin is initialized and ready to use
    ...
# plugin.shutdown() is called automatically on exit