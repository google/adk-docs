---
catalog_title: Agent Identity
catalog_description: Manages the complete lifecycle of an access token using the GCP Agent Identity Credentials service.
---

# Agent Identity

## Installation

```bash
pip install "google-adk[agent-identity]"
```

## Global Registration

Register the provider globally in your application:

```python
from google.adk.auth.credential_manager import CredentialManager
from google.adk.integrations.agent_identity import GcpAuthProvider

CredentialManager.register_auth_provider(GcpAuthProvider())
```

## Toolset Configuration

To use the Agent Identity provider with a specific toolset, define the scheme and pass it to the toolset's constructor.

```python
from google.adk.integrations.agent_identity import GcpAuthProviderScheme

auth_scheme = GcpAuthProviderScheme(name="my-jira-auth_provider")
mcp_toolset_jira = McpToolset(..., auth_scheme=auth_scheme)
```
