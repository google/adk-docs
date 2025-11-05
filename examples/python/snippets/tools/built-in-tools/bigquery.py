from google.adk.tools.bigquery import BigQueryToolset

bq_toolset = BigQueryToolset()

# Get job info
job_info = bq_toolset.get_job_info(
    project_id="bigquery-public-data",
    job_id="bquxjob_12345678_1234567890"
)
print(job_info)

# Detect anomalies
anomalies = bq_toolset.detect_anomalies(
    project_id="my-gcp-project",
    history_data="my-dataset.my-sales-table",
    times_series_timestamp_col="sale_date",
    times_series_data_col="daily_sales",
)
print(anomalies)
