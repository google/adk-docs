# Deploy to Agent Runtime with Agents CLI

<div class="language-support-tag" title="Agent Runtime currently supports only Python.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

This deployment procedure describes how to perform a deployment using
[Agents CLI in Agent Platform](https://google.github.io/agents-cli/)
and the ADK. Deploying to Agent Runtime via Agents CLI provides an accelerated path to a production-ready environment. Agents CLI automatically configures Google Cloud resources, CI/CD pipelines, and Infrastructure-as-Code (Terraform) to support the entire development lifecycle. As a best practice, always ensure you review the generated configurations to align with your organization’s security and compliance standards before production deployment.

This deployment guide uses Agents CLI to apply a project template to your
existing project, add deployment artifacts, and prepare your agent project for
deployment. These instructions show you how to use Agents CLI to provision a Google
Cloud project with services needed for deploying your ADK project, as follows:

-   [Prerequisites](#prerequisites-ad): Set up Google Cloud
    project, IAM permissions, and install required software.
-   [Prepare your ADK project](#prepare-ad): Modify your
    existing ADK project files to get ready for deployment.
-   [Connect to your Google Cloud project](#connect-ad):
    Connect your development environment to Google Cloud and your Google Cloud
    project.
-   [Deploy your ADK project](#deploy-ad):  Provision
    required services in your Google Cloud project and upload your ADK project code.

For information on testing a deployed agent, see [Test deployed agent](test.md).
For more information on using Agents CLI and its command line tools,
see the
[CLI reference](https://google.github.io/agents-cli/cli/)
and
[Guide](https://google.github.io/agents-cli/).

### Prerequisites {#prerequisites-ad}

You need the following resources configured to use this deployment path:

-   **Google Cloud Project and Permissions**: A Google Cloud project with [billing enabled](https://cloud.google.com/billing/docs/how-to/modify-project).
    You can use an existing project or create a new one. You must have one of the following IAM roles assigned within this project:
    -   **Agent Platform User role** — sufficient to deploy an agent to Agent Runtime.
    -   **Owner role** — required for the full production setup (Terraform infrastructure provisioning, CI/CD pipelines, IAM configuration).

!!! tip "Note"
    An empty project is recommended to avoid conflicts with existing resources.
    For new projects, see [Creating and managing projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects).

-   **Python Environment**: A Python version supported by
    [Agents CLI](https://google.github.io/agents-cli/guide/getting-started/).
-   **uv Tool:** Manage Python development environment and running agents-cli
    tools. For installation details, see
    [Install uv](https://docs.astral.sh/uv/getting-started/installation/).
-   **Google Cloud CLI tool**: The gcloud command line interface. For
    installation details, see
    [Google Cloud Command Line Interface](https://cloud.google.com/sdk/docs/install).
-   **Make tool**: Build automation tool. This tool is part of most
    Unix-based systems, for installation details, see the
    [Make tool](https://www.gnu.org/software/make/) documentation.

### Prepare your ADK project {#prepare-ad}

When you deploy an ADK project to Agent Runtime, you need some additional files
to support the deployment operation. The following Agents CLI command backs up your
project and then adds files to your project for deployment purposes.

These instructions assume you have an existing ADK project that you are modifying
for deployment. If you do not have an ADK project, or want to use a test
project, complete one of the [Get started](/get-started/) guides,
which creates an agent project. The following instructions use the `my_agent`
project as an example.

To prepare your ADK project for deployment to Agent Runtime:

1.  In a terminal window of your development environment, navigate to the
    **parent directory** that contains your agent folder. For example, if your
    project structure is:

    ```
    your-project-directory/
    ├── my_agent/
    │   ├── __init__.py
    │   ├── agent.py
    │   └── .env
    ```

    Navigate to `your-project-directory/`

1.  Run the Agents CLI `scaffold enhance` command to add the files required for deployment into
    your project.

    ```shell
    agents-cli scaffold enhance --deployment-target agent_engine
    ```

1.  Follow the instructions from the Agents CLI tool. In general, you can accept
    the default answers to all questions. However for the **GCP region**,
    option, make sure you select one of the
    [supported regions](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine)
    for Agent Runtime.

When you successfully complete this process, the tool shows the following message:

```
> Success! Your agent project is ready.
```

!!! tip "Note"
    The Agents CLI tool may show a reminder to connect to Google Cloud while
    running, but that connection is *not required* at this stage.

For more information about the changes Agents CLI makes to your ADK project, see
[Changes to your ADK project](#adk-agents-cli-changes).

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
ID, you are ready to deploy your ADK project files to Agent Runtime.

### Deploy your ADK project {#deploy-ad}

When using Agents CLI, you deploy using the `agents-cli deploy` command. This
command builds a container from your agent code, pushes it to a registry, and
deploys it to Agent Runtime in the hosted environment.

!!! warning "Important"
    *Make sure your Google Cloud target deployment project is set as your ***current
    project*** before performing these steps*. The `agents-cli deploy` command uses
    your currently set Google Cloud project when it performs a deployment. For
    information on setting and checking your current project, see
    [Connect to your Google Cloud project](#connect-ad).

To deploy your ADK project to Agent Runtime in your Google Cloud project:

1.  In a terminal window, navigate to your agent project directory (e.g.,
    `your-project-directory/`).

2.  Deploy your agent code to the Google Cloud development environment:

    ```shell
    agents-cli deploy
    ```

    The command reads your `deployment_target` from `pyproject.toml` and deploys
    to the configured target (Agent Runtime, Cloud Run, or GKE).

3.  (Optional) To enable observability features like prompt-response logging and
    content logs, provision the telemetry infrastructure:

    ```shell
    agents-cli infra single-project
    ```

    For more details, see the
    [Observability Guide](https://google.github.io/agents-cli/guide/observability/).

Once this process completes successfully, you should be able to interact with
the agent running on Google Cloud Agent Runtime. For details on testing the
deployed agent, see
[Test deployed agent](/deploy/agent-runtime/test/).

### Changes to your ADK project {#adk-agents-cli-changes}

The Agents CLI tools add more files to your project for deployment. The procedure
below backs up your existing project files before modifying them. This guide
uses the
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
project as a reference example. The original project has the following file
structure to start with:

```
my_agent/
├─ __init__.py
├─ agent.py
└─ .env
```

After running the Agents CLI scaffold enhance command to add Agent Runtime deployment
information, the new structure is as follows:

```
my-agent/
├─ app/                 # Core application code
│   ├─ agent.py         # Main agent logic
│   ├─ agent_engine_app.py # Agent Runtime application logic
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
For more information on using Agents CLI, see the
[Agents CLI documentation](https://google.github.io/agents-cli/).

## Test deployed agents

After completing deployment of your ADK agent you should test the workflow in
its new hosted environment. For more information on testing an ADK agent
deployed to Agent Runtime, see
[Test deployed agents in Agent Runtime](/deploy/agent-runtime/test/).
