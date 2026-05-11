# Agent Identity Auth Manager Integration

The Agent Identity Auth Manager service provides a streamlined, Google-managed solution for managing the complete lifecycle of auth credentials, including storing key configurations, generating and storing tokens, and auditing. This allows for a secure and simplified agent development experience.

Available from ADK version **1.30.0**.

For more details on the service itself, see the [Google Cloud Agent Identity Overview](https://docs.cloud.google.com/iam/docs/agent-identity-overview).

## Use with agent

Follow these steps to use the Agent Identity Auth Manager within ADK:

### 1. Install required package dependencies
Install the `agent-identity` extra package group to download the necessary client libraries.
```shell
pip install "google-adk[agent-identity]"
```

### 2. Register Auth Provider
In order for ADK to understand what `BaseAuthProvider` to use to process the given `CustomAuthScheme`, register the `GcpAuthProvider` instance with the `CredentialManager`. This should be done once in the agent code.

```python
from google.adk.auth.credential_manager import CredentialManager
from google.adk.integrations.agent_identity import GcpAuthProvider

CredentialManager.register_auth_provider(GcpAuthProvider())
```

### 3. Configure Tools (e.g., McpToolset, OpenAPIToolset)
Specify the Agent Identity auth provider configurations using the `GcpAuthProviderScheme` object and pass them as the `auth_scheme` field of the `Tool` or `Toolset`.

```python
from google.adk.integrations.agent_identity import GcpAuthProviderScheme
from google.adk.tools.mcp import McpToolset

auth_scheme = GcpAuthProviderScheme(
    name="projects/PROJECT_ID/locations/LOCATION/connectors/AUTH_PROVIDER_NAME",
    continue_uri=CONTINUE_URI
)

toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url="https://YOUR_MCP_SERVER_URL"),
    auth_scheme=auth_scheme,
)
```

### 4. Handling the Interactive OAuth Flow (Client-Side)
*   **Detecting the Auth Request**: Similar to the existing flow, whenever user consent is required, a `FunctionCall` event with name `adk-request-credential` will be generated containing the `auth_uri` field. The user app should open this `auth_uri` in a popup.
*   **Commit Endpoint Handler**: Once the user completes the OAuth consent flow, a redirect happens to the `continue_uri`. The agent application backend service must handle this redirect by submitting a POST request to the IAM credentials endpoint: `https://iamconnectorcredentials.googleapis.com/v1alpha/{connector_name}/credentials:finalize`.
*   After credentials are finalized, resume the agent conversation. Unlike the native user consent flow, no auth code is needed to be sent back to the agent.

## Security Considerations (Preventing Account Confusion)
As noted in the security review for this feature, developers must ensure the UI handling the consent flow is safe:
*   **No Auto-Popups**: Do not trigger the OAuth permission window automatically upon opening the app or clicking a deep link.
*   **Explicit Click**: Require the user to explicitly click a "Connect" button to start the flow.
*   **Identity Display**: Display the identity (e.g., email or account name) currently logged into the app on the connection screen so the user can verify they are connecting the correct account.

## Best practices
*   **Avoid caching access tokens** to allow the Agent Identity Auth Manager to audit access on these credentials effectively.

## Examples
*   A complete code sample and testing instructions can be found at: [adk-python samples](https://github.com/google/adk-python/tree/main/contributing/samples/gcp_auth).
SSS