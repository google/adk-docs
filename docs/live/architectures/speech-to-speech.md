# Speech-to-speech architecture

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

In a speech-to-speech architecture, a single multimodal model processes incoming audio, executes reasoning and tool calls, and generates spoken audio directly over a persistent [Gemini Live API](https://ai.google.dev/gemini-api/docs/live-api) connection, without converting the speech to text between the input and output..

For a comparison with chained STT-LLM-TTS pipelines, see [Choose a voice architecture](index.md).

## Configure a speech-to-speech agent

Pass a supported [native audio Live model](../models.md#live-models) to your agent:

=== "Python"

    ```python
    import os
    from google.adk.agents import Agent

    root_agent = Agent(
        name="voice_assistant",
        model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
        instruction="You are a helpful voice assistant.",
        tools=[...],
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;

    LlmAgent rootAgent =
        LlmAgent.builder()
            .name("voice_assistant")
            .model("gemini-live-2.5-flash-native-audio")
            .instruction("You are a helpful voice assistant.")
            .build();
    ```

Run the agent with `adk web` or pass it to [`Runner.run_live()`](../sessions.md#the-run_live-loop).

## Capabilities specific to speech-to-speech

The following capabilities apply specifically to native audio models:

- **Live video and image input**: Stream live camera or screen frames alongside audio so the agent can see what the user is showing. See [Audio and video](../audio-video.md#images-and-video).
- **Affective dialog and proactive audio**: Supported native audio models can adapt their spoken tone to the user's emotional expression and decide when to speak or stay silent. See [Proactivity and affective dialog](../configuration.md#proactivity-and-affective-dialog).
- **Stateful session resumption and context compression**: Because the Live API holds conversation state in a stateful WebSocket session, ADK supports automatic [session resumption](../sessions.md#session-resumption) across connection timeouts and [context window compression](../sessions.md#context-window-compression) for long-running sessions.
- **Session-level voice and VAD controls**: Configure voice selection and automatic voice activity detection (VAD) at the session level through [`RunConfig`](../configuration.md) or on the model instance.

## Considerations and limitations

- **Fixed model selection**: Speech-to-speech requires a model that supports the Gemini Live API ([Supported models](../models.md#live-models)). To use standard Gemini text models or third-party LLMs in a live voice session, use the [Cascaded architecture](cascade.md).
- **Audio-only output**: Native audio models output audio only and do not run under `Runner.run_async()`. Read [audio transcriptions](../configuration.md#audio-transcription) when you need the text of the conversation.
- **Guardrails evaluate transcriptions alongside audio**: Because the model generates audio directly without an intermediate text stage, [conversation validation callbacks](../guardrails.md#conversation-validation) screen input and output transcriptions rather than intercepting text before synthesis. If you must filter or redact text before audio is generated, use [Cascade](cascade.md#custom-speech-transforms).
