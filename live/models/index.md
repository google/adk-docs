# Supported models for live agents

Supported in ADKPython v0.1.0

Live agents run in one of two [voice architectures](https://adk.dev/live/architectures/index.md) under `run_live()`:

- **[Speech-to-speech](https://adk.dev/live/architectures/speech-to-speech/index.md)**: A single native audio Live model handles audio input and audio output directly over a bidirectional connection.
- **[Cascade](https://adk.dev/live/architectures/cascade/index.md)**: Chains speech-to-text, any text LLM, and text-to-speech in sequence.

## Native audio models

Native audio models take audio in and produce audio out end to end, with no intermediate text-to-speech stage. That gives them natural prosody over a single bidirectional connection.

| Model                             | AI Studio                                                 | Agent Platform                            |
| --------------------------------- | --------------------------------------------------------- | ----------------------------------------- |
| Gemini 2.5 Flash Live             | `gemini-2.5-flash-native-audio-preview-12-2025` (Preview) | `gemini-live-2.5-flash-native-audio` (GA) |
| Gemini 3.1 Flash Live             | `gemini-3.1-flash-live-preview` (Preview)                 | Not available                             |
| Gemini 3.8 Live                   | `gemini-3.8-live` (GA)                                    | `gemini-3.8-live` (GA)                    |
| Gemini 3.8 Live Extended Thinking | `gemini-3.8-live-extended-thinking` (GA)                  | Not available                             |

Gemini 2.5 Flash Live is one model with a different ID on each backend; the features are the same either way. ADK's `LlmAgent.DEFAULT_LIVE_MODEL` is `gemini-live-2.5-flash-native-audio`, which is also the model used in this section's examples.

Gemini 3.1 Flash Live is available only on AI Studio and does not support non-blocking tools. For details, see [Per-model feature support](#per-model-feature-support) and the [Gemini 3.1 Flash Live model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview).

Gemini 3.8 Live runs on both backends. Gemini 3.8 Live Extended Thinking adds background reasoning, is available only on AI Studio, and requires changes to your agent, which are listed in [Per-model feature support](#per-model-feature-support). To compare the two models, see the Gemini 3.8 Live model page for [AI Studio](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live) or [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-live), and the [Gemini 3.8 Live Extended Thinking model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live-extended-thinking).

These models produce **audio only** and detect the conversation language automatically. They do not support the `TEXT` response modality, so to get text alongside speech you use [audio transcription](https://adk.dev/live/configuration/#audio-transcription). Voice selection, transcription, and turn detection are covered in [Configuration](https://adk.dev/live/configuration/index.md).

### Per-model feature support

A few ADK settings behave differently depending on which model you are running:

| Feature                                                                                                  | Gemini 2.5 Flash Live  | Gemini 3.1 Flash Live        | Gemini 3.8 Live              | Gemini 3.8 Live Extended Thinking          |
| -------------------------------------------------------------------------------------------------------- | ---------------------- | ---------------------------- | ---------------------------- | ------------------------------------------ |
| [Proactivity and affective dialog](https://adk.dev/live/configuration/#proactivity-and-affective-dialog) | Opt-in via `RunConfig` | `RunConfig` settings ignored | `RunConfig` settings ignored | `RunConfig` settings ignored               |
| [Non-blocking tools](https://adk.dev/live/tools/#non-blocking-tools)                                     | Supported              | Not supported                | Supported                    | Required on every tool (see below)         |
| [`response_scheduling`](https://adk.dev/live/tools/#non-blocking-tools) on tools                         | Supported              | Not supported                | Supported                    | Not supported                              |
| [End of the model's response](https://adk.dev/live/events/#interaction-status)                           | `turn_complete`        | `turn_complete`              | `turn_complete`              | `interaction_status` is `IDLE` (see below) |

When moving from 2.5 to a newer model, iterate over `event.content.parts` instead of reading `parts[0]`, because a single server event can carry several parts. Turn coverage can also include all detected audio activity and video frames, which changes token costs if you stream video continuously. See the upstream [migration notes](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview#migrating-from-gemini-25-flash-live).

Each model's page in the [AI Studio](https://ai.google.dev/gemini-api/docs/models) and [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models) documentation covers model-level behavior, such as supported thinking levels. In ADK, you set thinking through the agent's `generate_content_config.thinking_config`.

Gemini 3.8 Live Extended Thinking requires ADK Python 2.10 or higher and two changes to your agent:

- **Non-blocking tools**: Set `behavior = types.Behavior.NON_BLOCKING` on every tool, and leave `response_scheduling` unset. See [Non-blocking tools](https://adk.dev/live/tools/#non-blocking-tools).
- **Interaction status**: Because `turn_complete` can arrive several times per request, read `event.interaction_status` (`interactionStatus` over `/run_live`), which is `IN_PROGRESS` while the model is still working on the request and `IDLE` once it has finished. See [Interaction status](https://adk.dev/live/events/#interaction-status).

## Cascaded models

In a [cascaded architecture](https://adk.dev/live/architectures/cascade/index.md), the reasoning stage accepts any text model in [Models for agents](https://adk.dev/agents/models/index.md). For the speech stages, ADK supports the following Gemini speech models:

| Stage                            | Model                                               |
| -------------------------------- | --------------------------------------------------- |
| **Speech-to-text (`GeminiSTT`)** | `gemini-3.5-transcribe-live`                        |
| **Text-to-speech (`GeminiTTS`)** | `gemini-3.8-flash-lite-tts`, `gemini-3.8-flash-tts` |

`CascadeLive` also includes built-in adapters for [ElevenLabs models](https://elevenlabs.io/docs/overview/models) (`ElevenLabsSTT`, `ElevenLabsTTS`) and supports any other speech provider through [custom transforms](https://adk.dev/live/architectures/cascade/#custom-speech-transforms).

## Choosing a backend

Gemini models are reached through one of two backends. ADK talks to both with the same code; you switch with environment variables, so you can develop on one and deploy on the other.

|               | AI Studio                                                       | Agent Platform                                                      |
| ------------- | --------------------------------------------------------------- | ------------------------------------------------------------------- |
| **Full name** | Google AI Studio                                                | Gemini Enterprise Agent Platform                                    |
| **Best for**  | Prototyping, development                                        | Production, enterprise                                              |
| **Auth**      | API key (`GOOGLE_API_KEY`)                                      | Cloud credentials (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) |
| **Setup**     | API key only                                                    | Cloud project setup                                                 |
| **Limits**    | [Session duration and concurrency](#platform-limits-and-quotas) | [Session duration and concurrency](#platform-limits-and-quotas)     |

Switch with the `GOOGLE_GENAI_USE_ENTERPRISE` environment variable (`FALSE` for AI Studio, `TRUE` for Agent Platform); no code changes. See the [quickstarts](https://adk.dev/live/get-started/streaming-python/index.md) for setup.

Agent Platform: the `global` location is not supported for Live API models

Live API models are not available at `GOOGLE_CLOUD_LOCATION=global`. Use a regional endpoint such as `us-central1`, `us-east1`, or `asia-northeast1`, and check it against the endpoint-locations table in [Agent Platform locations](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations) before deploying.

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

# AI Studio or Agent Platform
# DEMO_AGENT_MODEL=gemini-3.8-live

# AI Studio, for multi-step reasoning and slow tools
# DEMO_AGENT_MODEL=gemini-3.8-live-extended-thinking

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

1. **Choose a backend**: AI Studio for prototyping, Agent Platform for production. This picks the ID column in the table above, and on Agent Platform it narrows the choice to Gemini 2.5 Flash Live and Gemini 3.8 Live
1. **Check current availability**: Refer to the model table above and the official documentation
1. **Configure environment variable**: Set the model name in your `.env` file and read it from there when constructing the agent

## Model compatibility and availability

For the latest information on model compatibility and availability:

- **AI Studio**: See the [Gemini models documentation](https://ai.google.dev/gemini-api/docs/models) and the [Live API capabilities guide](https://ai.google.dev/gemini-api/docs/live-api/capabilities)
- **Agent Platform**: See the [Live API overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api) and the [Agent Platform model documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models)

Always verify model availability and feature support in the official documentation before deploying to production.
