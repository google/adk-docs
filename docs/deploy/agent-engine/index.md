# Deploy to Vertex AI Agent Engine

<div class="language-support-tag" title="Vertex AI Agent Engine currently supports only Python.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

Google Cloud
[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
is a fully managed Google Cloud service for developers to deploy, manage,
and scale AI agents in production. Agent Engine handles the infrastructure to
scale agents in production so you can focus on creating intelligent and
impactful applications.

This guide includes the following deployment paths, which serve different
purposes:

*   **[Standard deployment](/adk-docs/deploy/agent-engine/deploy/)**:
    Follow this standard deployment path if you have an existing Google Cloud
    project and if you want to carefully manage deploying an ADK agent to Agent
    Engine. This deployment path uses Cloud Console, ADK command line interface,
    and provides step-by-step instructions. This path is recommended for users
    who are already familiar with configuring Google Cloud projects, and users
    preparing for production deployments.

*   **[Agent Starter Pack deployment](/adk-docs/deploy/agent-engine/asp/)**:
    Follow this accelerated deployment path if you do not have an existing
    Google Cloud project and are creating a project specifically for development
    and testing. The Agent Starter Pack (ASP) helps you deploy ADK projects
    quickly and it configures Google Cloud services that are not strictly
    necessary for running an ADK agent with Agent Engine.

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
