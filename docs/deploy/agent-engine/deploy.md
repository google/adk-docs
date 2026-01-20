# Deploy to Vertex AI Agent Engine

<div class="language-support-tag" title="Vertex AI Agent Engine currently supports only Python.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

This deployment procedure describes how to perform a standard deployment of
ADK agent code to Google Cloud
[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview).
You should follow this deployment path if you have an existing Google Cloud
project and if you want to carefully manage deploying an ADK agent to Agent
Engine runtime environment. These instructions use Cloud Console, the gcloud
command line interface, and the ADK command line interface (ADK CLI). This path
is recommended for users who are already familiar with configuring Google Cloud
projects, and users preparing for production deployments.

These instructions describe how to deploy an ADK project to Google Cloud Agent
Engine runtime environment, which includes the following stages:

*   [Setup Google Cloud project](#setup-cloud-project)
*   [Prepare agent project folder](#define-your-agent)
*   [Deploy the agent](#deploy-agent)

## Setup Google Cloud project {#setup-cloud-project}

To deploy your agent to Agent Engine, you need a Google Cloud project:

1. **Sign into Google Cloud**:
    * If you're an **existing user** of Google Cloud:
        * Sign in via
          [https://console.cloud.google.com](https://console.cloud.google.com)
        * If you previously used a Free Trial that has expired, you may need to
          upgrade to a
          [Paid billing account](https://docs.cloud.google.com/free/docs/free-cloud-features#how-to-upgrade).
    * If you are a **new user** of Google Cloud:
        * You can sign up for the
          [Free Trial program](https://docs.cloud.google.com/free/docs/free-cloud-features).
          The Free Trial gets you a $300 Welcome credit to spend over 91 days on various
          [Google Cloud products](https://docs.cloud.google.com/free/docs/free-cloud-features#during-free-trial)
          and you won't be billed. During the Free Trial, you also get access to the
          [Google Cloud Free Tier](https://docs.cloud.google.com/free/docs/free-cloud-features#free-tier),
          which gives you free usage of select products up to specified monthly
          limits, and to product-specific free trials.

2. **Create a Google Cloud project**
    * If you already have an existing Google Cloud project, you can use it, but
      be aware this process is likely to add new services to the project.
    * If you want to create a new Google Cloud project, you can create a new one
      on the [Create Project](https://console.cloud.google.com/projectcreate)
      page.

3. **Get your Google Cloud Project ID**
    * You need your Google Cloud Project ID, which you can find on your GCP
      homepage. Make sure to note the Project ID (alphanumeric with hyphens),
      _not_ the project number (numeric).

    <img src="/adk-docs/assets/project-id.png" alt="Google Cloud Project ID">

4. **Enable Vertex AI in your project**
    * To use Agent Engine, you need to [enable the Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com). Click on the "Enable" button to enable the API. Once enabled, it
    should say "API Enabled".

5. **Enable Cloud Resource Manager API in your project**
    * To use Agent Engine, you need to [enable the Cloud Resource Manager API](https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview). Click on the "Enable" button to enable the API. Once enabled, it should say "API Enabled".

## Set up your coding environment {#prerequisites-coding-env}

Now that you prepared your Google Cloud project, you can return to your coding
environment. These steps require access to a terminal within your coding
environment to run command line instructions.

### Authenticate your coding environment with Google Cloud

*   You need to authenticate your coding environment so that you and your
    code can interact with Google Cloud. To do so, you need the gcloud CLI.
    If you have never used the gcloud CLI, you need to first
    [download and install it](https://docs.cloud.google.com/sdk/docs/install-sdk)
    before continuing with the steps below:

*   Run the following command in your terminal to access your Google Cloud
    project as a user:

    ```shell
    gcloud auth login
    ```

    After authenticating, you should see the message
    `You are now authenticated with the gcloud CLI!`.

*   Run the following command to authenticate your code so that it can work with
    Google Cloud:

    ```shell
    gcloud auth application-default login
    ```

    After authenticating, you should see the message
    `You are now authenticated with the gcloud CLI!`.

*   (Optional) If you need to set or change your default project in gcloud, you
    can use:

    ```shell
    gcloud config set project MY-PROJECT-ID
    ```

### Define your agent {#define-your-agent}

With your Google Cloud and coding environment prepared, you're ready to deploy
your agent. The instructions assume that you have an agent project folder,
such as:

```shell
multi_tool_agent/
├── .env
├── __init__.py
└── agent.py
```

For more details on the project files and format, see the
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
code sample.

## Deploy the agent {#deploy-agent}

You can deploy from your terminal using the `adk deploy` command line tool. This
process packages your code, builds it into a container, and deploys it to the
managed Agent Engine service. This process can take several minutes.

The following example deploy command uses the `multi_tool_agent` sample code as
the project to be deployed:

```shell
PROJECT_ID=my-project-id
LOCATION_ID=us-central1

adk deploy agent_engine \
        --project=$PROJECT_ID \
        --region=$LOCATION_ID \
        --display_name="My First Agent" \
        multi_tool_agent
```

For `region`, you can find a list of the supported regions on the
[Vertex AI Agent Builder locations page](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine).
To learn about the CLI options for the `adk deploy agent_engine` command, see the
[ADK CLI Reference](https://google.github.io/adk-docs/api-reference/cli/cli.html#adk-deploy-agent-engine).

### Deploy command output

Once successfully deployed, you should see the following output:

```shell
Creating AgentEngine
Create AgentEngine backing LRO: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944/operations/2356952072064073728
View progress and logs at https://console.cloud.google.com/logs/query?project=hopeful-sunset-478017-q0
AgentEngine created. Resource name: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944
To use this AgentEngine in another session:
agent_engine = vertexai.agent_engines.get('projects/123456789/locations/us-central1/reasoningEngines/751619551677906944')
Cleaning up the temp folder: /var/folders/k5/pv70z5m92s30k0n7hfkxszfr00mz24/T/agent_engine_deploy_src/20251219_134245
```

Note that you now have a `RESOURCE_ID` where your agent has been deployed (which
in the example above is `751619551677906944`). You need this ID number along
with the other values to use your agent on Agent Engine.

## Using an agent on Agent Engine

Once you have completed deployment of your ADK project, you can query the agent
using the Vertex AI SDK, Python requests library, or a REST API client. This
section provides some information on what you need to interact with your agent
and how to construct URLs to interact with your agent's REST API.

To interact with your agent on Agent Engine, you need the following:

*   **PROJECT_ID** (example: "my-project-id") which you can find on your
    [project details page](https://console.cloud.google.com/iam-admin/settings)
*   **LOCATION_ID** (example: "us-central1"), that you used to deploy your agent
*   **RESOURCE_ID** (example: "751619551677906944"), which you can find on the
    [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

The query URL structure is as follows:

```shell
https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query
```

You can make requests from your agent using this URL structure. For more information
on how to make requests, see the instructions in the Agent Engine documentation
[Use an Agent Development Kit agent](https://docs.cloud.google.com/agent-builder/agent-engine/use/adk#rest-api).
You can also check the Agent Engine documentation to learn about how to manage your
[deployed agent](https://docs.cloud.google.com/agent-builder/agent-engine/manage/overview).
For more information on testing and interacting with a deployed agent, see
[Test deployed agents in Agent Engine](/adk-docs/deploy/agent-engine/test/).

### Monitoring and verification

*   You can monitor the deployment status in the
    [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)
    in the Google Cloud Console.
*   For additional details, you can visit the Agent Engine documentation
    [deploying an agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy)
    and
    [managing deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview).

## Test deployed agents

After completing deployment of your ADK agent you should test the workflow in
its new hosted environment. For more information on testing an ADK agent
deployed to Agent Engine, see
[Test deployed agents in Agent Engine](/adk-docs/deploy/agent-engine/test/).
