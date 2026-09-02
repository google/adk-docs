from google.adk.auth.auth_credential import AuthCredential
from google.adk.auth.auth_credential import AuthCredentialTypes

# Configure the tool to look for "my_frontend_token" in the session state
credentials_config = AuthCredential(
    auth_type=AuthCredentialTypes.GOOGLE_CREDENTIALS,
    google_credentials_config={
        # Do not hardcode authentication keys in production code
        "external_access_token_key": "get_my_frontend_token" 
    }
)