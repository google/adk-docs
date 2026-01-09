# LiteLLM model connector for ADK agents

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

[LiteLLM](https://docs.litellm.ai/) is a Python library that acts as a
translation layer for models and model hosting services, providing a
standardized, OpenAI-compatible interface to over 100+ LLMs. ADK provides
integration through the LiteLLM library, allowing you to access a vast range of
LLMs from providers like OpenAI, Anthropic (non-Vertex AI), Cohere, and many
others. You can run open-source models locally or self-host them and integrate
them using LiteLLM for operational control, cost savings, privacy, or offline
use cases.

You can use the LiteLLM library to access remote or locally hosted AI models:

*   **Remote model host:** Use the `LiteLlm` wrapper class and set it
    as the `model` parameter of `LlmAgent`.
*   **Local model host:** Use the `LiteLlm` wrapper class configured to
    point to your local model server. For examples of local model hosting
    solutions, see the [Ollama](/adk-docs/agents/models/ollama/)
    or [vLLM](/adk-docs/agents/models/vllm/) documentation.

??? warning "Windows Encoding with LiteLLM"

    When using ADK agents with LiteLLM on Windows, you might encounter a
    `UnicodeDecodeError`. This error occurs because LiteLLM may attempt to read
    cached files using the default Windows encoding (`cp1252`) instead of UTF-8.
    Prevent this error by setting the `PYTHONUTF8` environment variable to
    `1`. This forces Python to use UTF-8 for all file I/O.

    **Example (PowerShell):**
    ```powershell
    # Set for the current session
    $env:PYTHONUTF8 = "1"

    # Set persistently for the user
    [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
    ```

## Setup

1. **Install LiteLLM:**
        ```shell
        pip install litellm
        ```
2. **Set Provider API Keys:** Configure API keys as environment variables for
   the specific providers you intend to use.

    * *Example for OpenAI:*

        ```shell
        export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        ```

    * *Example for Anthropic (non-Vertex AI):*

        ```shell
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

    * *Consult the
      [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers)
      for the correct environment variable names for other providers.*

## Example implementation

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
