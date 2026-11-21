# Get started with live agents

The quickstarts run your agent in `adk web`, which ships a browser client that already captures the microphone, plays the agent's replies, and renders the transcript. You write the agent and pick a model; there is no client code in the way.

Your agent needs a model that can hold a two-way streaming connection. See [Supported models](https://adk.dev/live/models/index.md) for the current list and how to configure one.

## Choose your language

- **Python**

  ______________________________________________________________________

  Set up ADK, build a voice agent, and talk to it in `adk web`.

  [Python quickstart](https://adk.dev/live/get-started/streaming-python/index.md)

- **Java**

  ______________________________________________________________________

  Set up Maven, build a voice agent, and run it in `adk web` or a custom audio app.

  [Java quickstart](https://adk.dev/live/get-started/streaming-java/index.md)

## Next steps

- **[Configuration](https://adk.dev/live/configuration/index.md)** — set the voice, language, transcription, and turn detection.
- **[Tools](https://adk.dev/live/tools/index.md)** — give the agent tools it can call mid-conversation, including ones that stream results back while they run.
- **[Sessions](https://adk.dev/live/sessions/index.md)** and **[Events](https://adk.dev/live/events/index.md)** — the `run_live()` loop and everything it hands back.
- **[Evaluation](https://adk.dev/live/evaluation/index.md)** — score voice conversations before you ship.
- **[Build a custom server](https://adk.dev/live/custom-server/index.md)** — `adk web` is a development client, so this is how you run a live agent behind your own server and client.
