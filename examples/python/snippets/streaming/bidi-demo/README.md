# bidi-demo

A working FastAPI application demonstrating real-time **bidirectional streaming**
with ADK and the Gemini Live API. It serves a browser UI over WebSocket and
supports text, audio, and image/video input with spoken (native audio) replies
and transcription in both directions.

This is the sample that the
[Live and Voice Agents](https://google.github.io/adk-docs/live/) documentation
walks through — in particular
[Build a custom server](https://google.github.io/adk-docs/live/custom-server/),
[Sessions and the streaming loop](https://google.github.io/adk-docs/live/sessions/),
and [Audio and video](https://google.github.io/adk-docs/live/audio-video/).

## What it demonstrates

The four phases of the ADK bidirectional streaming lifecycle:

1. **Application initialization** (once at startup) — `Agent`, `SessionService`,
   and `Runner`
2. **Session initialization** (once per connection) — `Session`, `RunConfig`,
   and `LiveRequestQueue`
3. **Bidi-streaming** — concurrent upstream (client → queue) and downstream
   (`run_live()` events → client) tasks
4. **Termination** — closing `LiveRequestQueue` in a `finally` block

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│  WebSocket  │────────▶│ LiveRequestQueue │────────▶│  Live API   │
│   Client    │◀────────│   run_live()     │◀────────│   Session   │
└─────────────┘         └──────────────────┘         └─────────────┘
  Upstream Task                                       Downstream Task
```

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/)
- A Google API key (Gemini Live API) or a Google Cloud project (Live API on
  Agent Platform)

## Setup

### 1. Install dependencies

```bash
cd examples/python/snippets/streaming/bidi-demo
uv sync
```

### 2. Configure credentials

```bash
cp app/.env.example app/.env
```

Then edit `app/.env`:

```bash
# Gemini Live API
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_api_key_here

# ...or Live API on Agent Platform
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_CLOUD_PROJECT=your_project_id
# GOOGLE_CLOUD_LOCATION=us-east1

DEMO_AGENT_MODEL=gemini-2.5-flash-native-audio-preview-12-2025
```

Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).
For Agent Platform, run `gcloud auth application-default login` instead.

### 3. Set the SSL certificate path

```bash
export SSL_CERT_FILE=$(uv run python -m certifi)
```

## Run

```bash
cd app
uv run --project .. uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> **Note:** you must run from inside `app/` so Python can import the
> `google_search_agent` module.

Then open <http://localhost:8000>.

- **Text mode** — type a message and press Enter; watch the event console for
  the raw ADK `Event` stream.
- **Audio mode** — click "Start Audio", speak, and hear the reply with live
  transcription.

## WebSocket API

```
ws://localhost:8000/ws/{user_id}/{session_id}
```

**Query parameters:**

- `proactivity` (default `false`) — enable proactive audio
- `affective_dialog` (default `false`) — enable affective dialog

Both are native-audio-only features.

**Client → server**

| Frame | Payload |
|-------|---------|
| Text | `{"type": "text", "text": "..."}` |
| Image | `{"type": "image", "data": "<base64>", "mimeType": "image/jpeg"}` |
| Binary | Raw PCM audio, 16 kHz, 16-bit |

**Server → client**: JSON-serialized ADK `Event` objects.

## Project structure

```
bidi-demo/
├── app/
│   ├── google_search_agent/
│   │   ├── __init__.py
│   │   └── agent.py              # Agent definition
│   ├── main.py                   # FastAPI app and WebSocket endpoint
│   ├── .env.example              # Credentials template
│   └── static/                   # Browser UI
│       ├── index.html
│       ├── css/style.css
│       └── js/                   # App logic, audio capture, and playback
└── pyproject.toml
```

## Supported models

This demo targets **native audio** models, which only support the `AUDIO`
response modality:

- `gemini-2.5-flash-native-audio-preview-12-2025` (Gemini Live API)
- `gemini-live-2.5-flash-native-audio` (Live API on Agent Platform)

Select one with `DEMO_AGENT_MODEL` in `app/.env`. See
[Supported models](https://google.github.io/adk-docs/live/models/) for current
availability.

## Code style

This sample follows adk-python's Python style — pyink (80 columns, 2-space
indent, majority quotes) and isort with the `google` profile. Both are pinned in
`pyproject.toml`:

```bash
uvx isort==8.0.1 app/
uvx pyink==25.12.0 app/
```

The `docs/live/*.md` pages link into these files with line anchors, so any edit
here needs those anchors re-checked:

```bash
grep -rn "snippets/streaming/bidi-demo" docs/live/
```
