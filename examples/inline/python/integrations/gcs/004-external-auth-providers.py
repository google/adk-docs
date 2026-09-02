from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# The key used to look up the access token in the session state
credentials_config = GCSCredentialsConfig(
    external_access_token_key="YOUR_AUTH_ID"
)
gcs_toolset = GCSToolset(credentials_config=credentials_config)