# ADK Gemini Live API Toolkit

Supported in ADKPython v0.5.0Experimental

Gemini Live API Toolkit in ADK adds the low-latency bidirectional voice and video interaction capability of [Gemini Live API](https://ai.google.dev/gemini-api/docs/live) to AI agents.

With ADK Gemini Live API Toolkit, you can provide end users with the experience of natural, human-like voice conversations, including the ability for the user to interrupt the agent's responses with voice commands. Agents with streaming can process text, audio, and video inputs, and they can provide text and audio output.

## Live Demos

- **LensMosaic: Visual Shopping with Live AI**

  ______________________________________________________________________

  A demo app that merges live camera input, voice interaction, and intelligent product discovery. Point your camera at any object to find similar products, combine visual and voice input for personalized recommendations, or chat with a real-time AI shopping assistant. Built with ADK Gemini Live API Toolkit, Gemini Embedding, Vector Search, and FastAPI.

  - [LensMosaic Demo](https://lens-mosaic-nhhfh7g7iq-uc.a.run.app)
  - [Source Code](https://github.com/kazunori279/lens-mosaic)

- **ADK Gemini Live API Toolkit Demo**

  ______________________________________________________________________

  A production-ready reference implementation showcasing ADK Gemini Live API Toolkit with multimodal support (text, audio, image). This FastAPI-based demo demonstrates real-time WebSocket communication, automatic transcription, tool calling with Google Search, and complete streaming lifecycle management.

  - [Bidi Demo](https://bidi-demo-761793285222.us-central1.run.app/)
  - [Source Code](https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo)

- **Quickstart (Gemini Live API Toolkit)**

  ______________________________________________________________________

  In this quickstart, you'll build a simple agent and use streaming in ADK to implement low-latency and bidirectional voice and video communication.

  - [Quickstart (Gemini Live API Toolkit)](https://adk.dev/get-started/streaming/quickstart-streaming/index.md)

- **Gemini Live API Toolkit Demo Application**

  ______________________________________________________________________

  A production-ready reference implementation showcasing ADK Gemini Live API Toolkit with multimodal support (text, audio, image). This FastAPI-based demo demonstrates real-time WebSocket communication, automatic transcription, tool calling with Google Search, and complete streaming lifecycle management. This demo is extensively referenced throughout the development guide series.

  - [ADK Gemini Live API Toolkit Demo](https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo)

- **Blog post: ADK Gemini Live API Toolkit Visual Guide**

  ______________________________________________________________________

  A visual guide to real-time multimodal AI agent development with ADK Gemini Live API Toolkit. This article provides intuitive diagrams and illustrations to help you understand how streaming works and how to build interactive AI agents.

  - [Blog post: ADK Gemini Live API Toolkit Visual Guide](https://medium.com/google-cloud/adk-bidi-streaming-a-visual-guide-to-real-time-multimodal-ai-agent-development-62dd08c81399)

- **Gemini Live API Toolkit development guide series**

  ______________________________________________________________________

  A series of articles for diving deeper into the Gemini Live API Toolkit development with ADK. You can learn basic concepts and use cases, the core API, and end-to-end application design.

  - [Part 1: Introduction to ADK Gemini Live API Toolkit](https://adk.dev/streaming/dev-guide/part1/index.md) - Fundamentals of streaming, Live API technology, ADK architecture components, and complete application lifecycle with FastAPI examples
  - [Part 2: Sending messages with LiveRequestQueue](https://adk.dev/streaming/dev-guide/part2/index.md) - Upstream message flow, sending text/audio/video, activity signals, and concurrency patterns
  - [Part 3: Event handling with run_live()](https://adk.dev/streaming/dev-guide/part3/index.md) - Processing events, handling text/audio/transcriptions, automatic tool execution, and multi-agent workflows
  - [Part 4: Understanding RunConfig](https://adk.dev/streaming/dev-guide/part4/index.md) - Response modalities, streaming modes, session management, session resumption, context window compression, and quota management
  - [Part 5: How to Use Audio, Image and Video](https://adk.dev/streaming/dev-guide/part5/index.md) - Audio specifications, model architectures, audio transcription, voice activity detection, and proactive/affective dialog features

- **Streaming Tools**

  ______________________________________________________________________

  Streaming tools allow tools (functions) to stream intermediate results back to agents and agents can respond to those intermediate results. For example, we can use streaming tools to monitor the changes of the stock price and have the agent react to it. Another example is we can have the agent monitor the video stream, and when there are changes in video stream, the agent can report the changes.

  - [Streaming Tools](https://adk.dev/streaming/streaming-tools/index.md)

- **Blog post: Google ADK + Gemini Live API**

  ______________________________________________________________________

  This article shows how to use Gemini Live API Toolkit in ADK for real-time audio/video streaming. It offers a Python server example using LiveRequestQueue to build custom, interactive AI agents.

  - [Blog post: Google ADK + Gemini Live API](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

- **Blog post: Supercharge ADK Development with Claude Code Skills**

  ______________________________________________________________________

  This article demonstrates how to use Claude Code Skills to accelerate ADK development, with an example of building a streaming chat app. Learn how to leverage AI-powered coding assistance to build better agents faster.

  - [Blog post: Supercharge ADK Development with Claude Code Skills](https://medium.com/@kazunori279/supercharge-adk-development-with-claude-code-skills-d192481cbe72)
