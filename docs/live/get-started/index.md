# Get started

The quickstarts run your agent in `adk web`, which ships a browser client that already
captures the microphone, plays the agent's replies, and renders the transcript. You write the
agent and pick a model; there is no client code in the way.

Your agent needs a model that can hold a two-way streaming connection. See
[Supported models](../models.md) for the current list and how to configure one.

## Choose your language

<!-- Adding a language: copy a card block below, then add the page under
     Live and Voice Agents > Get started in mkdocs.yml. -->

<div class="grid cards" markdown>

-   :fontawesome-brands-python:{ .lg .middle } **Python**

    ---

    Set up ADK, build a voice agent, and talk to it in `adk web`.

    [:octicons-arrow-right-24: Python quickstart](streaming-python.md)

-   :fontawesome-brands-java:{ .lg .middle } **Java**

    ---

    Set up Maven, build a voice agent, and run it in `adk web` or a custom audio app.

    [:octicons-arrow-right-24: Java quickstart](streaming-java.md)

</div>

## Next steps

- **[Configuration](../configuration.md)** — set the voice, language, transcription, and
  turn detection.
- **[Tools](../tools.md)** — give the agent tools it can call mid-conversation, including
  ones that stream results back while they run.
- **[Sessions](../sessions.md)** and **[Events](../events.md)** — the `run_live()` loop and
  everything it hands back.
- **[Evaluation](../evaluation.md)** — score voice conversations before you ship.
- **[Build a custom server](../custom-server.md)** — `adk web` is a development client, so
  this is how you run a live agent behind your own server and client.
