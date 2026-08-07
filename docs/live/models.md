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

| Platform | Model | Stage | Notes |
|----------|-------|-------|-------|
| Gemini Live API | [gemini-3.1-flash-live-preview](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview) | Preview | Newest. Lower latency, but no proactivity or affective dialog — see the caveats below |
| Gemini Live API | [gemini-2.5-flash-native-audio-preview-12-2025](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-native-audio-preview-12-2025) | Preview | Full feature set, including proactivity and affective dialog |
| Gemini Live API (Agent Platform) | [gemini-live-2.5-flash-native-audio](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/2-5-flash-live-api) | **GA** | The only Live API model on Agent Platform. Also ADK's `LlmAgent.DEFAULT_LIVE_MODEL` |

!!! warning "Gemini 3.x Live models are Gemini Live API only"

    `gemini-3.1-flash-live-preview` runs on the Gemini Live API
    (`generativelanguage.googleapis.com`) only. There is **no Gemini 3.x Live model on
    Agent Platform** — if you are on Agent Platform, `gemini-live-2.5-flash-native-audio`
    is your model.

!!! warning "What `gemini-3.1-flash-live-preview` does not support"

    Before switching from `gemini-2.5-flash-native-audio-preview-12-2025`, check that you
    do not depend on any of these:

    - **[Proactivity and affective dialog](voice.md#proactivity-and-affective-dialog)** are
      not supported. Remove `RunConfig.proactivity` and
      `RunConfig.enable_affective_dialog` — leaving them set is the most common upgrade
      failure
    - **Asynchronous function calling** is not supported; function calling is synchronous
      only, so the model will not speak again until you return the tool response
    - **Thinking** is configured with `thinking_level` (`minimal`, `low`, `medium`, `high`),
      not `thinking_budget`
    - **Server events carry multiple content parts at once.** If your client assumes
      `event.content.parts[0]` is the whole payload, iterate over `parts` instead
    - **Turn coverage** now defaults to including all detected audio activity and video
      frames, which can change your token costs

!!! note "Agent Platform: the `global` location is not supported"

    Live API models are not available at `GOOGLE_CLOUD_LOCATION=global` on Agent Platform.
    Use a regional endpoint (for example `us-central1`, `us-east1`, or `asia-northeast1`).
    See [Agent Platform locations](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations)
    for the current list.

**Key characteristics:**

- **End-to-end audio processing**: Processes audio input and generates audio output directly without converting to text intermediately
- **Natural prosody**: Produces more human-like speech patterns, intonation, and emotional expressiveness
- **Extended voice library**: Supports the eight prebuilt Live API voices plus additional voices from the Text-to-Speech (TTS) service — see [Voice configuration](voice.md#supported-voices)
- **Automatic language detection**: Determines language from conversation context without explicit configuration
- **Advanced conversational features**:
  - **[Affective dialog](voice.md#proactivity-and-affective-dialog)**: Adapts response style to input expression and tone, detecting emotional cues. Supported on `gemini-2.5-flash-native-audio-preview-12-2025` and `gemini-live-2.5-flash-native-audio`, **not** on `gemini-3.1-flash-live-preview`
  - **[Proactive audio](voice.md#proactivity-and-affective-dialog)**: Can proactively decide when to respond, offer suggestions, or ignore irrelevant input. Same model support as affective dialog
  - **Dynamic thinking**: Supports thought summaries and thinking controls (`thinking_budget` on 2.5, `thinking_level` on 3.1)
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

- **Model availability changes**: Models are released, updated, and deprecated regularly. `gemini-2.0-flash-live-001` was deprecated on December 09, 2025, and `gemini-3.1-flash-live-preview` arrived in March 2026 — a live agent written a year ago will not be pinned to a model that still exists
- **Platform-specific names**: Gemini Live API and Gemini Live API on Agent Platform use different model naming conventions for the same functionality
- **Easy switching**: Change models without modifying code by updating the `.env` file
- **Environment-specific configuration**: Use different models for development, staging, and production

**Configuration in `.env` file:**

```bash
# For Gemini Live API
DEMO_AGENT_MODEL=gemini-2.5-flash-native-audio-preview-12-2025

# ...or the newer Gemini 3.1 model, if you do not need proactivity or
# affective dialog
# DEMO_AGENT_MODEL=gemini-3.1-flash-live-preview

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

1. **Choose platform**: Decide between Gemini Live API (public) or Gemini Live API on Agent Platform (enterprise). This narrows the model list for you — Agent Platform has exactly one Live API model
2. **Check current availability**: Refer to the model table above and the official documentation
3. **Configure environment variable**: Set `DEMO_AGENT_MODEL` in your `.env` file (see [`agent.py:17-39`](https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/google_search_agent/agent.py#L17-L39) and [`main.py:36-41`](https://github.com/google/adk-docs/blob/main/examples/python/snippets/streaming/bidi-demo/app/main.py#L36-L41))

## Model compatibility and availability

For the latest information on Live API model compatibility and availability:

- **Gemini Live API models**: See the [Gemini models documentation](https://ai.google.dev/gemini-api/docs/models) and the [Live API capabilities guide](https://ai.google.dev/gemini-api/docs/live-api/capabilities)
- **Gemini Live API models (Agent Platform)**: See the [Live API overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api) and the [Agent Platform model documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models)

Always verify model availability and feature support in the official documentation before deploying to production.

