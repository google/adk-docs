# Test deployed agents in Agent Engine

These instructions explain how to test an ADK agent deployed to the
[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
runtime environment. Before using these instructions, you need to have completed
the deployment of your agent to the Agent Engine runtime environment using one
of the [available methods](/adk-docs/deploy/agent-engine/). This guide shows you
how to view, interact, and test your deployed agent through the Google Cloud
Console, and interact with the agent using REST API calls or the Vertex AI SDK
for Python.

## View deployed agent in Cloud Console

To view your deployed agent in the Cloud Console:

-   Navigate to the Agent Engine page in the Google Cloud Console:
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

This page lists all deployed agents in your currently selected Google Cloud
project. If you do not see your agent listed, make sure you have your
target project selected in Google Cloud Console. For more information on
selecting an existing Google Cloud project, see
[Creating and managing projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects).

## Find Google Cloud project information

You need the address and resource identification for your project (`PROJECT_ID`,
`LOCATION_ID`, `RESOURCE_ID`) to be able to test your deployment. You can use Cloud
Console or the `gcloud` command line tool to find this information.

??? note "Vertex AI express mode API key"
    If you are using Vertex AI express mode, you can skip this step and use your API key.

To find your project information with Google Cloud Console:

1.  In the Google Cloud Console, navigate to the Agent Engine page:
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

1.  At the top of the page, select **API URLs**, and then copy the **Query
    URL** string for your deployed agent, which should be in this format:

        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query

To find your project information with the `gcloud` command line tool:

1.  In your development environment, make sure you are authenticated to
    Google Cloud and run the following command to list your project:

    ```shell
    gcloud projects list
    ```

1.  With the Project ID you used for deployment, run this command to get
    the additional details:

    ```shell
    gcloud asset search-all-resources \
        --scope=projects/$(PROJECT_ID) \
        --asset-types='aiplatform.googleapis.com/ReasoningEngine' \
        --format="table(name,assetType,location,reasoning_engine_id)"
    ```

## Test using REST calls

A simple way to interact with your deployed agent in Agent Engine is to use REST
calls with the `curl` tool. This section describes how to check your
connection to the agent and also to test processing of a request by the deployed
agent.

### Check connection to agent

You can check your connection to the running agent using the **Query URL**
available in the Agent Engine section of the Cloud Console. This check does not
execute the deployed agent, but returns information about the agent.

To send a REST call and get a response from deployed agent:

-   In a terminal window of your development environment, build a request
    and execute it:

    === "Google Cloud Project"

        ```shell
        curl -X GET \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            "https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines"
        ```

    === "Vertex AI express mode"

        ```shell
        curl -X GET \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            "https://aiplatform.googleapis.com/v1/reasoningEngines"
        ```

If your deployment was successful, this request responds with a list of valid
requests and expected data formats.

!!! tip "Remove `:query` parameter for connection URL"
    If you use the **Query URL** available in the Agent Engine section of the Cloud
    Console, make sure to remove the `:query` parameter from end of the address.

!!! tip "Access for agent connections"
    This connection test requires the calling user has a valid access token for the
    deployed agent. When testing from other environments, make sure the calling user
    has access to connect to the agent in your Google Cloud project.

### Send an agent request

When getting responses from your agent project, you must first create a
session, receive a Session ID, and then send your requests using that Session
ID. This process is described in the following instructions.

To test interaction with the deployed agent via REST:

1.  In a terminal window of your development environment, create a session
    by building a request using this template:

    === "Google Cloud Project"

        ```shell
        curl \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            -H "Content-Type: application/json" \
            https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

    === "Vertex AI express mode"

        ```shell
        curl \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            -H "Content-Type: application/json" \
            https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

1.  In the response from the previous command, extract the created **Session ID**
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
        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query?alt=sse -d '{
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
        https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query?alt=sse -d '{
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
[Use an Agent Development Kit agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
in the Agent Engine documentation.

## Test using Python

You can use Python code for more sophisticated and repeatable testing of your
agent deployed in Agent Engine. These instructions describe how to create
a session with the deployed agent, and then send a request to the agent for
processing.

### Create a remote session

Use the `remote_app` object to create a connection to a deployed, remote agent:

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

### Sending Multimodal Queries

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
