---
catalog_title: Google Cloud Agent Identity
catalog_description: Manage OAuth tokens and API keys for your agents
catalog_icon: /integrations/assets/agent-identity.svg
catalog_tags: ["google"]
---

# Agent Identity Auth Manager for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.30.0</span><span class="lst-preview">Preview</span>
</div>

The [Google Cloud Agent
Identity](https://docs.cloud.google.com/iam/docs/agent-identity-overview)
service provides a streamlined, Google-managed solution for managing the
complete lifecycle of auth credentials, including storing credential
configurations, generating and storing tokens, and auditing access. This 
approach allows for a secure and simplified agent development experience.

!!! example "Preview release"

    The Agent Identity Auth Manager feature is a Preview release. For more
    information, see the [launch stage
    descriptions](https://cloud.google.com/products#product-launch-stages).

## Use cases

- **Simplified OAuth Flow**: Manage the complete lifecycle of auth credentials
  without building custom infrastructure.
- **Secure Exchange and Storage of Tokens**: Securely store credential
  configurations and exchange tokens.
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

Install the `agent-identity` extra package group to download the necessary
client libraries.

```bash
pip install "google-adk[agent-identity]"
```

## Use with agent

Follow these steps to use the Agent Identity Auth Manager within ADK:

### Register auth provider

To enable ADK to determine which `BaseAuthProvider` to use for a given
`CustomAuthScheme`, register the `GcpAuthProvider` instance with the
`CredentialManager`. This needs to be done only once in the agent code.

```python
from google.adk.auth.credential_manager import CredentialManager
from google.adk.integrations.agent_identity import GcpAuthProvider

CredentialManager.register_auth_provider(GcpAuthProvider())
```

### Configure tools

Configure the Agent Identity auth provider using a `GcpAuthProviderScheme`
object, then pass it to the `auth_scheme` parameter of any supported `Tool` or
`Toolset`. The following example shows usage with `McpToolset`, but
`GcpAuthProviderScheme` also works with other tools like
`AuthenticatedFunctionTool`. See the [GCP Auth
sample](https://github.com/google/adk-python/tree/main/contributing/samples/gcp_auth)
for a complete example.

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

### Handle OAuth consent

- **Detecting the Auth Request**: Similar to the existing flow, whenever user
  consent is required, a `FunctionCall` event named `adk-request-credential`
  is generated containing the `auth_uri` field. The user app should open
  the `auth_uri` in a popup window to continue the user consent flow.
- **Continue URI Handler**:
    - Once the user completes the OAuth consent flow on the third-party
      provider's website, the system redirects to the `continue_uri`
      callback defined earlier in the `GcpAuthProviderScheme`. The agent
      application service must implement this redirect. To finalize issuance,
      your handler must submit a POST request to the credentials endpoint:
      `https://iamconnectorcredentials.googleapis.com/v1alpha/{connector_name}/credentials:finalize`.
    - After credentials are successfully finalized, the web application should
      resume the agent by sending a FunctionResponse. For a sample
      implementation, refer to the [sample
      code](https://docs.cloud.google.com/iam/docs/auth-with-3lo#resume-conversation).
      Unlike the native user consent flow, no authorization code is required to
      resume the agent.
    - For more details, refer to the [sample handler
      implementation](https://docs.cloud.google.com/iam/docs/auth-with-3lo#validation-endpoint).
- **Resume the conversation**: Irrespective of the status of the consent flow
  (successful or unsuccessful), the agent app should resume the agent to
  complete the conversation turn. The ADK automatically determines whether
  consent was successfully completed and raise an error if it was not.

## Resources

- [Google Cloud Agent Identity Overview](https://docs.cloud.google.com/iam/docs/agent-identity-overview)
- [Sample agent code](https://github.com/google/adk-python/tree/main/contributing/samples/gcp_auth)
