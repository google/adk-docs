# LiteLLM model connector for ADK agents

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

For maximum control, cost savings, privacy, or offline use cases, you can run
open-source models locally or self-host them and integrate them using LiteLLM.

**Integration Method:** Instantiate the `LiteLlm` wrapper class, configured to
point to your local model server.

To access a vast range of LLMs from providers like OpenAI, Anthropic (non-Vertex
AI), Cohere, and many others, ADK offers integration through the LiteLLM
library.

**Integration Method:** Instantiate the `LiteLlm` wrapper class and pass it to
the `model` parameter of `LlmAgent`.

**LiteLLM Overview:** [LiteLLM](https://docs.litellm.ai/) acts as a translation
layer, providing a standardized, OpenAI-compatible interface to over 100+ LLMs.

**Setup:**

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

!!! warning "Windows Encoding Note for LiteLLM"

    When using ADK agents with LiteLLM on Windows, you might encounter a `UnicodeDecodeError`. This error occurs because LiteLLM may attempt to read cached files using the default Windows encoding (`cp1252`) instead of UTF-8.

    To prevent this, we recommend setting the `PYTHONUTF8` environment variable to `1`. This forces Python to use UTF-8 for all file I/O.

    **Example (PowerShell):**
    ```powershell
    # Set for the current session
    $env:PYTHONUTF8 = "1"

    # Set persistently for the user
    [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
    ```

### Using openai provider

Alternatively, `openai` can be used as the provider name. But this will also
require setting the `OPENAI_API_BASE=http://localhost:11434/v1` and
`OPENAI_API_KEY=anything` env variables instead of `OLLAMA_API_BASE`. **Please
note that api base now has `/v1` at the end.**

```py
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "hello world agent that can roll a dice of 8 sides and check prime"
        " numbers."
    ),
    instruction="""
      You roll dice and answer questions about the outcome of the dice rolls.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

```bash
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=anything
adk web
```

### Debugging

You can see the request sent to the Ollama server by adding the following in
your agent code just after imports.

```py
import litellm
litellm._turn_on_debug()
```

Look for a line like the following:

```bash
Request Sent from LiteLLM:
curl -X POST \
http://localhost:11434/api/chat \
-d '{'model': 'mistral-small3.1', 'messages': [{'role': 'system', 'content': ...
```

