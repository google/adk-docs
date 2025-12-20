# Deploy to Agent Engine with Agent Starter Pack

<div class="language-support-tag" title="Vertex AI Agent Engine currently supports only Python.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

This deployment procedure describes how to perform a deployment using the
[Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack)
(ASP) and the ADK command line interface (CLI) tool. Using ASP for deployment to
the Agent Engine runtime is an accelerated path, and you should use it for
_*development and testing*_ only. The ASP tool configures Google Cloud resources
that are not strictly necessary for running an ADK agent workflow, and you
should thoroughly review that configuration before using it in a production
deployment.

This deployment guide uses the ASP tool to apply a project template to your
existing project, add deployment artifacts, and prepare your agent project for
deployment. These instructions show you how to use ASP to provision a Google
Cloud project with services needed for deploying your ADK project, as follows:

-   [Prerequisites](#prerequisites-ad): Setup Google Cloud
    account, a project, and install required software.
-   [Prepare your ADK project](#prepare-ad): Modify your
    existing ADK project files to get ready for deployment.
-   [Connect to your Google Cloud project](#connect-ad):
    Connect your development environment to Google Cloud and your Google Cloud
    project.
-   [Deploy your ADK project](#deploy-ad):  Provision
    required services in your Google Cloud project and upload your ADK project code.

For information on testing a deployed agent, see [Test deployed agent](test.md).
For more information on using Agent Starter Pack and its command line tools,
see the
[CLI reference](https://googlecloudplatform.github.io/agent-starter-pack/cli/enhance.html)
and
[Development guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html).

### Prerequisites {#prerequisites-ad}

You need the following resources configured to use this deployment path:

-   **Google Cloud account**: with administrator access to the following:
    -   **Google Cloud Project**: An empty Google Cloud project with
        [billing enabled](https://cloud.google.com/billing/docs/how-to/modify-project).
        For information on creating projects, see
        [Creating and managing projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects).
-   **Python Environment**: A Python version supported by the
    [ASP project](https://googlecloudplatform.github.io/agent-starter-pack/guide/getting-started.html).
-   **uv Tool:** Manage Python development environment and running ASP
    tools. For installation details, see
    [Install uv](https://docs.astral.sh/uv/getting-started/installation/).
-   **Google Cloud CLI tool**: The gcloud command line interface. For
    installation details, see
    [Google Cloud Command Line Interface](https://cloud.google.com/sdk/docs/install).
-   **Make tool**: Build automation tool. This tool is part of most
    Unix-based systems, for installation details, see the
    [Make tool](https://www.gnu.org/software/make/) documentation.

### Prepare your ADK project {#prepare-ad}

When you deploy an ADK project to Agent Engine, you need some additional files
to support the deployment operation. The following ASP command backs up your
project and then adds files to your project for deployment purposes.

These instructions assume you have an existing ADK project that you are modifying
for deployment. If you do not have an ADK project, or want to use a test
project, complete the Python
[Quickstart](/adk-docs/get-started/quickstart/) guide,
which creates a
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
project. The following instructions use the `multi_tool_agent` project as an
example.

To prepare your ADK project for deployment to Agent Engine:

1.  In a terminal window of your development environment, navigate to the
    **parent directory** that contains your agent folder. For example, if your
    project structure is:

    ```
    your-project-directory/
    ├── multi_tool_agent/
    │   ├── __init__.py
    │   ├── agent.py
    │   └── .env
    ```

    Navigate to `your-project-directory/`

1.  Run the ASP `enhance` command to add the files required for deployment into
    your project.

    ```shell
    uvx agent-starter-pack enhance --adk -d agent_engine
    ```

1.  Follow the instructions from the ASP tool. In general, you can accept
    the default answers to all questions. However for the **GCP region**,
    option, make sure you select one of the
    [supported regions](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine)
    for Agent Engine.

When you successfully complete this process, the tool shows the following message:

```
> Success! Your agent project is ready.
```

!!! tip "Note"
    The ASP tool may show a reminder to connect to Google Cloud while
    running, but that connection is *not required* at this stage.

For more information about the changes ASP makes to your ADK project, see
[Changes to your ADK project](#adk-asp-changes).

### Connect to your Google Cloud project {#connect-ad}

Before you deploy your ADK project, you must connect to Google Cloud and your
project. After logging into your Google Cloud account, you should verify that
your deployment target project is visible from your account and that it is
configured as your current project.

To connect to Google Cloud and list your project:

1.  In a terminal window of your development environment, login to your
    Google Cloud account:

    ```shell
    gcloud auth application-default login
    ```

1.  Set your target project using the Google Cloud Project ID:

    ```shell
    gcloud config set project your-project-id-xxxxx
    ```

1.  Verify your Google Cloud target project is set:

    ```shell
    gcloud config get-value project
    ```

Once you have successfully connected to Google Cloud and set your Cloud Project
ID, you are ready to deploy your ADK project files to Agent Engine.

### Deploy your ADK project {#deploy-ad}

When using the ASP tool, you deploy in stages. In the first stage, you run a
`make` command that provisions the services needed to run your ADK workflow on
Agent Engine. In the second stage, the tool uploads your project code to the
Agent Engine service and runs it in the hosted environment

!!! warning "Important"
    *Make sure your Google Cloud target deployment project is set as your ***current
    project*** before performing these steps*. The `make backend` command uses
    your currently set Google Cloud project when it performs a deployment. For
    information on setting and checking your current project, see
    [Connect to your Google Cloud project](#connect-ad).

To deploy your ADK project to Agent Engine in your Google Cloud project:

1.  In a terminal window, ensure you are in the parent directory (e.g.,
    `your-project-directory/`) that contains your agent folder.

1.  Deploy the code from the updated local project into the Google Cloud
development environment, by running the following ASP make command:

    ```shell
    make backend
    ```

Once this process completes successfully, you should be able to interact with
the agent running on Google Cloud Agent Engine. For details on testing the
deployed agent, see
[Test deployed agent](/adk-docs/deploy/agent-engine/test/).

### Changes to your ADK project {#adk-asp-changes}

The ASP tools add more files to your project for deployment. The procedure
below backs up your existing project files before modifying them. This guide
uses the
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
project as a reference example. The original project has the following file
structure to start with:

```
multi_tool_agent/
├─ __init__.py
├─ agent.py
└─ .env
```

After running the ASP enhance command to add Agent Engine deployment
information, the new structure is as follows:

```
multi-tool-agent/
├─ app/                 # Core application code
│   ├─ agent.py         # Main agent logic
│   ├─ agent_engine_app.py # Agent Engine application logic
│   └─ utils/           # Utility functions and helpers
├─ .cloudbuild/         # CI/CD pipeline configurations for Google Cloud Build
├─ deployment/          # Infrastructure and deployment scripts
├─ notebooks/           # Jupyter notebooks for prototyping and evaluation
├─ tests/               # Unit, integration, and load tests
├─ Makefile             # Makefile for common commands
├─ GEMINI.md            # AI-assisted development guide
└─ pyproject.toml       # Project dependencies and configuration
```

See the *README.md* file in your updated ADK project folder for more information.
For more information on using Agent Starter Pack, see the
[Development guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html).

## Test deployed agents

After completing deployment of your ADK agent you should test the workflow in
its new hosted environment. For more information on testing an ADK agent
deployed to Agent Engine, see
[Test deployed agents in Agent Engine](/adk-docs/deploy/agent-engine/test/).