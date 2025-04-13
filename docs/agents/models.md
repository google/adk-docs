# Using Different Models with ADK

The Agent Development Kit (ADK) is designed for flexibility, allowing you to integrate various Large Language Models (LLMs) into your agents. While the setup for Google Gemini models is covered in the [Setup Foundation Models](../get-started/installation.md) guide, this page details how to leverage Gemini effectively and integrate other popular models, including those hosted externally or running locally.

ADK primarily uses two mechanisms for model integration:

1. **Direct String / Registry:** For models tightly integrated with Google Cloud (like Gemini models accessed via Google AI Studio or Vertex AI) or models hosted on Vertex AI endpoints. You typically provide the model name or endpoint resource string directly to the `LlmAgent`. ADK's internal registry resolves this string to the appropriate backend client, often utilizing the `google-genai` library.
2. **Wrapper Classes:** For broader compatibility, especially with models outside the Google ecosystem or those requiring specific client configurations (like models accessed via LiteLLM). You instantiate a specific wrapper class (e.g., `LiteLlm`) and pass this object as the `model` parameter to your `LlmAgent`.

The following sections guide you through using these methods based on your needs.

## Using Google Gemini Models

This is the most direct way to use Google's flagship models within ADK.

**Integration Method:** Pass the model's identifier string directly to the `model` parameter of `LlmAgent` (or its alias, `Agent`).

**Backend Options & Setup:**

The `google-genai` library, used internally by ADK for Gemini, can connect through either Google AI Studio or Vertex AI.

!!!note "Model support for voice/video streaming"

    In order to use voice/video streaming in ADK, you will need to use Gemini models that support the Live API. You can find the **model ID(s)** that supports the Gemini Live API in the documentation:

    - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
    - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### Google AI Studio

