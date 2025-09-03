# Deploy to Vertex AI Agent Engine

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="Vertex AI Agent Engine currently supports only Python."}

[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
is a fully managed Google Cloud service enabling developers to deploy, manage,
and scale AI agents in production. Agent Engine handles the infrastructure to
scale agents in production so you can focus on creating intelligent and
impactful applications.

!!! tip "🚀 Accelerate Production Deployment with the [Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack)"
    ```bash
    uvx agent-starter-pack enhance --adk -d agent_engine
    ```
    
    This command upgrades your existing agent project in-place, seamlessly adding:
    
    **Agent Engine deployment** • **Terraform infrastructure** • **Automated CI/CD pipeline** • **Cloud-native Observability** 
    
    [Enhance CLI reference →](https://googlecloudplatform.github.io/agent-starter-pack/cli/enhance.html) | [Development guide →](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html)

This guide provides a step-by-step walkthrough for deploying an agent from your local environment.

## Prerequisites

Before you begin, ensure you have the following:

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
    pip install "google-cloud-aiplatform[adk,agent_engines]" cloudpickle
    ```

## Deployment payload {#payload}

When you deploy your ADK agent workflow to Agent Engine,
the following content is uploaded to the service:

- Your ADK agent code
- Any dependencies declared in your ADK agent code

The deployment *does not* include the ADK API server or the ADK web user
interface libraries. The Agent Engine service provides the libraries for ADK API
server functionality.

## Step 1: Define Your Agent

First, define your agent. You can use the sample agent below, which has two tools (to get weather or retrieve the time in a specified city):
    ```python title="agent.py"
    --8<-- "examples/python/snippets/get-started/multi_tool_agent/agent.py"
    ```

## Step 2: Initialize Vertex AI

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

## Step 3: Prepare the Agent for Deployment

To make your agent compatible with Agent Engine, you need to wrap it in an `AdkApp` object.

```python title="deploy.py"
from vertexai.preview import reasoning_engines

# Wrap the agent in an AdkApp object
app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
```

!!!info
    When an AdkApp is deployed to Agent Engine, it automatically uses `VertexAiSessionService` for persistent, managed session state. This provides multi-turn conversational memory without any additional configuration. For local testing, the application defaults to a temporary, in-memory session service.

## Step 4: Test Your Agent Locally (Optional)

Before deploying, you can test your agent's behavior locally.

The `stream_query` method returns a stream of events that represent the agent's execution trace.

```python title="deploy.py"
# Create a local session to maintain conversation history
session = app.create_session(user_id="u_123")
print(session)
```

Expected output for `create_session` (local):

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743440392.8689594)
```

Send a query to the agent. Copy-paste the following code to your "deploy.py" python script or a notebook.

```py title="deploy.py"
events = list(app.stream_query(
    user_id="u_123",
    session_id=session.id,
    message="whats the weather in new york",
))

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

**Understanding the Output**

When you run the code above, you will see a few types of events:

*   **Tool Call Event**: The model asks to call a tool (e.g., `get_weather`).
*   **Tool Response Event**: The system provides the result of the tool call back to the model.
*   **Model Response Event**: The final text response from the agent after it has processed the tool results.

Expected output for `stream_query` (local):

```console
{'parts': [{'function_call': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

## Step 5: Deploy to Agent Engine

Once you are satisfied with your agent's local behavior, you can deploy it. You can do this using the Python SDK or the `adk` command-line tool.

This process packages your code, builds it into a container, and deploys it to the managed Agent Engine service. This can take several minutes.

=== "ADK CLI"

    You can deploy from your terminal using the `adk` CLI. This is useful for CI/CD pipelines. Make sure your agent definition (`root_agent`) is discoverable.

    ```shell
    adk deploy agent_engine \
        --project=[project] \
        --region=[region] \
        --staging_bucket=[staging_bucket] \
        --display_name=[app_name] \
        path/to/your/agent_folder
    ```
    For more details, see the [ADK CLI reference](https://google.github.io/adk-docs/api-reference/cli/cli.html#adk-deploy).

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
    ```



**Monitoring and Verification**

*   You can monitor the deployment status in the [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines) in the Google Cloud Console.
*   The `remote_app.resource_name` is the unique identifier for your deployed agent. You will need it to interact with the agent. You can also get this from the reponse returned by the ADK CLI command.
*   For additional details, you can visit the Agent Engine documentation [deploying an agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy) and [managing deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview).

## Step 6: Interact with the Deployed Agent

Once deployed, you can interact with your agent using its unique resource name.

### Create a remote session

The remote_app object from the previous step already has the connection. 

```py
# If you are in a new script or used the ADK CLI to deploy, you can connect like this:
# remote_app = reasoning_engines.ReasoningEngine("your-agent-resource-name")
remote_session = remote_app.create_session(user_id="u_456")
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

`id` is the session ID, and `app_name` is the resource ID of the deployed agent on Agent Engine.

### Send queries to your remote agent

```py
for event in remote_app.stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="whats the weather in new york",
):
    print(event)
```

Expected output for `stream_query` (remote):

```console
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

### Sending Multimodal Queries

To send multimodal queries (e.g., including images) to your agent, you can construct the `message` parameter of `stream_query` with a list of `types.Part` objects. Each part can be text or an image.

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

for event in remote_app.stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message=[text_part, image_part],
):
    print(event)
```

!!!note
    While the underlying communication with the model may involve Base64 encoding for images, the recommended and supported method for sending image data to an agent deployed on Agent Engine is by providing a GCS URI.

## Step 7: Clean up

After you have finished, it is a good practice to clean up your cloud resources.
You can delete the deployed Agent Engine instance to avoid any unexpected
charges on your Google Cloud account.

```python
remote_app.delete(force=True)
```

`force=True` will also delete any child resources that were generated from the deployed agent, such as sessions.

You can also delete your deployed agent via the [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines) on Google Cloud.
