import google.auth
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# Load Service Account credentials
credentials, _ = google.auth.load_credentials_from_file('path/to/key.json')

# Configure the toolset
credentials_config = GCSCredentialsConfig(credentials=credentials)
gcs_toolset = GCSToolset(credentials_config=credentials_config)