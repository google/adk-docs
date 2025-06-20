# Bidi-streaming(live) in ADK

!!! info

    This is an experimental feature. Currrently available in Python.

!!! info

    This is different from server-side streaming or token-leven streaming. This section is for bidi-streaming(live).
    
Bidi-streaming(live) in ADK adds the low-latency bidirectional voice and video interaction
capability of [Gemini Live API](https://ai.google.dev/gemini-api/docs/live) to
AI agents.

With bidi-streaming(live) mode, you can provide end users with the experience of natural,
human-like voice conversations, including the ability for the user to interrupt
the agent's responses with voice commands. Agents with streaming can process
text, audio, and video inputs, and they can provide text and audio output.

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/Tu7-voU7nnw?si=RKs7EWKjx0bL96i5" title="Shopper's Concierge" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>

  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/LwHPYyw7u6U?si=xxIEhnKBapzQA6VV" title="Shopper's Concierge" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>
</div>

<div class="grid cards" markdown>

-   :material-console-line: **Quickstart (Streaming)**

    ---

    In this quickstart, you'll build a simple agent and use streaming in ADK to
    implement low-latency and bidirectional voice and video communication.

    - [Quickstart (Bidi-streaming)](../get-started/streaming/quickstart-streaming.md)

-   :material-console-line: **Custom Audio Streaming app sample**

    ---

    This article overviews the server and client code for a custom asynchronous web app built with ADK Streaming and FastAPI, enabling real-time, bidirectional audio and text communication with both Server Sent Events (SSE) and WebSockets.

    - [Custom Audio Streaming app sample (SSE)](custom-streaming.md)
    - [Custom Audio Streaming app sample (WebSockets)](custom-streaming-ws.md)

-   :material-console-line: **Bidi-streaming development guide series**

    ---

    A series of articles for diving deeper into the Bidi-streaming development with ADK. You can learn basic concepts and use cases, the core API, and end-to-end application design.

    - [Bidi-streaming development guide series: Part 1 - Introduction](dev-guide/part1.md)

-   :material-console-line: **Streaming Tools**

    ---

    Streaming tools allows tools (functions) to stream intermediate results back to agents and agents can respond to those intermediate results. For example, we can use streaming tools to monitor the changes of the stock price and have the agent react to it. Another example is we can have the agent monitor the video stream, and when there is changes in video stream, the agent can report the changes.

    [:octicons-arrow-right-24: More information](streaming-tools.md)

-   :material-console-line: **Custom Audio Streaming app sample**

    ---

    This article overviews the server and client code for a custom asynchronous web app built with ADK Streaming and FastAPI, enabling real-time, bidirectional audio and text communication with both Server Sent Events (SSE) and WebSockets.

    [:octicons-arrow-right-24: More information (SSE)](custom-streaming.md) and 
    [:octicons-arrow-right-24: (WebSockets)](custom-streaming-ws.md)

-   :material-console-line: **Blog post: Google ADK + Vertex AI Live API**

    ---

    This article shows how to use Bidi-streaming (live) in ADK for real-time audio/video streaming. It offers a Python server example using LiveRequestQueue to build custom, interactive AI agents.

    [:octicons-arrow-right-24: More information](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

-   :material-console-line: **Shopper's Concierge demo**

    ---

    Learn how streaming in ADK can be used to build a personal shopping
    concierge that understands your personal style and offers tailored
    recommendations.

    [:octicons-arrow-right-24: More information](https://youtu.be/LwHPYyw7u6U)

-   :material-console-line: **Streaming Configurations**

    ---

    There are some configurations you can set for live(streaming) agents.

    [:octicons-arrow-right-24: More information](configuration.md)
</div>

