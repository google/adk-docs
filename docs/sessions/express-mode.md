# Vertex Express Mode: Using Sessions and Memory for Free

If you are interested in using either the `VertexAiSessionService` or `VertexAiMemoryService` but you don't have a Google Cloud Project, you can use sign up to Vertex Express Mode and get access
for free and try out these services! You can sign up with an eligible ***gmail*** account [here](https://console.cloud.google.com/expressmode). For more details about Vertex Express mode, see the [overview page](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview). 
Once you sign up, get an [API key](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview#api-keys) and you can get started using your local ADK agent with Vertex AI Session and Memory services!

## Create an Agent Engine

`Session` objects are children of an `AgentEngine`. When using Vertex Express Mode, we can create an empty `AgentEngine` parent to manage all of our `Session` and `Memory` objects.
First, ensure that your enviornment variables are set correctly. For example, in Python:

          ```env title="multi_tool_agent/.env"
          GOOGLE_GENAI_USE_VERTEXAI=TRUE
          GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
          ```

Next, we can create our Agent Engine instance. You can use the vertex ai SDK, or the Gen AI sdk.

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

=== "Vertex AI SDK"
    1. Install Vertex AI SDK.

        ```
        pip install google-cloud-aiplatform[adk,agent_engines]
        ```
  
    2. Initialization
        
        ```
        import vertexai
        from vertexai import agent_engines
        
        vertexai.init(api_key=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE)
        ```

    3. Create your Agent Engine instance.

        ```
        # Create Agent Engine with Vertex AI SDK
        agent_engine = agent_engines.create(displayName= "YOUR_AGENT_ENGINE_DISPLAY_NAME", description= "YOUR_AGENT_ENGINE_DESCRIPTION")
        ```
    4. Get the Agent Engine name and ID from the response

        ```
        APP_NAME=agent_engine.resource_name
        APP_ID=APP_NAME.split('/')[-1]
        ```

## Managing Sessions with a `VertexAiSessionService`

[VertexAiSessionService](session.md###sessionservice-implementations) is compatible with Vertex Express mode API Keys. We can 
instead initialize the session object without any project or location.

           ```py
           # Requires: pip install google-adk[vertexai]
           # Plus environment variable setup:
           # GOOGLE_GENAI_USE_VERTEXAI=TRUE
           # GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
           from google.adk.sessions import VertexAiSessionService

           # The app_name used with this service should be the Reasoning Engine ID or name
           REASONING_ENGINE_APP_ID = "your-reasoning-engine-id"

           # Project and location are not required when initializing with Vertex Express Mode
           session_service = VertexAiSessionService()
           # Use REASONING_ENGINE_APP_ID when calling service methods, e.g.:
           # session_service = await session_service.create_session(app_name=REASONING_ENGINE_APP_ID, user_id= ...)
           ```

## Managing Memories with a `VertexAiMemoryService`

[VertexAiMemoryService](memory.md###memoryservice-implementations) is compatible with Vertex Express mode API Keys. We can 
instead initialize the memory object without any project or location.

           ```py
           # Requires: pip install google-adk[vertexai]
           # Plus environment variable setup:
           # GOOGLE_GENAI_USE_VERTEXAI=TRUE
           # GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
           from google.adk.sessions import VertexAiMemoryService

           # The app_name used with this service should be the Reasoning Engine ID or name
           REASONING_ENGINE_APP_ID = "your-reasoning-engine-id"

           # Project and location are not required when initializing with Vertex Express Mode
           session_service = VertexAiMemoryService(REASONING_ENGINE_APP_ID)
           # Generate a memory from that session so the Agent can remember relevant details about the user
           # memory_service.add_session_to_memory(session)
           ```
## Vertex Express Mode Free Tier Quotas

If you strictly use Vertex Express mode for free, your project will have limited quotas. See the table below for the related Agent Engine quotas. If you want to remove these restrictions, add a billing account to enable deployment to agent engine and unlimited sessions, session events, and memories.

| Service    | Quota |
| -------- | ------- |
| Maximum number of Agent Engine resources	  | 10    |
| Maximum number of Session resources	 | 100     |
| Maximum number of Session Event resources	 | 10,000     |
| Maximum number of Memory resources	    | 200    |


## Code Sample: Weather Agent with Session and Memory using Vertex Express Mode

In this sample, we create a weather agent that utilizes both `VertexAiSessionService` and `VertexAiMemoryService` for context maangement, allowing our agent to recall user prefereneces and conversations!

??? "Code"
    === "Python"

          ```py
          import os
          import asyncio
          from google import adk
          from google import genai
          from google.adk.agents import Agent
          from google.adk.sessions import VertexAiSessionService
          from google.adk.sessions import VertexAiMemoryService
          from google.adk.runners import Runner
          from google.genai import types # For creating message Content/Parts
          
          # API Key (Get from Vertex Express Mode)
          os.environ["GOOGLE_API_KEY"] = "INSERT_API_KEY_HERE"
          # Set vertex to true
          os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
          
          # Use an allowlisted model for EasyGCP, we will use gemini 2.0. Find all allowlisted models here: https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview#models
          MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash-001"
          
          # Define the get_weather Tool
          def get_weather(city: str) -> dict:
              """Retrieves the current weather report for a specified city.
          
              Args:
                  city (str): The name of the city (e.g., "New York", "London", "Tokyo").
          
              Returns:
                  dict: A dictionary containing the weather information.
                        Includes a 'status' key ('success' or 'error').
                        If 'success', includes a 'report' key with weather details.
                        If 'error', includes an 'error_message' key.
              """
              print(f"--- Tool: get_weather called for city: {city} ---") # Log tool execution
              city_normalized = city.lower().replace(" ", "") # Basic normalization
          
              # Mock weather data
              mock_weather_db = {
                  "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
                  "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
                  "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
              }
          
              if city_normalized in mock_weather_db:
                  return mock_weather_db[city_normalized]
              else:
                  return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}
          
          # Define the Weather Agent
          weather_agent = Agent(
              name="weather_agent_v1",
              model=MODEL_GEMINI_2_0_FLASH,
              description="Provides weather information for specific cities.",
              instruction="You are a helpful weather assistant. "
                          "When the user asks for the weather in a specific city, "
                          "use the 'get_weather' tool to find the information. "
                          "If the tool returns an error, inform the user politely. "
                          "If the tool is successful, present the weather report clearly.",
              tools=[get_weather, adk.tools.preload_memory_tool.PreloadMemoryTool()], # Pass the function directly
          )
          
          # Create Agent Engine with GenAI SDK
          client = genai.Client(vertexai = True)._api_client
          client._http_options.base_url = (
                  'https://staging-aiplatform.sandbox.googleapis.com'
              )
          response = client.request(
                  http_method='POST',
                  path=f'reasoningEngines',
                  request_dict={"displayName": "Demo-Agent-Engine", "description": "ADK Vertex Express mode demo"},
              )
          
          # Save Agent Engine name and ID
          APP_NAME="/".join(response['name'].split("/")[:6])
          APP_ID=APP_NAME.split('/')[-1]
          print(f"Agent Engine created with ID: '{APP_ID}'.")
          
          # Set up Vertex Session and Memory services
          session_service = VertexAiSessionService()
          memory_service = AgentEngineMemoryBankService(APP_NAME)
          
          USER_ID = "INSERT_USER_ID_HERE"
          session = await session_service.create_session(app_name=APP_ID, user_id=USER_ID)
          SESSION_ID = session.id
          print(f"Session created: App='{APP_ID}', User='{USER_ID}', Session='{SESSION_ID}'")
          
          # Create your runner
          runner = Runner(
              agent=weather_agent, # The agent we want to run
              app_name=APP_ID,   # Associates runs with our app
              session_service=session_service, # Uses vertex session service
              memory_service=memory_service # Uses vertex memory service
          )
          print(f"Runner created for agent '{runner.agent.name}'.")
          
          # Define Agent Interaction Function
          async def call_agent_async(query: str, runner, user_id, session_id):
            """Sends a query to the agent and prints the final response."""
            print(f"\n>>> User Query: {query}")
          
            # Prepare the user's message in ADK format
            content = types.Content(role='user', parts=[types.Part(text=query)])
          
            final_response_text = "Agent did not produce a final response." # Default
          
            # Key Concept: run_async executes the agent logic and yields Events.
            # We iterate through events to find the final answer.
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                # You can uncomment the line below to see *all* events during execution
                print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")
          
                # Key Concept: is_final_response() marks the concluding message for the turn.
                if event.is_final_response():
                    if event.content and event.content.parts:
                       # Assuming text response in the first part
                       final_response_text = event.content.parts[0].text
                    elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                       final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                    # Add more checks here if needed (e.g., specific error codes)
                    break # Stop processing events once the final response is found
          
            print(f"<<< Agent Response: {final_response_text}")
          
          # Run the Initial Conversation
          # We need an async function to await our interaction helper
          async def run_conversation():
              await call_agent_async("What is the weather like in London?",
                                                 runner=runner,
                                                 user_id=USER_ID,
                                                 session_id=SESSION_ID)
          
              await call_agent_async("How about Paris?",
                                                 runner=runner,
                                                 user_id=USER_ID,
                                                 session_id=SESSION_ID) # Expecting the tool's error message
          
              await call_agent_async("Tell me the weather in New York",
                                                 runner=runner,
                                                 user_id=USER_ID,
                                                 session_id=SESSION_ID)
              await call_agent_async("I prefer the weather in New York, that sounds nicer than the weather in London",
                                                 runner=runner,
                                                 user_id=USER_ID,
                                                 session_id=SESSION_ID)
              await call_agent_async("What cities did I ask you about previously?",
                                                 runner=runner,
                                                 user_id=USER_ID,
                                                 session_id=SESSION_ID)
          
          # Execute the conversation using await in an async context (like Colab/Jupyter)
          await run_conversation()
          # OR
          # Uncomment the following lines if running as a standard Python script (.py file):
          # import asyncio
          # if __name__ == "__main__":
          #     try:
          #         asyncio.run(run_conversation())
          #     except Exception as e:
          #         print(f"An error occurred: {e}")
          
          # Create a memory based on the previous conversation
          memory_service.add_session_to_memory(session)
          print("Successfully created a memory based on the previous session")
          
          # Test the Agent Memory
          # Create a new session, and lets see if it will remember our preferences based on our user id
          new_session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
          SESSION_ID = new_session.id
          
          print(f"New Session created: App='{APP_ID}', User='{USER_ID}', Session='{SESSION_ID}'")
          
          await call_agent_async("What weather do I prefer?",
                                                 runner=runner,
                                                 user_id=USER_ID,
                                                 session_id=SESSION_ID)
