# Deploy to Vertex AI Agent Engine

<div class="language-support-tag" title="Vertex AI Agent Engine currently supports only Python.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
is a fully managed collection of Google Cloud services enabling developers to deploy, manage,
and scale AI agents in production.

The Agent Engine **runtime** handles the infrastructure to
scale agents in production so you can focus on creating intelligent and
impactful applications.

Hosting your agent on the Agent Engine runtime may incur costs if you go above the free tier. More information can be found on the [Agent Engine pricing page](https://cloud.google.com/vertex-ai/pricing#vertex-ai-agent-engine).

## Deploying with the ADK CLI (`adk deploy agent_engine`)

This section describes how to deploy your agent to Agent Engine, using the simple `adk deploy agent_engine` command.

### What this tutorial covers:

1. [(Prerequisites) Setting up your Google Cloud project](#prerequisites-google-cloud)
2. Preparing up your agent project folder (#define-your-agent)
3. Deploying your agent
4. Testing your agent

### Prerequisites: Setting up your Google Cloud project {#prerequisites-google-cloud}

To deploy your agent to Agent Engine, you will first need a Google Cloud project:

1. **Google Cloud sign-up**:
    * If you're an **existing user** of Google Cloud:
        * Sign in via https://console.cloud.google.com
        * If you previously used a Free Trial that has expired, you may need to [upgrade to a Paid billing account](https://docs.cloud.google.com/free/docs/free-cloud-features#how-to-upgrade).
    * If you're **new user** of Google Cloud:
        * you can sign up for the [Free Trial program](https://docs.cloud.google.com/free/docs/free-cloud-features). The Free Trial gets you a $300 Welcome credit to spend over 91 days on [various Google Cloud products](https://docs.cloud.google.com/free/docs/free-cloud-features#during-free-trial) and you won't be billed. During the Free Trial, you also get access to the [Google Cloud Free Tier](https://docs.cloud.google.com/free/docs/free-cloud-features#free-tier), which gives you free usage of select products up to specified monthly limits, and to product-specific free trials.

2. **Creating a Google Cloud project**
    * If you already have an existing Google Cloud project, you can use that and do not create a new one.
    * If you want to create a new Google Cloud project, you can create a new one on the [Create Project](https://console.cloud.google.com/projectcreate) page.

3. **Getting your Google Cloud project id**
    * You will need your Google Cloud project id, which you can find on your GCP homepage. Make sure to note the project id (alphanumeric with hyphens), _not_ the project number (numeric).

    <img src="../../assets/project-id.png" alt="Google Cloud Project ID">

4. **Enabling Vertex AI in your project**
    * To use Agent Engine, you will need to [enable the Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com). Click on the "Enable" button to enable the API. Once enabled, it should say "API Enabled".

5. **Enabling Cloud Resource Manager API in your project**
    * To use Agent Engine, you will need to [enable the Cloud Resource Manager API](https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview). Click on the "Enable" button to enable the API. Once enabled, it should say "API Enabled".

6. **Creating a Google Cloud Storage (GCS) Bucket**:
    * Agent Engine requires a GCS bucket to stage your agent's code and dependencies for deployment. If already have one, we recommend you create a new one.
    * Create a GCS bucket by following the instructions [here](https://cloud.google.com/storage/docs/creating-buckets). We recommend starting with the default settings when creating your first bucket.
    * Once you have created a storage bucket, you should be able to see it on the [Cloud Storage Buckets page](https://console.cloud.google.com/storage/browser).
    * You will need the GCS bucket path to set as your staging bucket. For example, if your GCS bucket name is "my-bucket", then your bucket path should be "gs://my-bucket".

### Prerequisites: Setting up your coding environment {#prerequisites-coding-env}

Now that you've prepared your Google Cloud project, you can now return to your coding environment (e.g. Terminal, VS Code, etc.).

7. **Authenticating your coding environment with Google Cloud**. 
    * You will need to authenticate your coding environment so that you and your code can interact with Google Cloud. To do so, you will need the gcloud CLI. If you have never used the gcloud CLI, you will need to first [download and install it](https://docs.cloud.google.com/sdk/docs/install-sdk) before continuing with the steps below:

    * Run the following command in your terminal to access your Google Cloud project as a user:

        ```shell
        gcloud auth login
        ```

        You should now see "You are now authenticated with the gcloud CLI!".

    * Run the following command to authenticate your code so that it can work with Google Cloud:

        ```shell
        gcloud auth application-default login
        ```

        You should now see "You are now authenticated with the gcloud CLI!".

    * (Optional) If you need to set or change your default project in gcloud, you can use:

        ```shell
        gcloud config set project MY-PROJECT-ID
        ```

### Define your agent {#define-your-agent}

With your Google Cloud and coding environment prepared, you're ready to deploy your agent.

The instructions will assume that you have an agent project folder, such as:

```shell
multi_tool_agent/
├── .env
├── __init__.py
└── agent.py
```

You can also refer to the sample agent on Github: [multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent).

### Deploy the agent

You can deploy from your terminal using the `adk deploy` command line tool.

This process packages your code, builds it into a container, and deploys it to the managed Agent Engine service. This process can take several minutes.

#### adk deploy agent_engine

The following example deploy command uses the `multi_tool_agent` sample code as the project to be deployed:

```shell
PROJECT_ID=my-project-id
LOCATION=us-central1
GCS_BUCKET=gs://MY-CLOUD-STORAGE-BUCKET

adk deploy agent_engine \
        --project=$PROJECT_ID \
        --region=$LOCATION \
        --staging_bucket=$GCS_BUCKET \
        --display_name="My First Agent" \
        multi_tool_agent  
```

Explanation:

* To learn about the CLI flags, see the [API reference page](https://google.github.io/adk-docs/api-reference/cli/cli.html#adk-deploy-agent-engine) for adk deploy agent_engine.

* For `region`, you can find a list of the supported regions on the [Vertex AI Agent Builder locations page](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine).

#### Output

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
Note that you now have a `RESOURCE_ID` where your agent has been deployed (which in the example above is `751619551677906944`). You will need this along with the other values to use your agent on Agent Engine.

### Using an agent on Agent Engine

To use your agent on Agent Engine, you will need the following:
* your **PROJECT_ID** (e.g. "my-project-id") which you can find on your [project details page](https://console.cloud.google.com/iam-admin/settings)
* your **REGION** (e.g. "us-central1"), that you used to deploy your agent
* your **RESOURCE_ID** (e.g. "751619551677906944"), which you can find on the [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

The query URL will be at:

```shell
https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query
```

Then, to make your requests, follow the detailed instructions on [Agent Engine documentation on using an agent](https://docs.cloud.google.com/agent-builder/agent-engine/use/adk#rest-api).

You can also check the Agent Engine documentation to learn about [how to managed your deployed agent](https://docs.cloud.google.com/agent-builder/agent-engine/manage/overview).

#### Monitoring and verification

*   You can monitor the deployment status in the [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines) in the Google Cloud Console.
*   For additional details, you can visit the Agent Engine documentation [deploying an agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy) and [managing deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview).

<!-- TODO: review remainder below-->

## Test deployed agent {#test-deployment}

Once you have completed the deployment of your agent to Agent Engine, you can
view your deployed agent through the Google Cloud Console, and interact
with the agent using REST calls or the Vertex AI SDK for Python.

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
    PROJECT_ID=MY-PROJECT-ID
    LOCATION=us-central1


    curl -X GET \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/reasoningEngines
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

    === "Google Cloud Project"

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

    === "Vertex AI express mode"

        ```shell
        curl \
        -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
        -H "Content-Type: application/json" \
        https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):streamQuery?alt=sse -d '{
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
