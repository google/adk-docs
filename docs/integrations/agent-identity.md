---
catalog_title: Agent Identity
catalog_description: Manage access-token lifecycle with the Google Cloud Agent Identity Credentials service
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["auth", "google-cloud"]
---

# Agent Identity

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.31.0</span><span class="lst-preview">Experimental</span>
</div>

Agent Identity manages the lifecycle of access tokens by using the Google Cloud
Agent Identity Credentials service. Use this integration when your agent needs
to authenticate to protected tools or services without implementing the full
credential retrieval and refresh flow yourself.

## Install

Install ADK with the Agent Identity extra:

```bash
pip install "google-adk[agent-identity]"
```

## Register the provider

Register `GcpAuthProvider` with the `CredentialManager` once during application
startup:

```python
from google.adk.auth.credential_manager import CredentialManager
from google.adk.integrations.agent_identity import GcpAuthProvider

CredentialManager.register_auth_provider(GcpAuthProvider())
```

## Configure a toolset

Use `GcpAuthProviderScheme` as the `auth_scheme` for a toolset that should use
Agent Identity credentials. The `name` value identifies the Agent Identity
provider configuration to use.

```python
from google.adk.integrations.agent_identity import GcpAuthProviderScheme
from google.adk.tools.mcp_tool import McpToolset

auth_scheme = GcpAuthProviderScheme(name="my-jira-auth-provider")

mcp_toolset_jira = McpToolset(
    # ...
    auth_scheme=auth_scheme,
)
```

You can also pass scopes when the connected service requires them:

```python
auth_scheme = GcpAuthProviderScheme(
    name="my-jira-auth-provider",
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
```

## How it works

When a tool uses `GcpAuthProviderScheme`, ADK delegates credential retrieval to
`GcpAuthProvider`. The provider calls the Agent Identity Credentials service
for the configured connector and current user, then returns an ADK
`AuthCredential` that the tool can use.

Depending on the connector and credential type, the service can return
credentials immediately, require polling for a non-interactive OAuth flow, or
return a consent URL for a three-legged OAuth flow.

For broader guidance on choosing between managed and self-managed credentials,
see [Authenticating with Tools](/tools-custom/authentication/).
