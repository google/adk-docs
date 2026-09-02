from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# Provide OAuth 2.0 Client ID and Secret
credentials_config = BigQueryCredentialsConfig(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)