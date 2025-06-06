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
pip install google-cloud-aiplatform[adk,agent_engines]
```

!!!info
    Agent Engine only supported Python version >=3.9 and <=3.12.

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



## Clean up

After you have finished, it is a good practice to clean up your cloud resources.
You can delete the deployed Agent Engine instance to avoid any unexpected
charges on your Google Cloud account.

```python
remote_app.delete(force=True)
```

`force=True` will also delete any child resources that were generated from the deployed agent, such as sessions.
