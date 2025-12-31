# Deploy to Vertex AI Agent Engine

<div class="language-support-tag" title="Vertex AI Agent Engine currently supports only Python.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

Google Cloud Vertex AI
[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
is a set of modular services that help developers scale and govern agents in
production. The Agent Engine runtime enables you to deploy agents in production
with end-to-end managed infrastructure so you can focus on creating intelligent
and impactful agents. When you deploy an ADK agent to Agent Engine, your code
runs in the *Agent Engine runtime* environment, which is part of the larger set
of agent services provided by the Agent Engine product.

This guide includes the following deployment paths, which serve different
purposes:

*   **[Standard deployment](/adk-docs/deploy/agent-engine/deploy/)**: Follow
    this standard deployment path if you have an existing Google Cloud project
    and if you want to carefully manage deploying an ADK agent to the Agent
    Engine runtime. This deployment path uses Cloud Console, ADK command line
    interface, and provides step-by-step instructions. This path is recommended
    for users who are already familiar with configuring Google Cloud projects,
    and users preparing for production deployments.

*   **[Agent Starter Pack deployment](/adk-docs/deploy/agent-engine/asp/)**:
    Follow this accelerated deployment path if you do not have an existing
    Google Cloud project and are creating a project specifically for development
    and testing. The Agent Starter Pack (ASP) helps you deploy ADK projects
    quickly and it configures Google Cloud services that are not strictly
    necessary for running an ADK agent with the Agent Engine runtime.

!!! note "Agent Engine service on Google Cloud"

    Agent Engine is a paid service and you may incur costs if you go
    above the no-cost access tier. More information can be found on the
    [Agent Engine pricing page](https://cloud.google.com/vertex-ai/pricing#vertex-ai-agent-engine).

## Deployment payload {#payload}

When you deploy your ADK agent project to Agent Engine, the following content is
uploaded to the service:

- Your ADK agent code
- Any dependencies declared in your ADK agent code

The deployment *does not* include the ADK API server or the ADK web user
interface libraries. The Agent Engine service provides the libraries for ADK API
server functionality.
