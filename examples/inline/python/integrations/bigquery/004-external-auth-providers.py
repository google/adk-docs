from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# The key used to look up the access token in the session state
credentials_config = BigQueryCredentialsConfig(
    external_access_token_key="YOUR_AUTH_ID"
)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)