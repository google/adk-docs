# Deploy to Agent Runtime

<div class="language-support-tag" title="Agent Runtime currently supports Python and Go.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-go">Go v1.2.0</span>
</div>

Google Cloud Agent Platform
[Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
is a set of modular services that help developers scale and govern agents in
production. The Agent Runtime runtime enables you to deploy agents in production
with end-to-end managed infrastructure so you can focus on creating intelligent
and impactful agents. When you deploy an ADK agent to Agent Runtime, your code
runs in the *Agent Runtime runtime* environment, which is part of the larger set
of agent services provided by the Agent Runtime product.

This guide includes the following deployment paths, which serve different
purposes:

*   **[Standard deployment](/deploy/agent-runtime/deploy/)**: Follow
    this standard deployment path if you want to carefully manage deploying an ADK agent to the Agent
    Runtime runtime. This deployment path uses Cloud Console, ADK command line
    interface, and provides step-by-step instructions. This path is recommended
    for users who are already familiar with configuring Google Cloud projects,
    and users preparing for production deployments.

*   **[Agents CLI deployment](/deploy/agent-runtime/agents-cli/)**:
    Follow this accelerated deployment path to set up a fully configured Google
    Cloud environment with CI/CD, infrastructure-as-code, and deployment pipelines
    for your ADK agent. You need a Google Cloud project with billing enabled.
    Agents CLI in Agent Platform helps you deploy ADK projects quickly and it
    includes advanced service configurations that extend the core capabilities of
    the Agent Runtime runtime for more mature use cases.

!!! note "Agent Runtime service on Google Cloud"

    Agent Runtime is a paid service and you may incur costs if you go
    above the no-cost access tier. More information can be found on the
    [Agent Runtime pricing page](https://cloud.google.com/vertex-ai/pricing#vertex-ai-agent-engine).

## Deployment payload {#payload}


=== "Python"

    When you deploy your ADK agent project to Agent Runtime, the following content is
    uploaded to the service:

    - Your ADK agent code
    - Any dependencies declared in your ADK agent code

    The deployment *does not* include the ADK API server or the ADK web user
    interface libraries. The Agent Runtime service provides the libraries for ADK API
    server functionality.

=== "Go"

    When you deploy your ADK project to Agent Runtime, the following content is uploaded to the server:

    - Your ADK project source code

    Please mind that Agent Runtime has its own API for querying the agent. All you have to do is use a dedicated launcher:
    ```go
	l := agentengine.NewLauncher(agentEngineID)
    err := l.Execute(ctx, config, os.Args[1:])
    ```
