# Agent Platform hosted models for ADK agents

For enterprise-grade scalability, reliability, and integration with Google Cloud's MLOps ecosystem, you can use models deployed to Agent Platform Endpoints. This includes models from Model Garden or your own fine-tuned models.

**Integration Method:** Pass the full Agent Platform Endpoint resource string (`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`) directly to the `model` parameter of `LlmAgent`.

## Agent Platform Setup

For more details on connecting ADK agents to Google Cloud hosted models and services, including Gemini Enterprise Agent Platform, see the [Connect to Google Cloud and Agent Platform](/get-started/google-cloud/) guide.

## Model Garden Deployments

Supported in ADKPython v0.2.0Java v0.1.0

You can deploy various open and proprietary models from the [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) to an endpoint.

**Example:**

```python
from google.adk.agents import LlmAgent
from google.genai import types # For config objects

# --- Example Agent using a Llama 3 model deployed from Model Garden ---

# Replace with your actual Agent Platform Endpoint resource name
llama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

agent_llama3_vertex = LlmAgent(
    model=llama3_endpoint,
    name="llama3_vertex_agent",
    instruction="You are a helpful assistant based on Llama 3, hosted on Agent Platform.",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
    # ... other agent parameters
)
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Gemini;
import com.google.genai.types.GenerateContentConfig;

// ...

// Replace with your actual Agent Platform Endpoint resource name
String llama3Endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID";

LlmAgent agentLlama3Vertex = LlmAgent.builder()
    .model(Gemini.builder()
        .modelName(llama3Endpoint)
        .build())
    .name("llama3_vertex_agent")
    .instruction("You are a helpful assistant based on Llama 3, hosted on Agent Platform.")
    .generateContentConfig(GenerateContentConfig.builder()
        .maxOutputTokens(2048)
        .build())
    // ... other agent parameters
    .build();
```

## Fine-tuned Model Endpoints

Supported in ADKPython v0.2.0Java v0.1.0

Deploying your fine-tuned models (whether based on Gemini or other architectures supported by Agent Platform) results in an endpoint that can be used directly.

**Example:**

```python
from google.adk.agents import LlmAgent

# --- Example Agent using a fine-tuned Gemini model endpoint ---

# Replace with your fine-tuned model's endpoint resource name
finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

agent_finetuned_gemini = LlmAgent(
    model=finetuned_gemini_endpoint,
    name="finetuned_gemini_agent",
    instruction="You are a specialized assistant trained on specific data.",
    # ... other agent parameters
)
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Gemini;

// ...

// Replace with your fine-tuned model's endpoint resource name
String finetunedGeminiEndpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID";

LlmAgent agentFinetunedGemini = LlmAgent.builder()
    .model(Gemini.builder()
        .modelName(finetunedGeminiEndpoint)
        .build())
    .name("finetuned_gemini_agent")
    .instruction("You are a specialized assistant trained on specific data.")
    // ... other agent parameters
    .build();
```

## Anthropic Claude on Agent Platform

Supported in ADKPython v0.2.0TypeScript v2.4.0Go v2.7.0Java v0.1.0Kotlin v1.4.0

Some providers, like Anthropic, make their models available directly through Agent Platform. To set up and use Claude models on Agent Platform, including extended thinking and prompt caching, see [Connect through Agent Platform](/agents/models/anthropic/#connect-through-agent-platform) in the Claude models guide.

## Open Models on Agent Platform

Supported in ADKPython v0.1.0Java v0.1.0

Agent Platform offers a curated selection of open-source models, such as Meta Llama, through Model-as-a-Service (MaaS). These models are accessible via managed APIs, allowing you to deploy and scale without managing the underlying infrastructure. For a full list of available options, see the [Agent Platform open models for MaaS](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/maas/use-open-models#open-models) documentation.

You can use the [LiteLLM](https://docs.litellm.ai/) library to access open models like Meta's Llama on Agent Platform MaaS

**Integration Method:** Use the `LiteLlm` wrapper class and set it as the `model` parameter of `LlmAgent`. Make sure you go through the [LiteLLM model connector for ADK agents](/agents/models/litellm/#litellm-model-connector-for-adk-agents) documentation on how to use LiteLLM in ADK

**Setup:**

1. **Agent Platform Environment:** Ensure the consolidated Agent Platform setup (ADC, Env Vars, `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`) is complete.

1. **Install LiteLLM:** ADK requires `litellm>=1.84`.

   ```shell
   pip install "litellm>=1.84"
   ```

**Example:**

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- Example Agent using Meta's Llama 4 Scout ---
agent_llama_vertexai = LlmAgent(
    model=LiteLlm(model="vertex_ai/meta/llama-4-scout-17b-16e-instruct-maas"), # LiteLLM model string format
    name="llama4_agent",
    instruction="You are a helpful assistant powered by Llama 4 Scout.",
    # ... other agent parameters
)
```
