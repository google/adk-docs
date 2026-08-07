# Supported models

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">Experimental</span>
</div>

Live agents require a Live API model — a standard Gemini model will not hold a
bidirectional connection. This page lists the models ADK supports for live agents, how to
configure model names so your application survives model deprecations, and where to check
current availability.

## Understanding Audio Model Architectures

When building voice applications with the Live API, one of the most important decisions is selecting the right audio model architecture. The Live API supports two fundamentally different type of models for audio processing: **Native Audio** and **Half-Cascade**. These model architectures differ in how they process audio input and generate audio output, which directly impacts response naturalness, tool execution reliability, latency characteristics, and overall use case suitability.

Understanding these architectures helps you make informed model selection decisions based on your application's requirements—whether you prioritize natural conversational AI, production reliability, or specific feature availability.

### Native Audio Models

A fully integrated end-to-end audio model architecture where the model processes audio input and generates audio output directly, without intermediate text conversion. This approach enables more human-like speech with natural prosody.

| Audio Model Architecture | Platform | Model | Notes |
|-------------------|----------|-------|-------|
| Native Audio | Gemini Live API | [gemini-2.5-flash-native-audio-preview-12-2025](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash-live) |Publicly available|
| Native Audio | Gemini Live API | [gemini-live-2.5-flash-native-audio](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api) | Public preview |

**Key Characteristics:**

- **End-to-end audio processing**: Processes audio input and generates audio output directly without converting to text intermediately
- **Natural prosody**: Produces more human-like speech patterns, intonation, and emotional expressiveness
- **Extended voice library**: Supports all half-cascade voices plus additional voices from Text-to-Speech (TTS) service
- **Automatic language detection**: Determines language from conversation context without explicit configuration
- **Advanced conversational features**:
  - **[Affective dialog](#proactivity-and-affective-dialog)**: Adapts response style to input expression and tone, detecting emotional cues
  - **[Proactive audio](#proactivity-and-affective-dialog)**: Can proactively decide when to respond, offer suggestions, or ignore irrelevant input
  - **Dynamic thinking**: Supports thought summaries and dynamic thinking budgets
- **AUDIO-only response modality**: Does not support TEXT response modality with `RunConfig`, resulting in slower initial response times

### Half-Cascade Models

A hybrid architecture that combines native audio input processing with text-to-speech (TTS) output generation. Also referred to as "Cascaded" models in some documentation.

Audio input is processed natively, but responses are first generated as text then converted to speech. This separation provides better reliability and more robust tool execution in production environments.

| Audio Model Architecture | Platform | Model | Notes |
|-------------------|----------|-------|-------|
| Half-Cascade | Gemini Live API | [gemini-2.0-flash-live-001](https://ai.google.dev/gemini-api/docs/models#gemini-2.0-flash-live) | Deprecated on December 09, 2025 |
| Half-Cascade | Gemini Live API | [gemini-live-2.5-flash](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash#2.5-flash) | Private GA, not publicly available |

**Key Characteristics:**

- **Hybrid architecture**: Combines native audio input processing with TTS-based audio output generation
- **TEXT response modality support**: Supports TEXT response modality  with `RunConfig` in addition to AUDIO, enabling much faster responses for text-only use cases
- **Explicit language control**: Supports manual language code configuration via `speech_config.language_code`
- **Established TTS quality**: Leverages proven text-to-speech technology for consistent audio output
- **Supported voices**: Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr (8 prebuilt voices)

### How to Handle Model Names

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
2. **Choose architecture**:
   - Native Audio for natural conversational AI with advanced features
   - Half-Cascade for production reliability with tool execution
3. **Check current availability**: Refer to the model tables above and official documentation
4. **Configure environment variable**: Set `DEMO_AGENT_MODEL` in your `.env` file (see [`agent.py:11-16`](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/google_search_agent/agent.py#L11-L16) and [`main.py:99-152`](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L99-L152))

### Live API Models Compatibility and Availability

For the latest information on Live API model compatibility and availability:

- **Gemini Live API models**: See the [Gemini models documentation](https://ai.google.dev/gemini-api/docs/models/gemini)
- **Gemini Live API models (Agent Platform)**: See the [Agent Platform model documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

Always verify model availability and feature support in the official documentation before deploying to production.

