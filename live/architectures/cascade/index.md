# Cascaded architecture

Supported in ADKPython v2.13.0Experimental

In a cascaded architecture, `CascadeLive` chains streaming speech-to-text (STT), a text-reasoning LLM, and streaming text-to-speech (TTS). Audio flows through three stages in sequence: speech recognition transcribes user audio to text, the LLM reasons over text and calls tools, and speech synthesis converts the streamed text reply into audio.

You configure `CascadeLive` on the agent's `model` parameter, so your [`Runner.run_live()`](https://adk.dev/live/sessions/#the-run_live-loop) loop, request queue, tools, callbacks, and workflows stay unchanged. The same agent also works with `Runner.run_async()` for text-only requests, bypassing the speech stages and calling the inner text model directly.

For a comparison with native speech-to-speech models, see [Choose a voice architecture](https://adk.dev/live/architectures/index.md).

## Configure a cascaded agent

Pass a `CascadeLive` instance to `Agent` with a text LLM, a speech-to-text provider, and a text-to-speech provider:

`GeminiSTT` and `GeminiTTS` in `google.adk.live` use your existing Google credentials and require no extra packages.

```python
from google.adk.agents import Agent
from google.adk.live import CascadeLive, GeminiSTT, GeminiTTS
from google.genai import types

root_agent = Agent(
    name="voice_assistant",
    model=CascadeLive(
        model="gemini-3.8-flash",
        stt=GeminiSTT(),
        tts=GeminiTTS(speech_config="Kore"),
    ),
    instruction=(
        "You are a voice assistant. Keep answers to one or two short "
        "sentences and end every sentence with punctuation. Write numbers, "
        "symbols, and abbreviations as spoken words."
    ),
    tools=[...],
    generate_content_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=types.ThinkingLevel.LOW
        ),
    ),
)
```

Install the ElevenLabs extra (`pip install "google-adk[elevenlabs]"`) and set `ELEVENLABS_API_KEY` in your environment.

```python
from google.adk.agents import Agent
from google.adk.integrations.eleven_labs import ElevenLabsSTT, ElevenLabsTTS
from google.adk.live import CascadeLive
from google.genai import types

root_agent = Agent(
    name="voice_assistant",
    model=CascadeLive(
        model="gemini-3.8-flash",
        stt=ElevenLabsSTT(),
        tts=ElevenLabsTTS(),
    ),
    instruction=(
        "You are a voice assistant. Keep answers to one or two short "
        "sentences and end every sentence with punctuation. Write numbers, "
        "symbols, and abbreviations as spoken words."
    ),
    tools=[...],
    generate_content_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=types.ThinkingLevel.LOW
        ),
    ),
)
```

Two settings on the agent directly affect voice latency and synthesis quality:

- **Minimize model thinking**: Model thinking runs before the first response token is emitted and adds directly to time-to-first-audio. Set a low thinking level (or a zero thinking budget on models that use token budgets) in `generate_content_config`.
- **Prompt for sentence punctuation and no abbreviations**: Built-in TTS providers split text at sentence boundaries so the first sentence starts playing before the LLM finishes its full reply. An abbreviation in the first sentence such as `Dr. Smith` can trigger an early split, and unpunctuated output buffers longer before playback starts.

Run the agent with `adk web` or drive it with [`Runner.run_live()`](https://adk.dev/live/sessions/#the-run_live-loop). A complete runnable example with both Gemini and ElevenLabs speech providers is available in the [`cascade` sample](https://github.com/google/adk-python/tree/main/contributing/samples/live/cascade).

## How it works

```
sequenceDiagram
    participant Client
    participant STT as Speech-to-Text
    participant LLM as Text LLM
    participant TTS as Text-to-Speech

    Client->>STT: Stream user audio
    STT-->>Client: Partial input transcription
    STT->>LLM: Final user transcript
    LLM->>TTS: Streamed text tokens
    TTS-->>Client: Synthesized audio chunks
    TTS-->>Client: Spoken output transcription
```

### Captions and turn detection

- **Live captions replace rather than append**: While the user speaks, interim transcripts arrive on `event.input_transcription`. Unlike native audio models that stream incremental word fragments, each interim update in cascaded mode holds the full utterance hypothesis so far, so your client should replace the displayed caption rather than append to it.
- **Custom vocabulary and client-controlled VAD**: Server voice activity detection (VAD) is enabled by default. To supply domain vocabulary or control turn boundaries from the client (such as push-to-talk) with `GeminiSTT`, pass `audio_transcription_config` or disable automatic activity detection and call [`send_activity_start()` and `send_activity_end()`](https://adk.dev/live/sessions/#liverequestqueue):

```python
from google.adk.live import GeminiSTT
from google.genai import types

stt = GeminiSTT(
    audio_transcription_config=types.AudioTranscriptionConfig(
        language_codes=["en-US"],
        custom_vocabulary=["Cymbal Direct", "Altostrat"],
    ),
    activity_detection=types.AutomaticActivityDetection(disabled=True),
)
```

### Barge-in truncates history to what the user heard

TTS providers synthesize upcoming sentences faster than real-time playback, so when a user interrupts mid-reply, the client buffer often holds audio the user has not heard yet.

When an interruption occurs, `CascadeLive` halts synthesis and LLM generation, emits an interrupted event so the client stops playback, and estimates how much audio actually played on the client. Only the words the user heard are saved to session history and the final `output_transcription`, so subsequent turns never reference unspoken text.

## Custom speech transforms

To integrate another speech provider or inspect text between stages, subclass `LiveIngress` (for speech-to-text) or `LiveEgress` (for text-to-speech) from `google.adk.live`:

- `LiveIngress` reads the incoming audio stream and yields speech-start, partial-transcript, and turn-finished events (`UserSpeechStarted`, `PartialTranscript`, `UserTurnFinished`).
- `LiveEgress` reads the streamed LLM text deltas and yields synthesized audio chunks and spoken transcript events (`AudioChunk`, `AgentSpokenOutput`) until completion or cancellation.

Because LLM output is plain text before synthesis, you can wrap any `LiveEgress` to redact or transform text before a single audio frame is generated:

```python
import asyncio
from typing import AsyncGenerator, AsyncIterator
from google.adk.live import EgressEvent, LiveEgress


class RedactingTTS(LiveEgress):
    """Redacts sensitive patterns from streamed LLM text before synthesis."""

    def __init__(self, inner_tts: LiveEgress, redact_fn):
        self._tts = inner_tts
        self._redact = redact_fn

    async def __call__(
        self, text: AsyncIterator[str], *, cancel: asyncio.Event
    ) -> AsyncGenerator[EgressEvent, None]:
        async def sanitized_text() -> AsyncGenerator[str, None]:
            async for delta in text:
                yield self._redact(delta)

        async for event in self._tts(sanitized_text(), cancel=cancel):
            yield event
```

## Considerations and limitations

- **Silence-based turn detection**: Server VAD ends a user turn after a silence threshold, so a long mid-sentence pause can split an utterance into two turns. Adjust the silence threshold on the STT provider or use client-controlled activity signals.
- **Avoid speaking during synchronous tool execution**: If a user finishes speaking while a synchronous tool call is still running, the new user turn lands between the tool call and its response, causing subsequent model requests in that session to fail.
- **Client echo cancellation**: Use browser or hardware acoustic echo cancellation (AEC) or headphones so speaker output is not picked up by the microphone as a false user interruption.
