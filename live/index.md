# Live and voice agents

Supported in ADKPython v0.5.0Java v0.2.0Experimental

ADK is the framework for building live and voice agents. A live agent holds an open, two-way connection with the user: instead of sending a message and waiting for a reply, the user and the agent both speak, listen, and respond at the same time, and the user can interrupt the agent mid-sentence the way people interrupt each other in real conversation. Live agents accept text, audio, and video input and reply with text or speech.

A live agent is an ADK agent, built with the same agent, tool, and session abstractions you use everywhere else. You describe the agent's behavior; ADK manages the real-time connection, tool execution, and session state underneath. Today that connection runs on the [Gemini Live API](https://ai.google.dev/gemini-api/docs/live-api); ADK handles the wiring so your agent code stays the same as the platform evolves.

## Build live agents

- **Get started**

  ______________________________________________________________________

  Build your first live agent and talk to it in the browser.

  - [Start here](https://adk.dev/live/get-started/index.md) — pick a language and build one
  - Jump straight to [Python](https://adk.dev/live/get-started/streaming-python/index.md) or [Java](https://adk.dev/live/get-started/streaming-java/index.md)

- **Building**

  ______________________________________________________________________

  The capability pages, roughly in the order you will need them.

  - [Sessions](https://adk.dev/live/sessions/index.md) — `run_live()`, resumption, scale
  - [Events](https://adk.dev/live/events/index.md) — what comes back and how to handle it
  - [Tools](https://adk.dev/live/tools/index.md) — automatic execution and streaming tools
  - [Workflows](https://adk.dev/live/workflows/index.md) — multi-agent under a live connection
  - [Audio and video](https://adk.dev/live/audio-video/index.md) — formats and streaming
  - [Configuration](https://adk.dev/live/configuration/index.md) — `RunConfig`, voice, transcription, turn detection

- **Production**

  ______________________________________________________________________

  Take a live agent beyond `adk web`.

  - [Evaluation](https://adk.dev/live/evaluation/index.md) — score voice conversations before you ship
  - [Build a custom server](https://adk.dev/live/custom-server/index.md)
  - [Supported models](https://adk.dev/live/models/index.md)

## Which kind of streaming do you need?

"Streaming" covers three different things in ADK, and picking the wrong one is a common source of confusion.

|                             | What it does                                                                  | User can interrupt? | Use it when                                             | Where                                                                                                |
| --------------------------- | ----------------------------------------------------------------------------- | ------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Server-side streaming**   | One-way flow from server to client, like a live feed.                         | No                  | You push dashboard or feed updates, not a conversation. | Outside ADK                                                                                          |
| **Token-level streaming**   | Text arrives word by word, but you wait for it to finish before sending more. | No                  | You want a responsive text chat.                        | `StreamingMode.SSE` ([Configuration](https://adk.dev/live/configuration/#streamingmode-bidi-or-sse)) |
| **Bidirectional streaming** | Both sides speak, listen, and respond at once over one open connection.       | **Yes**             | You are building voice or video conversation.           | `runner.run_live()` — these pages                                                                    |

These pages are about the third row.

```
sequenceDiagram
    participant Client as User
    participant Agent

    Client->>Agent: "Explain the history of Japan"
    Agent->>Client: "Sure! Japan's history is a..." (partial)
    Client->>Agent: "Ah, wait."
    Agent->>Client: "OK, how can I help?" [interrupted: true]
```

## Why build live agents on ADK

The Live API gives you the streaming protocol. ADK gives you everything around it, so you write agent behavior instead of streaming infrastructure.

|                     | Raw Live API (`google-genai`) | ADK                                                                               |
| ------------------- | ----------------------------- | --------------------------------------------------------------------------------- |
| Tool execution      | Manual                        | [Automatic](https://adk.dev/live/tools/#automatic-tool-execution)                 |
| Reconnection        | Manual                        | [Automatic session resumption](https://adk.dev/live/sessions/#session-resumption) |
| Events              | Custom structures             | [Unified event model](https://adk.dev/live/events/index.md)                       |
| Async coordination  | Manual                        | [`LiveRequestQueue` + `run_live()`](https://adk.dev/live/sessions/index.md)       |
| Session persistence | Manual                        | [SQL, Agent Platform, in-memory](https://adk.dev/sessions/index.md)               |
| Multi-agent         | Not available                 | [Workflows, sub-agents, transfer](https://adk.dev/live/workflows/index.md)        |

## Demos and resources

- **LensMosaic: Visual Shopping with Live AI**

  ______________________________________________________________________

  Merges live camera input, voice, and product discovery. Point your camera at any object to find similar products. Built with ADK live agents, Gemini Embedding, Vector Search, and FastAPI.

  - [Live demo](https://lens-mosaic-nhhfh7g7iq-uc.a.run.app)
  - [Source](https://github.com/kazunori279/lens-mosaic)

- **A Visual Guide to Bidi-streaming**

  ______________________________________________________________________

  Diagrams and illustrations covering how streaming works and how to build interactive agents with ADK.

  - [Read the post](https://medium.com/google-cloud/adk-bidi-streaming-a-visual-guide-to-real-time-multimodal-ai-agent-development-62dd08c81399)

- **Google ADK + Gemini Live API**

  ______________________________________________________________________

  Using live agents for real-time audio/video, with a Python server example built on `LiveRequestQueue`.

  - [Read the post](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)
