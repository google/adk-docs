import google.auth
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# Load Application Default Credentials
credentials, _ = google.auth.default()

# Configure the toolset
credentials_config = GCSCredentialsConfig(credentials=credentials)
gcs_toolset = GCSToolset(credentials_config=credentials_config)