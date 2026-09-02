from google.adk.auth.auth_credential import ServiceAccount
from google.adk.tools.openapi_tool.auth.auth_helpers import service_account_scheme_credential
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

# Configure the ServiceAccount to use ID token authentication.
# Replace <YOUR_AUDIENCE_URL> with the URL of the service you are calling.
sa_config = ServiceAccount(
    use_default_credential=True,
    use_id_token=True,
    audience="<YOUR_AUDIENCE_URL>",
)

auth_scheme, auth_credential = service_account_scheme_credential(sa_config)

sample_toolset = OpenAPIToolset(
    spec_str=sa_openapi_spec_str, # Fill this with an OpenAPI spec
    spec_str_type="json",
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
)