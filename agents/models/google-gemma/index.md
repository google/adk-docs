# Google Gemma models for ADK agents

Supported in ADKPython v0.1.0

ADK agents can use the [Google Gemma](https://ai.google.dev/gemma/docs) family of generative AI models that offer a wide range of capabilities. ADK supports many Gemma features, including [Tool Calling](/tools-custom/) and [Structured Output](/agents/llm-agents/#structuring-data-input_schema-output_schema-output_key).

You can use Gemma 4 through the [Gemini API](https://ai.google.dev/gemini-api/docs), or with one of many self-hosting options on Google Cloud: [Agent Platform](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma4), [Google Kubernetes Engine](https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm), [Cloud Run](https://docs.cloud.google.com/run/docs/run-gemma-on-cloud-run).

## Gemini API Example

Create an API key in [Google AI Studio](https://aistudio.google.com/app/apikey).

```python
# Set GEMINI_API_KEY environment variable to your API key
# export GEMINI_API_KEY="YOUR_API_KEY"

from google.adk.agents import LlmAgent
from google.adk.models import Gemini

# Simple tool to try
def get_weather(location: str) -> str:
    return f"Location: {location}. Weather: sunny, 76 degrees Fahrenheit, 8 mph wind."

root_agent = LlmAgent(
    model=Gemini(model="gemma-4-31b-it"),
    name="weather_agent",
    instruction="You are a helpful assistant that can provide current weather.",
    tools=[get_weather]
)
```

```java
// Set GEMINI_API_KEY environment variable to your API key
// export GEMINI_API_KEY="YOUR_API_KEY"

import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;

LlmAgent weatherAgent = LlmAgent.builder()
    .model("gemma-4-31b-it")
    .name("weather_agent")
    .instruction("""
        You are a helpful assistant that can provide current weather.
    """)
    .tools(FunctionTool.create(this, "getWeather")]    
    .build();

@Schema(name = "getWeather", 
        description = "Retrieve the weather forecast for a given location")
public Map<String, String> getWeather(
    @Schema(name = "location",
            description = "The location for the weather forecast")
    String location) {
    return Map.of("forecast", "Location: " + location 
        + ". Weather: sunny, 76 degrees Fahrenheit, 8 mph wind.");
}
```

## vLLM Example

To access Gemma 4 endpoints in these services, you can use vLLM models through the [LiteLLM](/agents/models/litellm/) library for Python, and through [LangChain4j](https://docs.langchain4j.dev/) for Java.

The following example shows how to use a Gemma 4 vLLM endpoint with ADK agents.

### Setup

1. **Deploy Model:** Deploy your chosen model using [Agent Platform](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma4), [Google Kubernetes Engine](https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm), or [Cloud Run](https://docs.cloud.google.com/run/docs/run-gemma-on-cloud-run), and use its OpenAI-compatible API endpoint. Note that the API base URL includes `/v1` (e.g., `https://your-vllm-endpoint.run.app/v1`).
   - *Important for ADK Tools:* When deploying, ensure the serving tool supports and enables compatible tool/function calling and reasoning parsers.
1. **Authentication:** Determine how your endpoint handles authentication (e.g., API key, bearer token).

### Code

```python
import subprocess
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- Example Agent using a model hosted on a vLLM endpoint ---

# Endpoint URL provided by your model deployment
api_base_url = "https://your-vllm-endpoint.run.app/v1"

# Model name as recognized by *your* vLLM endpoint configuration
model_name_at_endpoint = "openai/google/gemma-4-31B-it"

# Simple tool to try
def get_weather(location: str) -> str:
    return f"Location: {location}. Weather: sunny, 76 degrees Fahrenheit, 8 mph wind."

# Authentication (Example: using gcloud identity token for a Cloud Run deployment)
# Adapt this based on your endpoint's security
try:
    gcloud_token = subprocess.check_output(
        ["gcloud", "auth", "print-identity-token", "-q"]
    ).decode().strip()
    auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
except Exception as e:
    print(f"Warning: Could not get gcloud token - {e}.")
    auth_headers = None # Or handle error appropriately

root_agent = LlmAgent(
    model=LiteLlm(
        model=model_name_at_endpoint,
        api_base=api_base_url,
        # Pass authentication headers if needed
        extra_headers=auth_headers
        # Alternatively, if endpoint uses an API key:
        # api_key="YOUR_ENDPOINT_API_KEY",
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": True # Enable thinking
            },
            "skip_special_tokens": False # Should be set to False
        },
    ),
    name="weather_agent",
    instruction="You are a helpful assistant that can provide current weather.",
    tools=[get_weather] # Tools!
)
```

To use Gemma hosted on vLLM, you must use an OpenAI compatible library. LangChain4j offers an OpenAI dependency that you can add to your `pom.xml`:

```xml
<!-- LangChain4j to ADK bridge -->
<dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>google-adk-langchain4j</artifactId>
    <version>${adk.version}</version>
</dependency>
<!-- Core LangChain4j library -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-core</artifactId>
    <version>${langchain4j.version}</version>
</dependency>
<!-- OpenAI compatible model -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>${langchain4j.version}</version>
</dependency>
```

Create an OpenAI compatible chat model (streaming or non-streaming), wrap it with the `LangChain4j` wrapper, then pass it to the `LlmAgent`:

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.openai.OpenAiStreamingChatModel;

// Endpoint URL provided by your model deployment
String apiBaseUrl = "https://your-vllm-endpoint.run.app/v1";

// Model name as recognized by *your* vLLM endpoint configuration
String gemmaModelName = "gg-hf-gg/gemma-4-31b-it";

// First, define an OpenAI compatible chat model with LangChain4j
StreamingChatModel model =
    OpenAiStreamingChatModel.builder()
        .modelName(gemmaModelName)
        // If your endpoint requires an API key
        // .apiKey("YOUR_ENDPOINT_API_KEY")
        .baseUrl(apiBaseUrl)
        .customParameters(
            Map.of(
                "skip_special_tokens", false,
                "chat_template_kwargs", Map.of("enable_thinking", true)
            )
        )
        .build();

// Configure the agent with the LangChain4j wrapper model
LlmAgent weatherAgent = LlmAgent.builder()
    .model(new LangChain4j(model))
    .name("weather_agent")
    .instruction("""
        You are a helpful assistant that can provide the current weather.
    """)
    .tools(FunctionTool.create(this, "getWeather")]    
    .build();

@Schema(name = "getWeather", 
        description = "Retrieve the weather forecast for a given location")
public Map<String, String> getWeather(
    @Schema(name = "location",
            description = "The location for the weather forecast")
    String location) {
    return Map.of("forecast", "Location: " + location 
        + ". Weather: sunny, 76 degrees Fahrenheit, 8 mph wind.");
}
```

## Build a food tour agent with Gemma 4, ADK, and Google Maps MCP

This sample shows how to build a personalized food tour agent using Gemma 4, ADK, and the Google Maps MCP server. The agent takes a user’s dish photo or text description, a location, and an optional budget, then recommends places to eat and organizes them into a walking route.

### Prerequisites

- Get an API key in [Google AI Studio](https://aistudio.google.com/app/apikey). Set `GEMINI_API_KEY` environment variable to your Gemini API key.
- Enable [Google Maps API](https://console.cloud.google.com/maps-api/) on Google Cloud Console.
- Create a [Google Maps Platform API key](https://console.cloud.google.com/maps-api/credentials). Set `MAPS_API_KEY` environment variable to your API key.
- Install ADK and configure it in your Python environment or configure the Java dependencies in your Java project.

### Project structure

```bash
food_tour_app/
├── __init__.py
└── agent.py
```

**Full project can be found [here](https://github.com/google/adk-samples/tree/main/python/agents/gemma-food-tour-guide)**

`agent.py`

```python
import os
import dotenv
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

dotenv.load_dotenv()

system_instruction = """
You are an expert personalized food tour guide.
Your goal is to build a culinary tour based on the user's inputs: a photo of a dish (or a text description), a location, and a budget.

Follow these 4 rigorous steps:
1. **Identify the Cuisine/Dish:** Analyze the user's provided description or image URL to determine the primary cuisine or specific dish.
2. **Find the Best Spots:** Use the `search_places` tool to find highly rated restaurants, stalls, or cafes serving that cuisine/dish in the user's specified location.
   **CRITICAL RULE FOR PLACES:** `search_places` returns AI-generated place data summaries along with `place_id`, latitude/longitude coordinates, and map links for each place, but may lack a direct, explicit name field. You must carefully associate each described place to its provided `place_id` or `lat_lng`.
3. **Build the Route:** Use the `compute_routes` tool to structure a walking-optimized route between the selected spots.
   **CRITICAL ROUTING RULE:** To avoid hallucinating, you MUST provide the `origin` and `destination` using the exact `place_id` string OR `lat_lng` object returned by `search_places`. Do NOT guess or hallucinate an `address` or `place_id` if you do not know the exact name.
4. **Insider Tips:** Provide specific "order this, skip that" insider tips for each location on the tour.

Structure your response clearly and concisely. If the user provides a budget, ensure your suggestions align with it.
"""

MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp"

def get_maps_mcp_toolset():
    dotenv.load_dotenv()
    maps_api_key = os.getenv("MAPS_API_KEY")
    if not maps_api_key:
        print("Warning: MAPS_API_KEY environment variable not found.")
        maps_api_key = "no_api_found"

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MAPS_MCP_URL,
            headers={
                "X-Goog-Api-Key": maps_api_key
            }
        )
    )
    print("Google Maps MCP Toolset configured.")
    return tools

maps_toolset = get_maps_mcp_toolset()

root_agent = LlmAgent(
    model=Gemini(model="gemma-4-31b-it"),
    name="food_tour_agent",
    instruction=system_instruction,
    tools=[maps_toolset],
)
```

### Environment variables

Set the required environment variables before running the agent.

```text
export MAPS_API_KEY="YOUR_GOOGLE_MAPS_API_KEY"
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

### Example usage

To test out the capabilities of the Food Tour Agent, try pasting one of these prompts into the chat:

- *"I want to do a ramen tour in Toronto. My budget is $60 for the day. Give me a walking route for the top 3 spots and tell me what I should order at each."*
- *"I have this photo of a deep dish pizza [insert image URL]. I want to find the best places for this around Navy Pier in Chicago. Structure a walking tour and tell me what the must-have slice is at each stop."*
- *"I'm in Downtown Austin looking for an authentic BBQ tour. Let's keep the budget under $100. Build a walking route between 3 highly-rated spots and give me insider tips on the best cuts of meat to get."*

The agent will:

1. Infer the likely cuisine or dish style
1. Search for relevant places using Google Maps MCP tools
1. Compute a walking route between selected stops
1. Return a structured food tour with recommendations and insider tips
