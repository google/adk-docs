# Supported models

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

Live agents require a Live API model — a standard Gemini model will not hold a
bidirectional connection. For the models ADK supports outside live agents, and for
non-Gemini providers, see [Models for agents](../agents/models/index.md).

## Live models

Live agents run on models that take audio in and produce audio out, end to end, with no
intermediate text-to-speech stage. That is what gives them human-like speech with natural
prosody, and it is what a standard Gemini model cannot do over a bidirectional connection.

The same model has a different ID on each backend:

| Model | AI Studio | Agent Platform |
|-------|-----------|----------------|
| Gemini 2.5 Flash Live | `gemini-2.5-flash-native-audio-preview-12-2025` | `gemini-live-2.5-flash-native-audio` |

`gemini-live-2.5-flash-native-audio` is ADK's `LlmAgent.DEFAULT_LIVE_MODEL` and the model
used in this section's examples.

## Choosing a backend

Live models are reached through one of two backends. ADK talks to both with the same code;
you switch with environment variables, so you can develop on one and deploy on the other.

| | AI Studio | Agent Platform |
|---|---|---|
| **Full name** | Google AI Studio | Gemini Enterprise Agent Platform |
| **Best for** | Prototyping, development | Production, enterprise |
| **Auth** | API key (`GOOGLE_API_KEY`) | Cloud credentials (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) |
| **Setup** | API key only | Cloud project setup |
| **Limits** | [Session duration and concurrency](#platform-limits-and-quotas) | [Session duration and concurrency](#platform-limits-and-quotas) |

Switch with the `GOOGLE_GENAI_USE_ENTERPRISE` environment variable (`FALSE` for AI Studio,
`TRUE` for Agent Platform); no code changes. See the
[quickstarts](get-started/streaming-python.md) for setup.

!!! note "Agent Platform: the `global` location is not supported"

    Live models are not available at `GOOGLE_CLOUD_LOCATION=global` on Agent Platform.
    Use a regional endpoint (for example `us-central1`, `us-east1`, or `asia-northeast1`).
    See [Agent Platform locations](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations)
    for the current list.

These models produce audio directly, with natural prosody, and detect the conversation
language on their own. What you configure on top — voices, transcription, turn detection —
is described in [Configuration](configuration.md).

One property is fixed at the model level: Live models produce **audio only**. They do not
support the `TEXT` response modality, so to get text alongside speech you use
[audio transcription](configuration.md#audio-transcription).

### Per-model feature support

A few `RunConfig` settings depend on which model you are running:

| Feature | `gemini-live-2.5-flash-native-audio` |
|---|---|
| [Proactivity and affective dialog](configuration.md#proactivity-and-affective-dialog) | Opt-in via `RunConfig` |
| [`response_scheduling`](tools.md#non-blocking-tools) on tools | Supported |

## Platform limits and quotas

Both backends cap how long a connection and a session can run and how many sessions run at
once. These numbers change, so treat the upstream documentation as authoritative and verify
before you rely on a limit in production.

| Limit | AI Studio | Agent Platform |
|---|---|---|
| Connection duration | ~10 min (ADK reconnects transparently via [session resumption](sessions.md#session-resumption)) | Not documented separately |
| Session duration, audio-only | 15 min | 10 min |
| Session duration, audio + video | 2 min | 10 min |
| Concurrent sessions | 50 (Tier 1), 1,000 (Tier 2+) | Up to 1,000 per project |
| New-connection rate | [Tier-based](https://ai.google.dev/gemini-api/docs/quota) | 10 per minute |

Enabling [context window compression](sessions.md#context-window-compression) removes the
session-duration limits on both backends. On Agent Platform, request concurrent-session
increases from the [Cloud Console Quotas page](https://console.cloud.google.com/iam-admin/quotas)
under **"Bidi generate content concurrent requests"**. Verify the current numbers against the
[AI Studio](https://ai.google.dev/gemini-api/docs/live-api/capabilities),
[Gemini API quotas](https://ai.google.dev/gemini-api/docs/quota), and
[Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api)
documentation.

## How to handle model names

Read the model name from an environment variable rather than hard-coding it. The same model
has a different ID on AI Studio and Agent Platform, so an env var is what lets one codebase
target both backends, and it insulates you from model deprecations.

**Recommended Pattern:**

```python
import os
from google.adk.agents import Agent

# Use environment variable with fallback to a sensible default
agent = Agent(
    name="my_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
    tools=[...],
    instruction="..."
)
```

**Why use environment variables:**

- **Backend-specific IDs**: The same model is named differently on AI Studio and Agent Platform, so moving between them means changing the model ID. An env var keeps that out of your code
- **Model availability changes**: Models are released and deprecated regularly. A live agent written a year ago should not be pinned in code to a model that no longer exists
- **Environment-specific configuration**: Use different models for development, staging, and production

**Configuration in `.env` file:**

```bash
# AI Studio
DEMO_AGENT_MODEL=gemini-2.5-flash-native-audio-preview-12-2025

# Agent Platform
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

1. **Choose a backend**: AI Studio for prototyping, Agent Platform for production. This picks the ID column in the table above
2. **Check current availability**: Refer to the model table above and the official documentation
3. **Configure environment variable**: Set the model name in your `.env` file and read it from there when constructing the agent

## Model compatibility and availability

For the latest information on Live API model compatibility and availability:

- **AI Studio**: See the [Gemini models documentation](https://ai.google.dev/gemini-api/docs/models) and the [Live API capabilities guide](https://ai.google.dev/gemini-api/docs/live-api/capabilities)
- **Agent Platform**: See the [Live API overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api) and the [Agent Platform model documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models)

Always verify model availability and feature support in the official documentation before deploying to production.

