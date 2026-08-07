# Supported models

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">Experimental</span>
</div>

Live agents require a Live API model — a standard Gemini model will not hold a
bidirectional connection. This page lists the models ADK supports for live agents, how to
configure model names so your application survives model deprecations, and where to check
current availability.

## Native audio models

Live agents run on **native audio** models: the model processes audio input and generates
audio output directly, end to end, without an intermediate text conversion step. This is
what produces human-like speech with natural prosody, and it is the architecture ADK
supports for live agents.

| Platform | Model | Notes |
|----------|-------|-------|
| Gemini Live API | [gemini-2.5-flash-native-audio-preview-12-2025](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash-live) | Publicly available |
| Gemini Live API (Agent Platform) | [gemini-live-2.5-flash-native-audio](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api) | Public preview |

**Key characteristics:**

- **End-to-end audio processing**: Processes audio input and generates audio output directly without converting to text intermediately
- **Natural prosody**: Produces more human-like speech patterns, intonation, and emotional expressiveness
- **Extended voice library**: Supports the eight prebuilt Live API voices plus additional voices from the Text-to-Speech (TTS) service — see [Voice configuration](voice.md#supported-voices)
- **Automatic language detection**: Determines language from conversation context without explicit configuration
- **Advanced conversational features**:
  - **[Affective dialog](voice.md#proactivity-and-affective-dialog)**: Adapts response style to input expression and tone, detecting emotional cues
  - **[Proactive audio](voice.md#proactivity-and-affective-dialog)**: Can proactively decide when to respond, offer suggestions, or ignore irrelevant input
  - **Dynamic thinking**: Supports thought summaries and dynamic thinking budgets
- **AUDIO-only response modality**: Does not support the TEXT response modality with `RunConfig`. To get text alongside audio, use [audio transcription](voice.md#audio-transcription)

## How to handle model names

When building ADK applications, you'll need to specify which model to use. The recommended approach is to use environment variables for model configuration, which provides flexibility as model availability and naming change over time.

**Recommended Pattern:**

```python
import os
from google.adk.agents import Agent

# Use environment variable with fallback to a sensible default
agent = Agent(
    name="my_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[...],
    instruction="..."
)
```

**Why use environment variables:**

- **Model availability changes**: Models are released, updated, and deprecated regularly (e.g., `gemini-2.0-flash-live-001` was deprecated on December 09, 2025)
- **Platform-specific names**: Gemini Live API and Gemini Live API on Agent Platform use different model naming conventions for the same functionality
- **Easy switching**: Change models without modifying code by updating the `.env` file
- **Environment-specific configuration**: Use different models for development, staging, and production

**Configuration in `.env` file:**

```bash
# For Gemini Live API (publicly available)
DEMO_AGENT_MODEL=gemini-2.5-flash-native-audio-preview-12-2025

# For Gemini Live API (if using Agent Platform)
# DEMO_AGENT_MODEL=gemini-live-2.5-flash-native-audio
```

!!! note "Environment Variable Loading Order"

    When using `.env` files with `python-dotenv`, you must call `load_dotenv()` **before** importing any modules that read environment variables. Otherwise, `os.getenv()` will return `None` and fall back to the default value, ignoring your `.env` configuration.

    **Correct order in `main.py`:**

    ```python
    from dotenv import load_dotenv
    from pathlib import Path

    # Load .env file BEFORE importing agent
    load_dotenv(Path(__file__).parent / ".env")

    # Now safe to import modules that use environment variables
    from google_search_agent.agent import agent
    ```

    **Incorrect order (will not work):**

    ```python
    from dotenv import load_dotenv
    from google_search_agent.agent import agent  # Agent reads env var here

    # Too late! Agent already initialized with default model
    load_dotenv(Path(__file__).parent / ".env")
    ```

    This is a Python import behavior: when you import a module, its top-level code executes immediately. If your agent module calls `os.getenv("DEMO_AGENT_MODEL")` at import time, the `.env` file must already be loaded.

**Selecting the right model:**

1. **Choose platform**: Decide between Gemini Live API (public) or Gemini Live API on Agent Platform (enterprise)
2. **Check current availability**: Refer to the model table above and the official documentation
3. **Configure environment variable**: Set `DEMO_AGENT_MODEL` in your `.env` file (see [`agent.py:17-32`](https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/google_search_agent/agent.py#L17-L32) and [`main.py:36-41`](https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/main.py#L36-L41))

## Model compatibility and availability

For the latest information on Live API model compatibility and availability:

- **Gemini Live API models**: See the [Gemini models documentation](https://ai.google.dev/gemini-api/docs/models/gemini)
- **Gemini Live API models (Agent Platform)**: See the [Agent Platform model documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

Always verify model availability and feature support in the official documentation before deploying to production.

