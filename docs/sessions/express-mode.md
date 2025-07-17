# Vertex AI Express Mode: Using Vertex AI Sessions and Memory for Free

If you are interested in using either the `VertexAiSessionService` or `VertexAiMemoryBankService` but you don't have a Google Cloud Project, you can sign up for Vertex AI Express Mode and get access
for free and try out these services! You can sign up with an eligible ***gmail*** account [here](https://console.cloud.google.com/expressmode). For more details about Vertex AI Express mode, see the [overview page](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview). 
Once you sign up, get an [API key](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview#api-keys) and you can get started using your local ADK agent with Vertex AI Session and Memory services!

!!! info Vertex AI Express mode limitations

    Vertex AI Express Mode has certain limitations in the free tier. Free Express mode projects are only valid for 90 days and only select services are available to be used with limited quota. For example, the number of Agent Engines is restricted to 10 and deployment to Agent Engine is reserved for the paid tier only. To remove the quota restrictions and use all of Vertex AI's services, add a billing account to your Express Mode project.

## Create an Agent Engine

`Session` objects are children of an `AgentEngine`. When using Vertex AI Express Mode, we can create an empty `AgentEngine` parent to manage all of our `Session` and `Memory` objects.
First, ensure that your enviornment variables are set correctly. For example, in Python:

      ```env title="weather_agent/.env"
      GOOGLE_GENAI_USE_VERTEXAI=TRUE
      GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
      ```

Next, we can create our Agent Engine instance. You can use the Gen AI SDK.

=== "GenAI SDK"
    1. Import Gen AI SDK.

        ```
        from google import genai
        ```

    2. Set Vertex AI to be True, then use a POST request to create the Agent Engine
        
        ```
        # Create Agent Engine with GenAI SDK
        client = genai.Client(vertexai = True)._api_client

        response = client.request(
                http_method='POST',
                path=f'reasoningEngines',
                request_dict={"displayName": "YOUR_AGENT_ENGINE_DISPLAY_NAME", "description": "YOUR_AGENT_ENGINE_DESCRIPTION"},
            )
        response
        ```

    3. Replace `YOUR_AGENT_ENGINE_DISPLAY_NAME` and `YOUR_AGENT_ENGINE_DESCRIPTION` with your use case.
    4. Get the Agent Engine name and ID from the response

        ```
        APP_NAME="/".join(response['name'].split("/")[:6])
        APP_ID=APP_NAME.split('/')[-1]
        ```

## Managing Sessions with a `VertexAiSessionService`

[VertexAiSessionService](session.md###sessionservice-implementations) is compatible with Vertex AI Express mode API Keys. We can 
instead initialize the session object without any project or location.

       ```py
       # Requires: pip install google-adk[vertexai]
       # Plus environment variable setup:
       # GOOGLE_GENAI_USE_VERTEXAI=TRUE
       # GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
       from google.adk.sessions import VertexAiSessionService

       # The app_name used with this service should be the Reasoning Engine ID or name
       APP_ID = "your-reasoning-engine-id"

       # Project and location are not required when initializing with Vertex Express Mode
       session_service = VertexAiSessionService(agent_engine_id=APP_ID)
       # Use REASONING_ENGINE_APP_ID when calling service methods, e.g.:
       # session = await session_service.create_session(app_name=REASONING_ENGINE_APP_ID, user_id= ...)
       ```
!!! info Session Service Quotas

    For Free Express Mode Projects, `VertexAiSessionService` has the following quota:

    - 100 Session Entities
    - 10,000 Event Entities

## Managing Memories with a `VertexAiMemoryBankService`

[VertexAiMemoryBankService](memory.md###memoryservice-implementations) is compatible with Vertex AI Express mode API Keys. We can 
instead initialize the memory object without any project or location.

       ```py
       # Requires: pip install google-adk[vertexai]
       # Plus environment variable setup:
       # GOOGLE_GENAI_USE_VERTEXAI=TRUE
       # GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
       from google.adk.sessions import VertexAiMemoryBankService

       # The app_name used with this service should be the Reasoning Engine ID or name
       APP_ID = "your-reasoning-engine-id"

       # Project and location are not required when initializing with Vertex Express Mode
       memory_service = VertexAiMemoryBankService(agent_engine_id=APP_ID)
       # Generate a memory from that session so the Agent can remember relevant details about the user
       # memory = await memory_service.add_session_to_memory(session)
       ```
!!! info Memory Service Quotas

    For Free Express Mode Projects, `VertexAiMemoryBankService` has the following quota:

    - 200 Memory Entities

## Code Sample: Weather Agent with Session and Memory using Vertex AI Express Mode

In this sample, we create a weather agent that utilizes both `VertexAiSessionService` and `VertexAiMemoryBankService` for context maangement, allowing our agent to recall user prefereneces and conversations!

**[Weather Agent with Session and Memory using Vertex AI Express Mode](https://github.com/google/adk-docs/blob/main/examples/python/notebooks/express-mode-weather-agent.ipynb)**
