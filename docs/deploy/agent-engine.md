# Deploy to Vertex AI Agent Engine

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="Vertex AI Agent Engine currently supports only Python."}

[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
is a fully managed Google Cloud service enabling developers to deploy, manage,
and scale AI agents in production. Agent Engine handles the infrastructure to
scale agents in production so you can focus on creating intelligent and
impactful applications. This guide provides an accelerated deployment
instruction set for when you want to deploy an ADK project quickly, and a
standard, step-by-step set of instructions for when you want to carefully manage
deploying an agent to Agent Engine.

## Accelerated deployment

This section describes how to perform a deployment using the
[Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack)
(ASP) and the ADK command line interface (CLI) tool. This approach uses the ASP
tool to apply a project template to your existing project, add deployment
artifacts, and prepare your agent project for deployment. These instructions
show you how to use ASP to provision a Google Cloud project with services needed
for deploying your ADK project, as follows:

-   [Prerequisites](#prerequisites-ad): Setup Google Cloud
    account, a project, and install required software.
-   [Prepare your ADK project](#prepare-ad): Modify your
    existing ADK project files to get ready for deployment.
-   [Connect to your Google Cloud project](#connect-ad):
    Connect your development environment to Google Cloud and your Google Cloud
    project.
-   [Deploy your ADK project](#deploy-ad):  Provision
    required services in your Google Cloud project and upload your ADK project code.

For information on testing a deployed agent, see [Test deployed agent](#test-deployment).
For more information on using Agent Starter Pack and its command line tools,
see the
[CLI reference](https://googlecloudplatform.github.io/agent-starter-pack/cli/enhance.html)
and
[Development guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html).


### Prerequisites {#prerequisites-ad}

You need the following resources configured to use this deployment path:

-   **Google Cloud account**, with administrator access to:
-   **Google Cloud Project**: An empty Google Cloud project with
    [billing enabled](https://cloud.google.com/billing/docs/how-to/modify-project).
    For information on creating projects, see
    [Creating and managing projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects).
-   **Python Environment**: A Python version between 3.9 and 3.13.
-   **UV Tool:** Manage Python development environment and running ASP
    tools. For installation details, see 
    [Install UV](https://docs.astral.sh/uv/getting-started/installation/).
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

1.  Run the ASP `enhance` command to add the needed files required for
    deployment into your project.

    ```shell
    uvx agent-starter-pack enhance --adk -d agent_engine
    ```

1.  Follow the instructions from the ASP tool. In general, you can accept
    the default answers to all questions. However for the **GCP region**, 
    option, make sure you select one of the 
    [supported regions for Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions).

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
Agent Engine. In the second stage, your project code is uploaded to the Agent
Engine service and the agent project is executed.

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
deployed agent, see the next section.

Once this process completes successfully, you should be able to interact with
the agent running on Google Cloud Agent Engine. For details on testing the
deployed agent, see 
[Test deployed agent](#test-deployment).

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

See the README.md file in your updated ADK project folder for more information.
For more information on using Agent Starter Pack, see the
[Development guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html).

## Standard deployment

This section describes how to perform a deployment to Agent Engine step-by-step.
These instructions are more appropriate if you want to carefully manage your
deployment settings, or are modifying an existing deployment with Agent Engine.

### Prerequisites

These instructions assume you have already defined an ADK project. If you do not
have an ADK project, see the instructions for creating a test project in
[Define your agent](#define-your-agent).

Before starting deployment procedure, ensure you have the following:

1.  **Google Cloud Project**: A Google Cloud project with the [Vertex AI API enabled](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com).

2.  **Authenticated gcloud CLI**: You need to be authenticated with Google Cloud. Run the following command in your terminal:
    ```shell
    gcloud auth application-default login
    ```

3.  **Google Cloud Storage (GCS) Bucket**: Agent Engine requires a GCS bucket to stage your agent's code and dependencies for deployment. If you don't have a bucket, create one by following the instructions [here](https://cloud.google.com/storage/docs/creating-buckets).

4.  **Python Environment**: A Python version between 3.9 and 3.13.

5.  **Install Vertex AI SDK**

    Agent Engine is part of the Vertex AI SDK for Python. For more information, you can review the [Agent Engine quickstart documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/quickstart).

    ```shell
    pip install google-cloud-aiplatform[adk,agent_engines]>=1.111
    ```

### Define your agent {#define-your-agent}

These instructions assume you have an existing ADK project that you are modifying
for deployment. If you do not have an ADK project, or want to use a test
project, complete the Python
[Quickstart](/adk-docs/get-started/quickstart/) guide,
which creates a
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
project. The following instructions use the `multi_tool_agent` project as an
example.

### Initialize Vertex AI

Next, initialize the Vertex AI SDK. This tells the SDK which Google Cloud project and region to use, and where to stage files for deployment.

!!! tip "For IDE Users"
    You can place this initialization code in a separate `deploy.py` script along with the deployment logic for the following steps: 3 through 6.

```python title="deploy.py"
import vertexai
from agent import root_agent # modify this if your agent is not in agent.py

# TODO: Fill in these values for your project
PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"  # For other options, see https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions
STAGING_BUCKET = "gs://your-gcs-bucket-name"

# Initialize the Vertex AI SDK
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)
```

### Prepare the agent for deployment

To make your agent compatible with Agent Engine, you need to wrap it in an `AdkApp` object.

```python title="deploy.py"
from vertexai import agent_engines

# Wrap the agent in an AdkApp object
app = agent_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
```

!!!info
    When an AdkApp is deployed to Agent Engine, it automatically uses `VertexAiSessionService` for persistent, managed session state. This provides multi-turn conversational memory without any additional configuration. For local testing, the application defaults to a temporary, in-memory session service.

### Test agent locally (optional)

Before deploying, you can test your agent's behavior locally.

The `async_stream_query` method returns a stream of events that represent the agent's execution trace.

```python title="deploy.py"
# Create a local session to maintain conversation history
session = await app.async_create_session(user_id="u_123")
print(session)
```

Expected output for `create_session` (local):

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743440392.8689594)
```

Send a query to the agent. Copy-paste the following code to your "deploy.py" python script or a notebook.

```py title="deploy.py"
events = []
async for event in app.async_stream_query(
    user_id="u_123",
    session_id=session.id,
    message="whats the weather in new york",
):
    events.append(event)

# The full event stream shows the agent's thought process
print("--- Full Event Stream ---")
for event in events:
    print(event)

# For quick tests, you can extract just the final text response
final_text_responses = [
    e for e in events
    if e.get("content", {}).get("parts", [{}])[0].get("text")
    and not e.get("content", {}).get("parts", [{}])[0].get("function_call")
]
if final_text_responses:
    print("\n--- Final Response ---")
    print(final_text_responses[0]["content"]["parts"][0]["text"])
```

#### Understanding the output

When you run the code above, you will see a few types of events:

*   **Tool Call Event**: The model asks to call a tool (e.g., `get_weather`).
*   **Tool Response Event**: The system provides the result of the tool call back to the model.
*   **Model Response Event**: The final text response from the agent after it has processed the tool results.

Expected output for `async_stream_query` (local):

```console
{'parts': [{'function_call': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

### Deploy to agent engine

Once you are satisfied with your agent's local behavior, you can deploy it. You can do this using the Python SDK or the `adk` command-line tool.

This process packages your code, builds it into a container, and deploys it to the managed Agent Engine service. This process can take several minutes.

=== "ADK CLI"

    You can deploy from your terminal using the `adk deploy` command line tool.
    The following example deploy command uses the `multi_tool_agent` sample
    code as the project to be deployed:

    ```shell
    adk deploy agent_engine \
        --project=my-cloud-project-xxxxx \
        --region=us-central1 \
        --staging_bucket=gs://my-cloud-project-staging-bucket-name \
        --display_name="My Agent Name" \
        /multi_tool_agent
    ```

    Find the names of your available storage buckets in the
    [Cloud Storage Bucket](https://pantheon.corp.google.com/storage/browser)
    section of your deployment project in the Google Cloud Console.
    For more details on using the `adk deploy` command, see the 
    [ADK CLI reference](/adk-docs/api-reference/cli/cli.html#adk-deploy).

    !!! tip
        Make sure your main ADK agent definition (`root_agent`) is 
        discoverable when deploying your ADK project.

=== "Python"

    This code block initiates the deployment from a Python script or notebook.

    ```python title="deploy.py"
    from vertexai import agent_engines

    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]"   
        ]
    )

    print(f"Deployment finished!")
    print(f"Resource Name: {remote_app.resource_name}")
    # Resource Name: "projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
    #       Note: The PROJECT_NUMBER is different than the PROJECT_ID.
    ```

#### Monitoring and verification

*   You can monitor the deployment status in the [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines) in the Google Cloud Console.
*   The `remote_app.resource_name` is the unique identifier for your deployed agent. You will need it to interact with the agent. You can also get this from the response returned by the ADK CLI command.
*   For additional details, you can visit the Agent Engine documentation [deploying an agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy) and [managing deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview).

## Test deployed agent {#test-deployment}

Once you have completed the deployment of your agent to Agent Engine, you can
view your deployed agent through the Google Cloud Console, and interact
with the agent using REST calls or the Vertex AI SDK for Python.

To view your deployed agent in the Cloud Console:

-   Navigate to the Agent Engine page in the Google Cloud Console:
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

This page lists all deployed agents in your currently selected Google Cloud 
project. If you do not see your agent listed, make sure you have your
target project selected in Google Cloud Console. For more information on
selecting an exising Google Cloud project, see
[Creating and managing projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects).

### Find Google Cloud project information

You need the address and resource identification for your project (`PROJECT_ID`,
`LOCATION`, `RESOURCE_ID`) to be able to test your deployment. You can use Cloud
Console or the `gcloud` command line tool to find this information. 

To find your project information with Google Cloud Console:

1.  In the Google Cloud Console, navigate to the Agent Engine page:
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

1.  At the top of the page, select **API URLs**, and then copy the **Query
    URL** string for your deployed agent, which should be in this format:

        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query

To find your project information with `gloud`:

1.  In your development environment, make sure you are authenticated to 
    Google Cloud and run the following command to list your project:

    ```shell
    gcloud projects list
    ```

1.  Take the Project ID used for deployment and run this command to get
    the additional details:

    ```shell
    gcloud asset search-all-resources \
        --scope=projects/$(PROJECT_ID) \
        --asset-types='aiplatform.googleapis.com/ReasoningEngine' \
        --format="table(name,assetType,location,reasoning_engine_id)"
    ```

### Test using REST calls

A simple way to interact with your deployed agent in Agent Engine is to use REST
calls with the `curl` tool. This section describes the how to check your
connection to the agent and also to test processing of a request by the deployed
agent.

#### Check connection to agent

You can check your connection to the running agent using the **Query URL**
available in the Agent Engine section of the Cloud Console. This check does not
execute the deployed agent, but returns information about the agent.

To send a REST call get a response from deployed agent:

-   In a terminal window of your development environment, build a request
    and execute it:

    ```shell
    curl -X GET \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        "https://$(LOCATION)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION)/reasoningEngines"
    ```

If your deployment was successful, this request responds with a list of valid
requests and expected data formats. 

!!! tip "Access for agent connections"
    This connection test requires the calling user has a valid access token for the
    deployed agent. When testing from other environments, make sure the calling user
    has access to connect to the agent in your Google Cloud project.

#### Send an agent request

When getting responses from your agent project, you must first create a
session, receive a Session ID, and then send your requests using that Session
ID. This process is described in the following instructions.

To test interaction with the deployed agent via REST:

1.  In a terminal window of your development environment, create a session
    by building a request using this template:

    ```shell
    curl \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        https://$(LOCATION)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION)/reasoningEngines/$(RESOURCE_ID):query \
        -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
    ```

1.  In the response to the previous command, extract the created **Session ID**
    from the **id** field:

    ```json
    {
        "output": {
            "userId": "u_123",
            "lastUpdateTime": 1757690426.337745,
            "state": {},
            "id": "4857885913439920384", # Session ID
            "appName": "9888888855577777776",
            "events": []
        }
    }
    ```

1.  In a terminal window of your development environment, send a message to
    your agent by building a request using this template and the Session ID
    created in the previous step:

    ```shell
    curl \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    https://$(LOCATION)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION)/reasoningEngines/$(RESOURCE_ID):streamQuery?alt=sse -d '{
    "class_method": "async_stream_query",
    "input": {
        "user_id": "u_123",
        "session_id": "4857885913439920384",
        "message": "Hey whats the weather in new york today?",
    }
    }'
    ```

This request should generate a response from your deployed agent code in JSON
format. For more information about interacting with a deployed ADK agent in
Agent Engine using REST calls, see
[Manage deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview#console)
and
[Use a Agent Development Kit agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
in the Agent Engine documentation.

### Test using Python

You can use Python code for more sophisticated and repeatable testing of your
agent deployed in Agent Engine. These instructions describe how to create
a session with the deployed agent, and then send a request to the agent for
processing.

#### Create a remote session

Use the `remote_app` object to create a connection to deployed, remote agent:

```py
# If you are in a new script or used the ADK CLI to deploy, you can connect like this:
# remote_app = agent_engines.get("your-agent-resource-name")
remote_session = await remote_app.async_create_session(user_id="u_456")
print(remote_session)
```

Expected output for `create_session` (remote):

```console
{'events': [],
'user_id': 'u_456',
'state': {},
'id': '7543472750996750336',
'app_name': '7917477678498709504',
'last_update_time': 1743683353.030133}
```

The `id` value is the session ID, and `app_name` is the resource ID of the
deployed agent on Agent Engine.

#### Send queries to your remote agent

```py
async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="whats the weather in new york",
):
    print(event)
```

Expected output for `async_stream_query` (remote):

```console
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

For more information about interacting with a deployed ADK agent in
Agent Engine, see
[Manage deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)
and
[Use a Agent Development Kit agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
in the Agent Engine documentation.

#### Sending Multimodal Queries

To send multimodal queries (e.g., including images) to your agent, you can construct the `message` parameter of `async_stream_query` with a list of `types.Part` objects. Each part can be text or an image.

To include an image, you can use `types.Part.from_uri`, providing a Google Cloud Storage (GCS) URI for the image.

```python
from google.genai import types

image_part = types.Part.from_uri(
    file_uri="gs://cloud-samples-data/generative-ai/image/scones.jpg",
    mime_type="image/jpeg",
)
text_part = types.Part.from_text(
    text="What is in this image?",
)

async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message=[text_part, image_part],
):
    print(event)
```

!!!note 
    While the underlying communication with the model may involve Base64
    encoding for images, the recommended and supported method for sending image
    data to an agent deployed on Agent Engine is by providing a GCS URI.

## Deployment payload {#payload}

When you deploy your ADK agent project to Agent Engine,
the following content is uploaded to the service:

- Your ADK agent code
- Any dependencies declared in your ADK agent code

The deployment *does not* include the ADK API server or the ADK web user
interface libraries. The Agent Engine service provides the libraries for ADK API
server functionality.

## Clean up deployments

If you have performed deployments as tests, it is a good practice to clean up
your cloud resources after you have finished. You can delete the deployed Agent
Engine instance to avoid any unexpected charges on your Google Cloud account.

```python
remote_app.delete(force=True)
```

The `force=True` parameter also deletes any child resources that were generated
from the deployed agent, such as sessions. You can also delete your deployed
agent via the
[Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)
on Google Cloud.
