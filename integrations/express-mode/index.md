# Google Cloud Agent Platform express mode for ADK

Supported in ADKPython v0.1.0Java v0.1.0Preview

Google Cloud Agent Platform express mode provides a no-cost access tier for prototyping and development, allowing you to use Agent Platform services without creating a full Google Cloud Project. This service includes access to many powerful Agent Platform services, including:

- [Agent Runtime SessionService](#agent-runtime-session-service)
- [Agent Runtime MemoryBankService](#memory-bank)

You can sign up for an express mode account using a Google account and receive an API key to use with the ADK. Obtain an API key through the [Google Cloud Console](https://console.cloud.google.com/expressmode). For more information, see [Agent Platform express mode](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview).

Preview release

The Agent Platform express mode feature is a Preview release. For more information, see the [launch stage descriptions](https://cloud.google.com/products#product-launch-stages).

Agent Platform express mode limitations

Agent Platform express mode projects are only valid for 90 days and only select services are available to be used with limited quota. For example, the number of Agent Runtime instances are restricted to 10 and deployment to Agent Runtime requires paid access. To remove the quota restrictions and use all of Agent Platform's services, add a billing account to your express mode project.

## Configure Agent Runtime container

When using Agent Platform express mode, create an `AgentEngine` object to enable Agent Platform management of agent components such as `Session` and `Memory` objects. With this approach, `Session` objects are handled as children of the `AgentEngine` object. Before running your agent make sure your environment variables are set correctly, as shown below:

agent/.env

```text
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
```

Next, create your Agent Runtime instance using the Agent Platform SDK.

1. Import Agent Platform SDK.

   ```py
   import vertexai
   from vertexai import agent_engines
   ```

1. Initialize the Agent Platform Client with your API key and create an agent engine instance.

   ```py
   # Create Agent Runtime with Gen AI SDK
   client = vertexai.Client(
     api_key="YOUR_API_KEY",
   )

   agent_engine = client.agent_engines.create(
     config={
       "display_name": "Demo Agent Runtime",
       "description": "Agent Runtime for Session and Memory",
     })
   ```

1. Get the Agent Runtime name and ID from the response to use with Memories and Sessions.

   ```py
   APP_ID = agent_engine.api_resource.name.split('/')[-1]
   ```

## Manage Sessions with `VertexAiSessionService`

[`VertexAiSessionService`](/sessions/session#sessionservice-implementations) is compatible with Agent Platform Express Mode API Keys. You can instead initialize the session object without any project or location.

```py
# Requires: pip install google-adk[vertexai]
# Plus environment variable setup:
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
from google.adk.sessions import VertexAiSessionService

# The app_name used with this service should be the Reasoning Engine ID or name
APP_ID = "your-reasoning-engine-id"

# Project and location are not required when initializing with Agent Platform express mode
session_service = VertexAiSessionService(agent_engine_id=APP_ID)
# Use REASONING_ENGINE_APP_ID when calling service methods, e.g.:
# session = await session_service.create_session(app_name=APP_ID, user_id= ...)
```

Session Service Quotas

For Free express mode Projects, `VertexAiSessionService` has the following quota:

- 10 Create, delete, or update Agent Runtime sessions per minute
- 30 Append event to Agent Runtime sessions per minute

## Manage Memory with `VertexAiMemoryBankService`

[`VertexAiMemoryBankService`](/sessions/memory.md#memory-bank) is compatible with Agent Platform express mode API Keys. You can instead initialize the memory object without any project or location.

```py
# Requires: pip install google-adk[vertexai]
# Plus environment variable setup:
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
from google.adk.memory import VertexAiMemoryBankService

# The app_name used with this service should be the Reasoning Engine ID or name
APP_ID = "your-reasoning-engine-id"

# Project and location are not required when initializing with express mode
memory_service = VertexAiMemoryBankService(agent_engine_id=APP_ID)
# Generate a memory from that session so the Agent can remember relevant details about the user
# memory = await memory_service.add_session_to_memory(session)
```

Memory Service Quotas

For Free express mode Projects, `VertexAiMemoryBankService` has the following quota:

- 10 Create, delete, or update Agent Runtime memory resources per minute
- 10 Get, list, or retrieve from Agent Runtime Memory Bank per minute

### Code Sample: Weather Agent with Session and Memory

This code sample shows a weather agent that utilizes both `VertexAiSessionService` and `VertexAiMemoryBankService` for context management, allowing your agent to recall user preferences and conversations.

- [Weather Agent with Session and Memory](https://github.com/google/adk-docs/blob/main/examples/python/notebooks/express-mode-weather-agent.ipynb) using Agent Platform express mode
