from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
from google.adk.tools.apihub_tool.apihub_toolset import APIHubToolset

# Provide authentication for your APIs. Not required if your APIs don't required authentication.
auth_scheme, auth_credential = token_to_scheme_credential(
    "apikey", "query", "apikey", apikey_credential_str
)

sample_toolset = APIHubToolset(
    name="apihub-sample-tool",
    description="Sample Tool",
    access_token="...",  # Copy your access token generated in step 1
    apihub_resource_name="...", # API Hub resource name
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
)