* **Use Case:** Google AI Studio is the easiest way to started with Gemini. All you need is the [API key](https://aistudio.google.com/app/apikey). Best for rapid prototyping and development.
* **Setup:** Typically requires an API key set as an environment variable:

```shell
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

* **Models:** Find all available models on the [Google AI for Developers site](https://ai.google.dev/gemini-api/docs/models).

### Vertex AI

* **Use Case:** Recommended for production applications, leveraging Google Cloud infrastructure. Gemini on Vertex AI supports enterprise-grade features, security, and compliance controls.
* **Setup:**
    * Authenticate using Application Default Credentials (ADC):

        ```shell
        gcloud auth application-default login
        ```

    * Set your Google Cloud project and location:

        ```shell
        export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
        export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
        ```

    * Explicitly tell the library to use Vertex AI:

        ```shell
        export GOOGLE_GENAI_USE_VERTEXAI=TRUE
        ```

* **Models:** Find available model IDs in the [Vertex AI documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models).

**Example:**

```python
from google.adk.agents import LlmAgent

# --- Example using a stable Gemini Flash model ---
agent_gemini_flash = LlmAgent(
    # Use the latest stable Flash model identifier
    model="gemini-2.0-flash",
    name="gemini_flash_agent",
    instruction="You are a fast and helpful Gemini assistant.",
    # ... other agent parameters
)

# --- Example using a powerful Gemini Pro model ---
# Note: Always check the official Gemini documentation for the latest model names,
# including specific preview versions if needed. Preview models might have
# different availability or quota limitations.
agent_gemini_pro = LlmAgent(
    # Use the latest generally available Pro model identifier
    model="gemini-2.5-pro-preview-03-25",
    name="gemini_pro_agent",
    instruction="You are a powerful and knowledgeable Gemini assistant.",
    # ... other agent parameters
)
```

## Using Cloud & Proprietary Models via LiteLLM

To access a vast range of LLMs from providers like OpenAI, Anthropic (non-Vertex AI), Cohere, and many others, ADK offers integration through the LiteLLM library.

**Integration Method:** Instantiate the `LiteLlm` wrapper class and pass it to the `model` parameter of `LlmAgent`.

**LiteLLM Overview:** [LiteLLM](https://docs.litellm.ai/) acts as a translation layer, providing a standardized, OpenAI-compatible interface to over 100+ LLMs.

**Setup:**

1. **Install LiteLLM:**
        ```shell
        pip install litellm
        ```
2. **Set Provider API Keys:** Configure API keys as environment variables for the specific providers you intend to use.

    * *Example for OpenAI:*

        ```shell
        export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        ```

    * *Example for Anthropic (non-Vertex AI):*

        ```shell
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

    * *Consult the [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers) for the correct environment variable names for other providers.*

        **Example:**

        ```python
        from google.adk.agents import LlmAgent
        from google.adk.models.lite_llm import LiteLlm

        # --- Example Agent using OpenAI's GPT-4o ---
        # (Requires OPENAI_API_KEY)
        agent_openai = LlmAgent(
            model=LiteLlm(model="openai/gpt-4o"), # LiteLLM model string format
            name="openai_agent",
            instruction="You are a helpful assistant powered by GPT-4o.",
            # ... other agent parameters
        )

        # --- Example Agent using Anthropic's Claude Haiku (non-Vertex) ---
        # (Requires ANTHROPIC_API_KEY)
        agent_claude_direct = LlmAgent(
            model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
            name="claude_direct_agent",
            instruction="You are an assistant powered by Claude Haiku.",
            # ... other agent parameters
        )
        ```

## Using Open & Local Models via LiteLLM

For maximum control, cost savings, privacy, or offline use cases, you can run open-source models locally or self-host them and integrate them using LiteLLM.

**Integration Method:** Instantiate the `LiteLlm` wrapper class, configured to point to your local model server.

### Ollama Integration

[Ollama](https://ollama.com/) allows you to easily run open-source models locally.

**Prerequisites:**

1. Install Ollama.
2. Pull the desired model (e.g., Google's Gemma):

    ```shell
    ollama pull gemma:2b
    ```

3. Ensure the Ollama server is running (usually happens automatically after installation or by running `ollama serve`).

    **Example:**

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- Example Agent using Gemma 2B running via Ollama ---
    agent_ollama_gemma = LlmAgent(
        # LiteLLM knows how to connect to a local Ollama server by default
        model=LiteLlm(model="ollama/gemma:2b"), # Standard LiteLLM format for Ollama
        name="ollama_gemma_agent",
        instruction="You are Gemma, running locally via Ollama.",
        # ... other agent parameters
    )
    ```

### Self-Hosted Endpoint (e.g., vLLM)

Tools like [vLLM](https://github.com/vllm-project/vllm) allow you to host models efficiently and often expose an OpenAI-compatible API endpoint.

**Setup:**

1. **Deploy Model:** Deploy your chosen model using vLLM (or a similar tool). Note the API base URL (e.g., `https://your-vllm-endpoint.run.app/v1`).
    * *Important for ADK Tools:* When deploying, ensure the serving tool supports and enables OpenAI-compatible tool/function calling. For vLLM, this might involve flags like `--enable-auto-tool-choice` and potentially a specific `--tool-call-parser`, depending on the model. Refer to the vLLM documentation on Tool Use.
2. **Authentication:** Determine how your endpoint handles authentication (e.g., API key, bearer token).

    **Integration Example:**

    ```python
    import subprocess
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- Example Agent using a model hosted on a vLLM endpoint ---

    # Endpoint URL provided by your vLLM deployment
    api_base_url = "https://your-vllm-endpoint.run.app/v1"

    # Model name as recognized by *your* vLLM endpoint configuration
    model_name_at_endpoint = "hosted_vllm/google/gemma-3-4b-it" # Example from vllm_test.py

    # Authentication (Example: using gcloud identity token for a Cloud Run deployment)
    # Adapt this based on your endpoint's security
    try:
        gcloud_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token", "-q"]
        ).decode().strip()
        auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
    except Exception as e:
        print(f"Warning: Could not get gcloud token - {e}. Endpoint might be unsecured or require different auth.")
        auth_headers = None # Or handle error appropriately

    agent_vllm = LlmAgent(
        model=LiteLlm(
            model=model_name_at_endpoint,
            api_base=api_base_url,
            # Pass authentication headers if needed
            extra_headers=auth_headers
            # Alternatively, if endpoint uses an API key:
            # api_key="YOUR_ENDPOINT_API_KEY"
        ),
        name="vllm_agent",
        instruction="You are a helpful assistant running on a self-hosted vLLM endpoint.",
        # ... other agent parameters
    )
    ```

## Using Hosted & Tuned Models on Vertex AI

For enterprise-grade scalability, reliability, and integration with Google Cloud's MLOps ecosystem, you can use models deployed to Vertex AI Endpoints. This includes models from Model Garden or your own fine-tuned models.

**Integration Method:** Pass the full Vertex AI Endpoint resource string (`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`) directly to the `model` parameter of `LlmAgent`.

**Vertex AI Setup (Consolidated):**

Ensure your environment is configured for Vertex AI:

1. **Authentication:** Use Application Default Credentials (ADC):

    ```shell
    gcloud auth application-default login
    ```

2. **Environment Variables:** Set your project and location:

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_ENDPOINT_LOCATION" # e.g., us-central1
    ```

3. **Enable Vertex Backend:** Crucially, ensure the `google-genai` library targets Vertex AI:

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### Model Garden Deployments

You can deploy various open and proprietary models from the [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) to an endpoint.

**Example:**

```python
from google.adk.agents import LlmAgent
from google.genai import types # For config objects

# --- Example Agent using a Llama 3 model deployed from Model Garden ---

# Replace with your actual Vertex AI Endpoint resource name
llama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

agent_llama3_vertex = LlmAgent(
    model=llama3_endpoint,
    name="llama3_vertex_agent",
    instruction="You are a helpful assistant based on Llama 3, hosted on Vertex AI.",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
    # ... other agent parameters
)
```

### Fine-tuned Model Endpoints

Deploying your fine-tuned models (whether based on Gemini or other architectures supported by Vertex AI) results in an endpoint that can be used directly.

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

### Third-Party Models on Vertex AI (e.g., Anthropic Claude)

Some providers, like Anthropic, make their models available directly through Vertex AI.

**Integration Method:** Uses the direct model string (e.g., `"claude-3-sonnet@20240229"`), *but requires manual registration* within ADK.

**Why Registration?** ADK's registry automatically recognizes `gemini-*` strings and standard Vertex AI endpoint strings (`projects/.../endpoints/...`) and routes them via the `google-genai` library. For other model types used directly via Vertex AI (like Claude), you must explicitly tell the ADK registry which specific wrapper class (`Claude` in this case) knows how to handle that model identifier string with the Vertex AI backend.

**Setup:**

1. **Vertex AI Environment:** Ensure the consolidated Vertex AI setup (ADC, Env Vars, `GOOGLE_GENAI_USE_VERTEXAI=TRUE`) is complete.
2. **Install Provider Library:** Install the necessary client library configured for Vertex AI.

    ```shell
    pip install "anthropic[vertex]"
    ```

3. **Register Model Class:** Add this code near the start of your application, *before* creating an agent using the Claude model string:

    ```python
    # Required for using Claude model strings directly via Vertex AI with LlmAgent
    from google.adk.models.anthropic_llm import Claude
    from google.adk.models.registry import LLMRegistry

    LLMRegistry.register(Claude)
    ```

    **Example:**

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models.anthropic_llm import Claude # Import needed for registration
    from google.adk.models.registry import LLMRegistry # Import needed for registration
    from google.genai import types

    # --- Register Claude class (do this once at startup) ---
    LLMRegistry.register(Claude)

    # --- Example Agent using Claude 3 Sonnet on Vertex AI ---

    # Standard model name for Claude 3 Sonnet on Vertex AI
    claude_model_vertexai = "claude-3-sonnet@20240229"

    agent_claude_vertexai = LlmAgent(
        model=claude_model_vertexai, # Pass the direct string after registration
        name="claude_vertexai_agent",
        instruction="You are an assistant powered by Claude 3 Sonnet on Vertex AI.",
        generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
        # ... other agent parameters
    )
    ```
