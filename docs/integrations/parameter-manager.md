---
catalog_title: Google Cloud Parameter Manager
catalog_description: Manage and retrieve runtime configuration parameters and secrets securely for ADK agents.
catalog_icon: /integrations/assets/parameter_manager.png
catalog_tags: ["google"]
---

# Parameter Manager for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.30.0</span>
</div>

The [Google Cloud Parameter
Manager](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/overview)
integration provides a standard interface for Agent Development Kit (ADK) agents to connect with the Google Cloud Parameter Manager service
and retrieve rendered parameter values at runtime. This module lets you use the
Google Cloud Parameter Manager service as the single source of truth for agent instructions and tool
configurations.

## Use cases

The Parameter Manager integration supports several operations:

*   **Dynamic instruction updates**: You can publish parameters instantly to
    defend against prompt injection attacks, update mandatory disclaimer
    resources, or automatically adjust the agent tone without a full code
    redeployment.
*   **Feature flag and parameter management**: You can store configurations as a
    JSON payload and retrieve them through the tool context to lower query rates
    or switch between experimental and production API endpoints.
*   **Accuracy improvement with input and output pairs**: You can store few-shot
    examples as YAML files and load them into the session state to improve agent
    performance over time.
*   **Just-in-time tool authorization**: You can load secrets into memory on
    demand rather than using insecure static API keys in initialization code.
*   **Secure multi-tenant workflows**: You can store Parameter Manager IDs that
    map to users and use callbacks to rehydrate the session state with resolved
    OAuth tokens.
*   **Encrypted system tasks**: You can prevent primary database passwords from
    entering the large language model (LLM) conversation history during
    background polling tasks.
*   **Multi-region deployments**: You can maintain shared logic across global
    deployments while using regional Parameter Manager overrides to apply local
    currency and contact information.

## Prerequisites

You must meet the following requirements before you configure the integration:

- **Required Software Versions**: ADK Python version v1.30.0 or higher
- **Required Accounts / APIs**: A [Google Cloud Project](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects) with the [**Parameter Manager API**](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/prepare-environment#enable_api), [**Secret Manager API**](https://docs.cloud.google.com/secret-manager/docs/configuring-secret-manager), and **Agent Development Kit API** enabled.

Complete the following setup steps:

1.  [Set up an agent with ADK](/get-started/).
1.  [Create a parameter](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/create-parameter).
1.  Grant the [Parameter Manager Parameter Accessor](https://docs.cloud.google.com/iam/docs/roles-permissions/parametermanager#parametermanager.parameterAccessor) role
    (`roles/parametermanager.parameterAccessor`)
    IAM role to your agent identity. This role allows your agent to render the parameter configuration at runtime.
1.  If your parameter contains embedded secrets, grant the [Secret Manager Secret Accessor](https://docs.cloud.google.com/iam/docs/roles-permissions/secretmanager#secretmanager.secretAccessor) role                 (`roles/secretmanager.secretAccessor`) to your parameter resource. This cross-service permission allows Parameter Manager to resolve the referenced secrets on behalf of the agent. For more information, [Grant the Secret Manager Secret Accessor role to the parameter](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/reference-secrets-in-parameter#grant_the_secret_manager_secret_accessor_role_to_the_parameter).

## Installation

Install the ADK extensions package to enable the Parameter Manager integration:

```bash
pip install "google-adk[extensions]"
```

## Use with agent

The following examples show complete, working code to retrieve a parameter
securely within an ADK agent using either global or regional endpoints.

### Global parameters

```python
--8<-- "examples/inline/python/integrations/parameter-manager/001-global-parameters.py"
```

### Regional parameters

```python
--8<-- "examples/inline/python/integrations/parameter-manager/002-regional-parameters.py"
```

## Resources

-   [Parameter Manager
    documentation](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/overview)
-   [ADK GitHub repository](https://github.com/google/adk-python)
-   [Include few-shot examples](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/prompts/few-shot-examples)
