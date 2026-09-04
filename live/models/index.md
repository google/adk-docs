# Supported models for live agents

Supported in ADKPython v0.1.0

Live agents require a model that can hold a bidirectional connection; a standard Gemini model will not. For the models ADK supports outside live agents, and for non-Gemini providers, see [Models for agents](https://adk.dev/agents/models/index.md).

## Live models

Live agents run on models that take audio in and produce audio out, end to end, with no intermediate text-to-speech stage. That is what gives them human-like speech with natural prosody, and it is what a standard Gemini model cannot do over a bidirectional connection.

The same model has a different ID on each backend:

| Model                 | AI Studio                                       | Agent Platform                       |
| --------------------- | ----------------------------------------------- | ------------------------------------ |
| Gemini 2.5 Flash Live | `gemini-2.5-flash-native-audio-preview-12-2025` | `gemini-live-2.5-flash-native-audio` |

`gemini-live-2.5-flash-native-audio` is ADK's `LlmAgent.DEFAULT_LIVE_MODEL` and the model used in this section's examples.

## Choosing a backend

Live models are reached through one of two backends. ADK talks to both with the same code; you switch with environment variables, so you can develop on one and deploy on the other.

|               | AI Studio                                                       | Agent Platform                                                      |
| ------------- | --------------------------------------------------------------- | ------------------------------------------------------------------- |
| **Full name** | Google AI Studio                                                | Gemini Enterprise Agent Platform                                    |
| **Best for**  | Prototyping, development                                        | Production, enterprise                                              |
| **Auth**      | API key (`GOOGLE_API_KEY`)                                      | Cloud credentials (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) |
| **Setup**     | API key only                                                    | Cloud project setup                                                 |
| **Limits**    | [Session duration and concurrency](#platform-limits-and-quotas) | [Session duration and concurrency](#platform-limits-and-quotas)     |

Switch with the `GOOGLE_GENAI_USE_ENTERPRISE` environment variable (`FALSE` for AI Studio, `TRUE` for Agent Platform); no code changes. See the [quickstarts](https://adk.dev/live/get-started/streaming-python/index.md) for setup.

Agent Platform: confirm location support

Live model availability varies by location on Agent Platform. Check your `GOOGLE_CLOUD_LOCATION` against the endpoint-locations table in [Agent Platform locations](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations) before deploying; a regional endpoint such as `us-central1`, `us-east1`, or `asia-northeast1` is the safe default.

These models produce audio directly, with natural prosody, and detect the conversation language on their own. What you configure on top — voices, transcription, turn detection — is described in [Configuration](https://adk.dev/live/configuration/index.md).

One property is fixed at the model level: Live models produce **audio only**. They do not support the `TEXT` response modality, so to get text alongside speech you use [audio transcription](https://adk.dev/live/configuration/#audio-transcription).

### Per-model feature support

A few `RunConfig` settings depend on which model you are running:

| Feature                                                                                                  | `gemini-live-2.5-flash-native-audio` |
| -------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| [Proactivity and affective dialog](https://adk.dev/live/configuration/#proactivity-and-affective-dialog) | Opt-in via `RunConfig`               |
| [`response_scheduling`](https://adk.dev/live/tools/#non-blocking-tools) on tools                         | Supported                            |

## Platform limits and quotas

Both backends cap how long a connection and a session can run and how many sessions run at once. These numbers change, so treat the upstream documentation as authoritative and verify before you rely on a limit in production.

| Limit                           | AI Studio                                                            | Agent Platform                                                                 |
| ------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Session duration, audio-only    | 15 min                                                               | 15 min                                                                         |
| Session duration, audio + video | 2 min                                                                | 2 min                                                                          |
| Connection lifetime             | ~10 min                                                              | ~10 min                                                                        |
| Concurrent sessions             | See [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) | Up to 1,000 per project on pay-as-you-go; no limit with Provisioned Throughput |

Agent Platform additionally caps a conversation session at 10 minutes by default, separately from the audio-only limit above.

Enabling [context window compression](https://adk.dev/live/sessions/#context-window-compression) lets a session be extended past the duration limits. On Agent Platform, request concurrent-session increases from the [Cloud Console Quotas page](https://console.cloud.google.com/iam-admin/quotas) under **"Bidi generate content concurrent requests"**. Verify the current numbers against the [AI Studio](https://ai.google.dev/gemini-api/docs/live-api/capabilities), [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), and [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api/start-manage-session) documentation.

## How to handle model names

Read the model name from an environment variable rather than hard-coding it. The same model has a different ID on AI Studio and Agent Platform, so an `.env` var is what lets one codebase target both backends, and it insulates you from model deprecations.

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

Environment Variable Loading Order

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
1. **Check current availability**: Refer to the model table above and the official documentation
1. **Configure environment variable**: Set the model name in your `.env` file and read it from there when constructing the agent

## Model compatibility and availability

For the latest information on model compatibility and availability:

- **AI Studio**: See the [Gemini models documentation](https://ai.google.dev/gemini-api/docs/models) and the [Live API capabilities guide](https://ai.google.dev/gemini-api/docs/live-api/capabilities)
- **Agent Platform**: See the [Live API overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api) and the [Agent Platform model documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models)

Always verify model availability and feature support in the official documentation before deploying to production.
