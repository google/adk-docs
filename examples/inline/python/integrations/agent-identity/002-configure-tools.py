from google.adk.integrations.agent_identity import GcpAuthProviderScheme
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams

auth_scheme = GcpAuthProviderScheme(
    name="projects/PROJECT_ID/locations/LOCATION/connectors/AUTH_PROVIDER_NAME",
    # continue_uri is only needed for 3-legged OAuth flows. This URI receives
    # the redirect after user consent and must be hosted by your application.
    continue_uri=CONTINUE_URI
)

toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url="https://YOUR_MCP_SERVER_URL"),
    auth_scheme=auth_scheme,
)