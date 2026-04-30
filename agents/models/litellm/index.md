# LiteLLM model connector for ADK agents

Supported in ADKPython v0.1.0

ADK Python Security Advisory: LiteLLM supply chain compromise

Unauthorized code was identified in LiteLLM versions 1.82.7 and 1.82.8 on PyPI on March 24, 2026. If you use ADK Python with the `eval` or `extensions` extras, update to the latest version of ADK Python immediately. If you installed or upgraded LiteLLM during this period, rotate all secrets and credentials. For details and required actions, refer to the [ADK security advisory](https://github.com/google/adk-python/issues/5005) and [LiteLLM's Security Update: Suspected Supply Chain Incident](https://docs.litellm.ai/blog/security-update-march-2026).

[LiteLLM](https://docs.litellm.ai/) is a Python library that acts as a translation layer for models and model hosting services, providing a standardized, OpenAI-compatible interface to over 100+ LLMs. ADK provides integration through the LiteLLM library, allowing you to access a vast range of LLMs from providers like OpenAI, Anthropic (non-Agent Platform), Cohere, and many others. You can run open-source models locally or self-host them and integrate them using LiteLLM for operational control, cost savings, privacy, or offline use cases.

You can use the LiteLLM library to access remote or locally hosted AI models:

- **Remote model host:** Use the `LiteLlm` wrapper class and set it as the `model` parameter of `LlmAgent`.
- **Local model host:** Use the `LiteLlm` wrapper class configured to point to your local model server. For examples of local model hosting solutions, see the [Ollama](/agents/models/ollama/) or [vLLM](/agents/models/vllm/) documentation.

Windows Encoding with LiteLLM

When using ADK agents with LiteLLM on Windows, you might encounter a `UnicodeDecodeError`. This error occurs because LiteLLM may attempt to read cached files using the default Windows encoding (`cp1252`) instead of UTF-8. Prevent this error by setting the `PYTHONUTF8` environment variable to `1`. This forces Python to use UTF-8 for all file I/O.

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

1. **Set Provider API Keys:** Configure API keys as environment variables for the specific providers you intend to use.

   - *Example for OpenAI:*

     ```shell
     export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
     ```

   - *Example for Anthropic (non-Agent Platform):*

     ```shell
     export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
     ```

   - *Consult the [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers) for the correct environment variable names for other providers.*

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
