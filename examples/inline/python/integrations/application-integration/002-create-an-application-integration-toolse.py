from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset
from google.adk.tools.openapi_tool.auth.auth_helpers import dict_to_auth_scheme
from google.adk.auth import AuthCredential
from google.adk.auth import AuthCredentialTypes
from google.adk.auth import OAuth2Auth

oauth2_data_google_cloud = {
  "type": "oauth2",
  "flows": {
      "authorizationCode": {
          "authorizationUrl": "https://accounts.google.com/o/oauth2/auth",
          "tokenUrl": "https://oauth2.googleapis.com/token",
          "scopes": {
              "https://www.googleapis.com/auth/cloud-platform": (
                  "View and manage your data across Google Cloud Platform"
                  " services"
              ),
              "https://www.googleapis.com/auth/calendar.readonly": "View your calendars"
          },
      }
  },
}

oauth_scheme = dict_to_auth_scheme(oauth2_data_google_cloud)

auth_credential = AuthCredential(
  auth_type=AuthCredentialTypes.OAUTH2,
  oauth2=OAuth2Auth(
      client_id="...", #TODO: replace with client_id
      client_secret="...", #TODO: replace with client_secret
  ),
)

connector_tool = ApplicationIntegrationToolset(
    project="test-project", # TODO: replace with GCP project of the connection
    location="us-central1", #TODO: replace with location of the connection
    connection="test-connection", #TODO: replace with connection name
    entity_operations={"Entity_One": ["LIST","CREATE"], "Entity_Two": []},#empty list for actions means all operations on the entity are supported.
    actions=["GET_calendars/%7BcalendarId%7D/events"], #TODO: replace with actions. this one is for list events
    service_account_json='{...}', # optional. Stringified json for service account key
    tool_name_prefix="tool_prefix2",
    tool_instructions="...",
    auth_scheme=oauth_scheme,
    auth_credential=auth_credential
)