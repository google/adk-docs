---
catalog_title: Agent Identity Auth Manager
catalog_description: Manage OAuth tokens and API keys for your agents
catalog_icon: /integrations/assets/agent-identity.svg
catalog_tags: ["google"]
---

# Agent Identity Auth Manager for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span> <span class="lst-python">Python v1.30.0</span> <span class="lst-preview">Preview</span>
</div>

The Google Cloud [Agent Identity](https://docs.cloud.google.com/iam/docs/agent-identity-overview) 
service provides a streamlined, Google-managed solution for managing the complete lifecycle of auth credentials, including
storing credential configurations, generating and storing tokens, and auditing the access. This
allows for a secure and simplified agent development experience.

!!! example "Preview release"

The Agent Identity Auth Manager feature is a Preview release. For more
information, see the [launch stage descriptions](https://cloud.google.com/products#product-launch-stages).

## Use cases

- **Simplified OAuth Flow**: Manage the complete lifecycle of auth credentials
  without building custom infrastructure.
- **Secure Exchange and Storage of Tokens**: Securely store credential configurations, and exchange tokens.
- **Audit Logging**: View and audit access to stored credentials.

## Prerequisites

- A [Google Cloud
  project](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
- One or more Agent Identity [auth
  providers](https://cloud.google.com/iam/docs/manage-auth-providers) created in
  your project
- The caller identity must have the
  [`iamconnectors.user`](https://docs.cloud.google.com/iam/docs/roles-permissions/iamconnectors#iamconnectors.user)
  role or equivalent permissions
- Authentication configured via [Application Default
  Credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
  (`gcloud auth application-default login`)

## Installation

Make sure the Agent Identity service is enabled and appropriate permissions are set for 
your agent to access it. To install necessary package dependencies for this feature, install 
the agent-identity additional package group. This will download the client for the above GCP service.

```bash
pip install "google-adk[agent-identity]"
```

## Use with agent

Follow these steps to use the Agent Identity Auth Manager within ADK:

### Register auth provider

In order for ADK to understand what `BaseAuthProvider` to use to process the
given `CustomAuthScheme`, register the `GcpAuthProvider` instance with the
`CredentialManager`. This should be done once in the agent code.

```python
from google.adk.auth.credential_manager import CredentialManager
from google.adk.integrations.agent_identity import GcpAuthProvider

CredentialManager.register_auth_provider(GcpAuthProvider())
```

### Configure tools

Specify the Agent Identity auth provider configurations using the
`GcpAuthProviderScheme` object and pass them as the `auth_scheme` field of the
`Tool` or `Toolset`.

```python
from google.adk.integrations.agent_identity import GcpAuthProviderScheme
from google.adk.tools.mcp import McpToolset

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
```

You can also use `GcpAuthProviderScheme` with `AuthenticatedFunctionTool` by
wrapping it in an `AuthConfig`. See the [GCP Auth
sample](https://github.com/google/adk-python/tree/main/contributing/samples/gcp_auth)
for a complete example.

### Handle OAuth consent

- **Detecting the Auth Request**: Similar to the existing flow, whenever user
  consent is required, a `FunctionCall` event with name `adk-request-credential`
  will be generated containing the `auth_uri` field. The user app should open
  this `auth_uri` in a popup.
- **Commit Endpoint Handler**: Once the user completes the OAuth consent flow, a
  redirect happens to the `continue_uri`. The agent application backend service
  must handle this redirect by submitting a POST request to the IAM credentials
  endpoint:
  `https://iamconnectorcredentials.googleapis.com/v1alpha/{connector_name}/credentials:finalize`.
- **Resume the conversation**: After credentials are finalized, resume the
  agent conversation. Unlike the native user consent flow, no auth code is
  needed to be sent back to the agent.

## Security considerations

When implementing the consent flow, developers must ensure the UI follows these
security practices:

- **No Auto-Popups**: Do not trigger the OAuth permission window automatically
  upon opening the app or clicking a deep link.
- **Explicit Click**: Require the user to explicitly click a "Connect" button to
  start the flow.
- **Identity Display**: Display the identity (e.g., email or account name)
  currently logged into the app on the connection screen so the user can verify
  they are connecting the correct account.

## Best practices

- **Avoid caching access tokens** to allow the Agent Identity Auth Manager to
  audit access on these credentials effectively.

## Resources

- [Google Cloud Agent Identity Overview](https://docs.cloud.google.com/iam/docs/agent-identity-overview)
- [Sample agent code](https://github.com/google/adk-python/tree/main/contributing/samples/gcp_auth)
