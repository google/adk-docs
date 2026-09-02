---
catalog_title: Google Cloud Secret Manager
catalog_description: Retrieve secrets at runtime without exposing them to the LLM
catalog_icon: /integrations/assets/secret_manager.png
catalog_tags: ["google"]
---

# Secret Manager for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.29.0</span>
</div>

The [Secret Manager](https://docs.cloud.google.com/secret-manager/docs/overview) integration provides a standard interface for ADK agents to retrieve sensitive credentials (such as API keys, database passwords, and private keys) at runtime. This approach ensures that sensitive information isn't hardcoded in the source code or exposed in the LLM's context window, conversation history, or observability logs.

## Use cases

- **Just-in-time tool authorization**: Storing static API keys in agent initialization code is insecure. With this integration, the ADK agent dynamically retrieves credentials from Secret Manager at runtime, ensuring keys are loaded into memory on demand.
- **Secure multi-tenant workflows**: To avoid passing raw user tokens from frontend, agents can map user IDs to specific Secret Manager resources. A `before_agent_callback` hook dynamically retrieves the user's secret to securely rehydrate the `session.state` OAuth token.
- **Encrypted system tasks**: Background system tasks, such as database polling, retrieve credentials directly from Secret Manager inside the tool logic. This prevents passwords from entering the LLM's conversation history and exposes only execution summary to the model.

## Prerequisites

- **Required Software Versions**: ADK Python version v1.29.0 or higher
- **Required Accounts / APIs**: A [Google Cloud Project](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects) with the [**Secret Manager API**](https://docs.cloud.google.com/secret-manager/docs/configuring-secret-manager) and **Agent Development Kit API** enabled.

Complete the following setup steps:

1.  [Set up an agent with ADK](/get-started/).
1.  [Create a secret](https://docs.cloud.google.com/secret-manager/docs/creating-and-accessing-secrets) (such as an API key) in Secret Manager.
1.  Grant the [`Secret Manager Secret Accessor`](https://docs.cloud.google.com/iam/docs/roles-permissions/secretmanager#secretmanager.secretAccessor) IAM role to your agent identity.

## Installation

```bash
pip install "google-adk[extensions]"
```

## Use with agent

```python
--8<-- "examples/inline/python/integrations/secret-manager/001-use-with-agent.py"
```

## Resources
- [Secret Manager documentation](https://docs.cloud.google.com/secret-manager/docs/overview).
- [ADK GitHub repository](https://github.com/google/adk-python).
