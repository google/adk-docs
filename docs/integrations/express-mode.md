---
catalog_title: Vertex AI express mode
catalog_description: Try development with Vertex AI services at no cost
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["google"]
---

# Google Cloud Vertex AI express mode for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-preview">Preview</span>
</div>

Google Cloud Vertex AI express mode provides a no-cost access tier for
prototyping and development, allowing you to use Vertex AI services without
creating a full Google Cloud Project. This service includes access to many
powerful Vertex AI services, including:

- [Vertex AI SessionService](#vertex-ai-session-service)
- [Vertex AI MemoryBankService](#vertex-ai-memory-bank)

You can sign up for an express mode account using a Gmail account and receive an
API key to use with the ADK. Obtain an API key through the
[Google Cloud Console](https://console.cloud.google.com/expressmode).
For more information, see
[Vertex AI express mode](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview).

!!! example "Preview release"
    The Vertex AI express mode feature is a Preview release. For
    more information, see the
    [launch stage descriptions](https://cloud.google.com/products#product-launch-stages).

??? info "Vertex AI express mode limitations"

    Vertex AI express mode projects are only valid for 90 days and only select
    services are available to be used with limited quota. For example, the number of
    Agent Engines is restricted to 10 and deployment to Agent Engine requires paid
    access. To remove the quota restrictions and use all of Vertex AI's services,
    add a billing account to your express mode project.

## Configure Agent Engine container

When using Vertex AI express mode, create an `AgentEngine` object to enable
Vertex AI management of agent components such as `Session` and `Memory` objects.
With this approach, `Session` objects are handled as children of the
`AgentEngine` object. Before running your agent make sure your environment
variables are set correctly, as shown below:

```env title="agent/.env"
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
```

Next, create your Agent Engine instance using the Vertex AI SDK.

1. Import Vertex AI SDK.

    ```py
    import vertexai
    from vertexai import agent_engines
    ```

2. Initialize the Vertex AI Client with your API key and create an agent engine instance.

    ```py
    # Create Agent Engine with Gen AI SDK
    client = vertexai.Client(
      api_key="YOUR_API_KEY",
    )

    agent_engine = client.agent_engines.create(
      config={
        "display_name": "Demo Agent Engine",
        "description": "Agent Engine for Session and Memory",
      })
    ```

3. Get the Agent Engine name and ID from the response to use with Memories and Sessions.

    ```py
    APP_ID = agent_engine.api_resource.name.split('/')[-1]
    ```

## Manage Sessions with `VertexAiSessionService` {#vertex-ai-session-service}

[`VertexAiSessionService`](/adk-docs/sessions/session.md#sessionservice-implementations)
is compatible with Vertex AI express mode API Keys. You can instead initialize
the session object without any project or location.

```py
# Requires: pip install google-adk[vertexai]
# Plus environment variable setup:
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
from google.adk.sessions import VertexAiSessionService

# The app_name used with this service should be the Reasoning Engine ID or name
APP_ID = "your-reasoning-engine-id"

# Project and location are not required when initializing with Vertex express mode
session_service = VertexAiSessionService(agent_engine_id=APP_ID)
# Use REASONING_ENGINE_APP_ID when calling service methods, e.g.:
# session = await session_service.create_session(app_name=APP_ID, user_id= ...)
```

!!! info "Session Service Quotas"

    For Free express mode Projects, `VertexAiSessionService` has the following quota:

    - 10 Create, delete, or update Vertex AI Agent Engine sessions per minute
    - 30 Append event to Vertex AI Agent Engine sessions per minute

## Manage Memory with `VertexAiMemoryBankService` {#vertex-ai-memory-bank}

[`VertexAiMemoryBankService`](/adk-docs/sessions/memory.md#vertex-ai-memory-bank)
is compatible with Vertex AI express mode API Keys. You can instead initialize
the memory object without any project or location.

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

!!! info "Memory Service Quotas"

    For Free express mode Projects, `VertexAiMemoryBankService` has the following quota:

    - 10 Create, delete, or update Vertex AI Agent Engine memory resources per minute
    - 10 Get, list, or retrieve from Vertex AI Agent Engine Memory Bank per minute

### Code Sample: Weather Agent with Session and Memory

This code sample shows a weather agent that utilizes both
`VertexAiSessionService` and `VertexAiMemoryBankService` for context management,
allowing your agent to recall user preferences and conversations.

*   [Weather Agent with Session and Memory](https://github.com/google/adk-docs/blob/main/examples/python/notebooks/express-mode-weather-agent.ipynb)
    using Vertex AI express mode
