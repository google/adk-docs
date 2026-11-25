# Google Maps grounding tool for ADK

Supported in ADKPythonTypeScriptGoJavaKotlinPreview

The Google Maps grounding tool connects your Agent Development Kit (ADK) agent to Google Maps geospatial data through Gemini models. When a user asks a location-aware question, the model invokes Google Maps internally to retrieve factual details about places, reviews, opening hours, and directions without executing local tool code.

Preview

The Google Maps grounding tool is a preview release. It may have limitations and is not recommended for production use.

Service usage requirements

When you present results grounded in Google Maps, you must display the associated Google Maps sources and attribution in your application. For the complete display, attribution, and usage requirements, see the Grounding with Google Maps documentation for the [Gemini API](https://ai.google.dev/gemini-api/docs/maps-grounding#service-usage-requirements) or [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/grounding/grounding-with-google-maps).

## Use cases

- **Local discovery and recommendations**: Recommend nearby restaurants, cafes, or services tailored to user preferences and geographic coordinates.
- **Place-specific questions**: Answer questions about business hours, menu highlights, accessibility, EV charging stations, and customer review insights.
- **Travel and itinerary planning**: Build day plans, estimate travel times, and find points of interest along a route.

## Prerequisites

- A supported Gemini model. See the supported model lists in the [Gemini API](https://ai.google.dev/gemini-api/docs/maps-grounding#supported-models) or [Agent Platform](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-google-maps#supported-models) documentation.
- Credentials configured for [Google Cloud Agent Platform](/get-started/google-cloud/), by setting `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`, `GOOGLE_CLOUD_PROJECT`, and `GOOGLE_CLOUD_LOCATION`.
- ADK installed for your target language. See the [ADK quickstart](/get-started/) for installation instructions.

## Use with agent

Add the built-in Google Maps grounding tool to your agent's tool list. The model decides when to query Google Maps based on the user's prompt.

```python
from google.adk.agents import Agent
from google.adk.tools import google_maps_grounding

root_agent = Agent(
    name="maps_grounding_agent",
    model="gemini-flash-latest",
    description="Answers location and place questions using Google Maps.",
    instruction=(
        "You are a local guide. Use Google Maps to answer questions about "
        "places, business hours, reviews, and nearby recommendations."
    ),
    tools=[google_maps_grounding],
)
```

```typescript
import { GOOGLE_MAPS_GROUNDING, LlmAgent } from "@google/adk";

const rootAgent = new LlmAgent({
  name: "maps_grounding_agent",
  model: "gemini-flash-latest",
  description: "Answers location and place questions using Google Maps.",
  instruction:
    "You are a local guide. Use Google Maps to answer questions about " +
    "places, business hours, reviews, and nearby recommendations.",
  tools: [GOOGLE_MAPS_GROUNDING],
});

export { rootAgent };
```

```go
package main

import (
    "context"
    "log"

    "google.golang.org/adk/v2/agent"
    "google.golang.org/adk/v2/agent/llmagent"
    "google.golang.org/adk/v2/model/gemini"
    "google.golang.org/adk/v2/tool"
    "google.golang.org/adk/v2/tool/geminitool"
    "google.golang.org/genai"
)

func newMapsAgent(ctx context.Context) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{})
    if err != nil {
        return nil, err
    }

    return llmagent.New(llmagent.Config{
        Name:        "maps_grounding_agent",
        Model:       model,
        Description: "Answers location and place questions using Google Maps.",
        Instruction: "You are a local guide. Use Google Maps to answer questions about places, business hours, reviews, and nearby recommendations.",
        Tools:       []tool.Tool{geminitool.GoogleMaps{}},
    })
}

func main() {
    if _, err := newMapsAgent(context.Background()); err != nil {
        log.Fatal(err)
    }
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.GoogleMapsTool;

LlmAgent rootAgent =
    LlmAgent.builder()
        .name("maps_grounding_agent")
        .model("gemini-flash-latest")
        .description("Answers location and place questions using Google Maps.")
        .instruction(
            "You are a local guide. Use Google Maps to answer questions about "
                + "places, business hours, reviews, and nearby recommendations.")
        .tools(GoogleMapsTool.INSTANCE)
        .build();
```

```kotlin
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.tools.GoogleMapsTool

val rootAgent =
    LlmAgent(
        name = "maps_grounding_agent",
        model = Gemini(name = "gemini-flash-latest"),
        description = "Answers location and place questions using Google Maps.",
        instruction =
            Instruction(
                "You are a local guide. Use Google Maps to answer questions about " +
                    "places, business hours, reviews, and nearby recommendations.",
            ),
        tools = listOf(GoogleMapsTool()),
    )
```

## Provide location context

When a user asks a proximity query such as "coffee shops near me", pass geographic coordinates in the agent's content generation configuration so the model can tailor local results to that area. ADK Python, ADK TypeScript, ADK Go, and ADK Java support setting latitude and longitude coordinates in the retrieval configuration. In ADK Kotlin, specify the city, neighborhood, or address directly in the prompt or agent instruction.

```python
from google.adk.agents import Agent
from google.adk.tools import google_maps_grounding
from google.genai import types

root_agent = Agent(
    name="maps_grounding_agent",
    model="gemini-flash-latest",
    description="Answers location-aware questions using Google Maps.",
    instruction=(
        "Recommend nearby places based on the user's location and preferences."
    ),
    tools=[google_maps_grounding],
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(
            retrieval_config=types.RetrievalConfig(
                lat_lng=types.LatLng(
                    latitude=37.7749,
                    longitude=-122.4194,
                ),
                language_code="en_US",
            )
        )
    ),
)
```

```typescript
import { GOOGLE_MAPS_GROUNDING, LlmAgent } from "@google/adk";

const rootAgent = new LlmAgent({
  name: "maps_grounding_agent",
  model: "gemini-flash-latest",
  description: "Answers location-aware questions using Google Maps.",
  instruction:
    "Recommend nearby places based on the user's location and preferences.",
  tools: [GOOGLE_MAPS_GROUNDING],
  generateContentConfig: {
    toolConfig: {
      retrievalConfig: {
        latLng: {
          latitude: 37.7749,
          longitude: -122.4194,
        },
        languageCode: "en_US",
      },
    },
  },
});

export { rootAgent };
```

```go
package main

import (
    "context"
    "log"

    "google.golang.org/adk/v2/agent"
    "google.golang.org/adk/v2/agent/llmagent"
    "google.golang.org/adk/v2/model/gemini"
    "google.golang.org/adk/v2/tool"
    "google.golang.org/adk/v2/tool/geminitool"
    "google.golang.org/genai"
)

func newLocalizedMapsAgent(ctx context.Context) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{})
    if err != nil {
        return nil, err
    }

    return llmagent.New(llmagent.Config{
        Name:        "maps_grounding_agent",
        Model:       model,
        Description: "Answers location-aware questions using Google Maps.",
        Instruction: "Recommend nearby places based on the user's location and preferences.",
        Tools:       []tool.Tool{geminitool.GoogleMaps{}},
        GenerateContentConfig: &genai.GenerateContentConfig{
            ToolConfig: &genai.ToolConfig{
                RetrievalConfig: &genai.RetrievalConfig{
                    LatLng: &genai.LatLng{
                        Latitude:  genai.Ptr(37.7749),
                        Longitude: genai.Ptr(-122.4194),
                    },
                    LanguageCode: "en_US",
                },
            },
        },
    })
}

func main() {
    if _, err := newLocalizedMapsAgent(context.Background()); err != nil {
        log.Fatal(err)
    }
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.GoogleMapsTool;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.LatLng;
import com.google.genai.types.RetrievalConfig;
import com.google.genai.types.ToolConfig;

LlmAgent rootAgent =
    LlmAgent.builder()
        .name("maps_grounding_agent")
        .model("gemini-flash-latest")
        .description("Answers location-aware questions using Google Maps.")
        .instruction(
            "Recommend nearby places based on the user's location and preferences.")
        .tools(GoogleMapsTool.INSTANCE)
        .generateContentConfig(
            GenerateContentConfig.builder()
                .toolConfig(
                    ToolConfig.builder()
                        .retrievalConfig(
                            RetrievalConfig.builder()
                                .latLng(
                                    LatLng.builder()
                                        .latitude(37.7749)
                                        .longitude(-122.4194)
                                        .build())
                                .languageCode("en_US")
                                .build())
                        .build())
                .build())
        .build();
```

## Inspect grounding metadata

When the model grounds a response with Google Maps, the response event includes grounding metadata with a list of grounding chunks. Each Maps chunk provides the place title, a Google Maps URI, and a place ID so your application can render required citations and links:

```json
{
  "groundingChunks": [
    {
      "maps": {
        "uri": "https://maps.google.com/?cid=...",
        "title": "Example Cafe",
        "placeId": "places/..."
      }
    }
  ]
}
```

Use the `title` and `uri` values from each Maps grounding chunk to display Google Maps source links in accordance with the display and attribution requirements for the [Gemini API](https://ai.google.dev/gemini-api/docs/maps-grounding#service-usage-requirements) or [Agent Platform](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-google-maps#service-usage-requirements).

## Available tools

| Tool name     | SDK symbol                                                                                                                                                                                                                          | Description                                                              |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `google_maps` | Python: `google_maps_grounding` (`GoogleMapsGroundingTool`) TypeScript: `GOOGLE_MAPS_GROUNDING` (`GoogleMapsGroundingTool`) Go: `geminitool.GoogleMaps` Java: `GoogleMapsTool.INSTANCE` (`GoogleMapsTool`) Kotlin: `GoogleMapsTool` | Enables server-side Grounding with Google Maps on Gemini model requests. |

## Limitations

- **Gemini models only**: This tool works only with supported Gemini models. The tool does not support non-Gemini models or Gemini 1.x models.
- **No local function execution**: Because Google Maps grounding executes inside the Gemini backend, the tool does not expose a client-side function declaration, and you cannot call it directly as a local function.
- **Combining with other tools**: Depending on the Gemini model version, you might not be able to combine built-in grounding tools with other tools in the same agent. For workarounds such as wrapping the agent in an `AgentTool`, see [Limitations for ADK tools](/tools/limitations/#one-tool-one-agent).
- **Built-in grounding vs. Model Context Protocol (MCP)**: Use this built-in tool for in-model Gemini grounding over Google Maps places, reviews, and directions. If you need client-side tool calls or want to connect non-Gemini models to Google Maps Grounding Lite, see [MCP tools](/tools-custom/mcp-tools/).

## Additional resources

- [Grounding with Google Maps (Gemini API)](https://ai.google.dev/gemini-api/docs/maps-grounding)
- [Grounding with Google Maps (Agent Platform)](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-google-maps)
- [Google Maps and Google Earth legal notices](https://www.google.com/help/legalnotices_maps/)
- [Google Search tool for ADK](/integrations/google-search/)
- [Limitations for ADK tools](/tools/limitations/)
