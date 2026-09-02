from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# Provide OAuth 2.0 Client ID and Secret
credentials_config = GCSCredentialsConfig(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
gcs_toolset = GCSToolset(credentials_config=credentials_config)