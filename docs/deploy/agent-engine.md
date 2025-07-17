# Deploy to Vertex AI Agent Engine

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="Vertex AI Agent Engine currently supports only Python."}

[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
is a fully managed Google Cloud service enabling developers to deploy, manage,
and scale AI agents in production. Agent Engine handles the infrastructure to
scale agents in production so you can focus on creating intelligent and
impactful applications.

```python
from vertexai import agent_engines

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ]
)
```

## Install Vertex AI SDK

Agent Engine is part of the Vertex AI SDK for Python. For more information, you can review the [Agent Engine quickstart documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/quickstart).

### Install the Vertex AI SDK

```shell
pip install "google-cloud-aiplatform[adk,agent_engines]" cloudpickle
```

!!!info
    Agent Engine only supports Python version >=3.9 and <=3.13.

### Initialization

```py
import vertexai

PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://your-google-cloud-storage-bucket"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)
```

For `LOCATION`, you can check out the list of [supported regions in Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions).

### Create your agent

You can use the sample agent below, which has two tools (to get weather or retrieve the time in a specified city):

```python
--8<-- "examples/python/snippets/get-started/multi_tool_agent/agent.py"
```

### Prepare your agent for Agent Engine

Use `reasoning_engines.AdkApp()` to wrap your agent to make it deployable to Agent Engine

```py
from vertexai.preview import reasoning_engines

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
```

!!!info
    When an AdkApp is deployed to Agent Engine, it automatically uses `VertexAiSessionService` for persistent, managed session state. This provides multi-turn conversational memory without any additional configuration. For local testing, the application defaults to a temporary, in-memory session service.

### Try your agent locally

You can try it locally before deploying to Agent Engine.

#### Create session (local)

```py
session = app.create_session(user_id="u_123")
session
```

Expected output for `create_session` (local):

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743440392.8689594)
```

#### List sessions (local)

```py
app.list_sessions(user_id="u_123")
```

Expected output for `list_sessions` (local):

```console
ListSessionsResponse(session_ids=['c6a33dae-26ef-410c-9135-b434a528291f'])
```

#### Get a specific session (local)

```py
session = app.get_session(user_id="u_123", session_id=session.id)
session
```

Expected output for `get_session` (local):

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743681991.95696)
```

#### Send queries to your agent (local)

```py
for event in app.stream_query(
    user_id="u_123",
    session_id=session.id,
    message="whats the weather in new york",
):
print(event)
```

Expected output for `stream_query` (local):

```console
{'parts': [{'function_call': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

### Deploy your agent to Agent Engine

```python
from vertexai import agent_engines

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"   
    ]
)
```

This step may take several minutes to finish. Each deployed agent has a unique identifier. You can run the following command to get the resource_name identifier for your deployed agent:

```python
remote_app.resource_name
```

The response should look like the following string:

```
f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
```

For additional details, you can visit the Agent Engine documentation [deploying an agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy) and [managing deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview).

### Try your agent on Agent Engine

#### Create session (remote)

```py
remote_session = remote_app.create_session(user_id="u_456")
remote_session
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

#### List sessions (remote)

```py
remote_app.list_sessions(user_id="u_456")
```

#### Get a specific session (remote)

```py
remote_app.get_session(user_id="u_456", session_id=remote_session["id"])
```

!!!note
    While using your agent locally, session ID is stored in `session.id`, when using your agent remotely on Agent Engine, session ID is stored in `remote_session["id"]`.

#### Send queries to your agent (remote)

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

## Deploying Agents with MCP Tools

When deploying an agent to Agent Engine that depends on an `MCPToolset`, you must ensure the MCP server is accessible over the network and that credentials are handled securely.

### Architecture

*   **External MCP Server**: The MCP server cannot be a local subprocess (`StdioConnectionParams` is not supported). It must be deployed as a separate, network-accessible service (e.g., on Cloud Run, GKE, or another compute platform).
*   **Network Connectivity**: Ensure that the Agent Engine environment has the necessary VPC network configuration and firewall rules to reach your MCP server's endpoint.
*   **Connection Parameters**: In your agent code, use `StreamableHTTPConnectionParams` to specify the URL of your deployed MCP server.

### Secure Credential Management

Handling authentication tokens and other secrets is critical for security.

*   **Use Secret Manager**: The recommended best practice is to store credentials like API tokens in [Google Cloud Secret Manager](https://cloud.google.com/secret-manager).
*   **Runtime Access**: Your agent code, running within Agent Engine, should be granted an IAM role (e.g., `Secret Manager Secret Accessor`) that allows it to fetch the secret value at runtime. This avoids exposing secrets in environment variables or source code.
*   **Pass Secrets to Tools**: Once fetched from Secret Manager, the token can be used to construct the `AuthCredential` for your `MCPToolset`.

### Example: Agent with MCP Toolset for Agent Engine

Your agent definition would be packaged for Agent Engine, fetching credentials securely.

```python
# In your agent.py to be deployed to Agent Engine
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from google.adk.auth import AuthCredential, AuthCredentialTypes, HttpAuth, HttpCredentials
from google.adk.auth.auth_schemes import HTTPBearer
# You would also need the Secret Manager client library
# from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    # Placeholder for logic to fetch a secret from Google Secret Manager
    # client = secretmanager.SecretManagerServiceClient()
    # name = f"projects/{os.environ['GCP_PROJECT']}/secrets/{secret_id}/versions/latest"
    # response = client.access_secret_version(name=name)
    # return response.payload.data.decode("UTF-8")
    # For deployment, you would use the real client. For local testing, you might use an env var.
    return os.environ.get(secret_id)

# Get configuration from environment variables or secrets
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL")
MCP_AUTH_TOKEN = get_secret("MCP_API_TOKEN_SECRET_ID")

if not MCP_SERVER_URL or not MCP_AUTH_TOKEN:
    raise ValueError("MCP server configuration or token is missing.")

root_agent = LlmAgent(
    model='gemini-1.5-flash',
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(url=MCP_SERVER_URL),
            auth_scheme=HTTPBearer(),
            auth_credential=AuthCredential(
                auth_type=AuthCredentialTypes.HTTP,
                http=HttpAuth(scheme="bearer", credentials=HttpCredentials(token=MCP_AUTH_TOKEN))
            )
        )
    ],
    # ... other agent parameters
)
```

When deploying with `agent_engines.create`, you would need to ensure the `requirements` list includes `google-cloud-secret-manager` and that the necessary environment variables (`MCP_SERVER_URL`, `MCP_API_TOKEN_SECRET_ID`, `GCP_PROJECT`) are available to the runtime.

## Clean up

After you have finished, it is a good practice to clean up your cloud resources.
You can delete the deployed Agent Engine instance to avoid any unexpected
charges on your Google Cloud account.

```python
remote_app.delete(force=True)
```

`force=True` will also delete any child resources that were generated from the deployed agent, such as sessions.