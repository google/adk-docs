# Events for live agents

Supported in ADKPython v0.1.0

Everything a live agent produces reaches your application as an `Event`: partial text as the model composes it, raw audio bytes, transcriptions of both sides of the conversation, tool calls, token counts, and errors. A single spoken reply can arrive as dozens of events, and handling them correctly is what makes a voice interface feel immediate rather than laggy.

`Event` is the same class ADK uses everywhere, documented in [Events](https://adk.dev/events/index.md). A live session fills in fields a request/response agent never touches — audio blobs, transcriptions, interruption flags — and delivers them continuously instead of once. For the loop that yields them, see [Sessions](https://adk.dev/live/sessions/index.md).

## Live agent event data

An [`Event`](https://adk.dev/api-reference/python/google-adk.html#google.adk.events.Event) is a Pydantic model that extends `LlmResponse`. Live sessions use these fields:

| Field                                                 | What it holds                                                                  |
| ----------------------------------------------------- | ------------------------------------------------------------------------------ |
| `content.parts[].text`                                | Text parts — in a live session, thought summaries and other non-spoken content |
| `content.parts[].inline_data`                         | Raw audio bytes for playback (ephemeral)                                       |
| `content.parts[].file_data`                           | Reference to audio saved in artifacts (when `save_live_blob=True`)             |
| `content.parts[].function_call` / `function_response` | Tool invocations and results (ADK executes these for you)                      |
| `input_transcription` / `output_transcription`        | User and model speech as text                                                  |
| `partial`                                             | `True` for an incremental chunk, `False` for the merged result                 |
| `turn_complete`                                       | `True` when the model has finished its whole response                          |
| `interrupted`                                         | `True` when the user barged in mid-response                                    |
| `usage_metadata`                                      | Token counts for cost and quota tracking                                       |
| `error_code` / `error_message`                        | Failure diagnostics                                                            |
| `author`                                              | Who produced the event (see below)                                             |

### Authorship

In a live session, `event.author` is `"user"` for transcribed user speech and the **agent's name** (not the literal `"model"`) for the model's own output. ADK sets `author="user"` whenever the response carries an `input_transcription` or `content.role == 'user'`; checking the transcription is what makes attribution reliable, since an input-transcription response does not always carry `role == 'user'` ([`base_llm_flow.py`](https://github.com/google/adk-python/blob/main/src/google/adk/flows/llm_flows/base_llm_flow.py)).

Using the agent name lets you filter by author in multi-agent sessions:

```python
events = [e for e in stream if e.author == "billing_agent"]
```

## Event types

During a live session, an agent delivers its continuous output through several distinct event types, which can include partial text, audio, speech transcriptions, tool calls, and token usage metadata. The following sections describe these event types.

During a live session, an agent delivers its continuous output through several distinct event types, which can include partial text, audio, speech transcriptions, tool calls, and token usage metadata. The following sections describe these event types.

### Text

Text arrives on `event.content.parts[].text`. In a live session this is thought summaries and other non-spoken content — **the model's spoken reply comes back as an [output transcription](https://adk.dev/live/configuration/#audio-transcription), not a text part**, because every [Live model](https://adk.dev/live/models/#live-models) ADK supports takes audio in and produces audio out.

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.text and not event.partial:
                update_display(part.text)
```

Iterate over `parts`, never assume `parts[0]`

A single event can carry several parts, and Live models do this routinely. `event.content.parts[0].text` silently drops the rest and breaks when the first part is not text (a thought summary, a function call, an audio blob). Loop over the parts and branch on which field is set.

### Audio

With `response_modalities=["AUDIO"]` (the live default), the model returns audio as `inline_data`:

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.inline_data:  # raw PCM bytes
                await play_audio(part.inline_data.data)
```

`inline_data` is ephemeral and never persisted. Set [`save_live_blob=True`](https://adk.dev/live/configuration/#save_live_blob) and ADK aggregates audio into files in the artifact service, delivering a `file_data` reference instead of (not in addition to) raw bytes so you can retrieve the audio later. For formats and playback, see [Audio and video](https://adk.dev/live/audio-video/index.md).

### Transcription

When transcription is enabled (on by default), user and model speech arrive on `event.input_transcription` and `event.output_transcription`. They stream in fragments: `.text` holds the latest fragment and `.finished` marks the last for the turn, mirrored by `event.partial`. Concatenate the fragments to build the full transcript. See [Audio transcription](https://adk.dev/live/configuration/#audio-transcription).

```python
async for event in runner.run_live(...):
    if event.input_transcription and event.input_transcription.text:
        show_caption(event.input_transcription.text, is_user=True)
    if event.output_transcription and event.output_transcription.text:
        show_caption(event.output_transcription.text, is_user=False)
```

### Tool calls

The model requests a tool through `part.function_call`. ADK executes registered tools automatically, so you rarely handle these directly. See [Automatic tool execution](https://adk.dev/live/tools/#automatic-tool-execution).

### Metadata

`event.usage_metadata` carries token counts (`prompt_token_count`, `candidates_token_count`, `total_token_count`, `cached_content_token_count`) for real-time cost and quota tracking.

## Streaming flags

Three flags drive a live UI: `partial`, `turn_complete`, and `interrupted`. The `partial` flag distinguishes an incremental chunk from the merged result:

- `partial=True`: only the new text since the last event.
- `partial=False`: the full merged text for this segment.

ADK accumulates the chunks for you (`StreamingResponseAggregator`), so a `partial=False` event already holds the sum of the preceding `partial=True` chunks. If you do not need a live typing effect, ignore the partials and act only on `partial=False`.

```text
Event 1: partial=True,  text="Hello",       turn_complete=False
Event 2: partial=True,  text=" world",      turn_complete=False
Event 3: partial=False, text="Hello world", turn_complete=False
Event 4: partial=False, text="",            turn_complete=True
```

A `partial=False` condition can occur several times per turn (once per sentence, for example), and `turn_complete=True` arrives once, in its own event, after the last segment.

`turn_complete` and `interrupted` tell your UI what state to enter:

| turn_complete | interrupted | Your app should                         |
| ------------- | ----------- | --------------------------------------- |
| True          | False       | Enable input, show "ready"              |
| False         | True        | Stop playback, clear partial content    |
| True          | True        | Turn is done; same as normal completion |
| False         | False       | Keep displaying streaming text          |

```python
async for event in runner.run_live(...):
    if event.interrupted:
        stop_audio_playback()   # user barged in; drop queued audio
        clear_streaming_text()
    if event.turn_complete:
        enable_microphone()     # ready for the next turn
```

Without handling `interrupted`, already-buffered audio keeps playing over the user.

## Handling errors

Errors surface on `event.error_code` and `event.error_message`. The one decision to make is whether the model's response can continue: `break` when the model has stopped, `continue` when the failure is transient.

```python
try:
    async for event in runner.run_live(...):
        if event.error_code:
            logger.error("Model error: %s - %s", event.error_code, event.error_message)
            if event.error_code in ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "MAX_TOKENS"):
                break       # Model terminated; no more events this turn.
            continue        # Transient; the stream may recover.
        # ... handle content ...
finally:
    live_request_queue.close()  # Runs whether you break or finish.
```

| Error code                                  | Category       | Action                                            |
| ------------------------------------------- | -------------- | ------------------------------------------------- |
| `SAFETY`, `PROHIBITED_CONTENT`, `BLOCKLIST` | Content policy | `break` — model terminated the response           |
| `MAX_TOKENS`                                | Limit          | `break` — model finished generating               |
| `UNAVAILABLE`, `DEADLINE_EXCEEDED`          | Transient      | `continue` — network or timeout, may self-resolve |
| `RESOURCE_EXHAUSTED`                        | Rate limit     | `continue` with exponential backoff               |
| `CANCELLED`                                 | Client         | `break` — clean up                                |
| `UNKNOWN`                                   | System         | `continue` with logging                           |

For transient errors under a second, do not notify the user. For `RESOURCE_EXHAUSTED`, back off and cap retries so you do not loop forever. Error codes come from the Gemini API; see [FinishReason](https://ai.google.dev/api/python/google/ai/generativelanguage/Candidate/FinishReason) and the [Agent Platform reference](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/inference).

## Sending events to a client

To stream events to a browser or mobile client, serialize them and send over your transport. `Event` is a Pydantic model, so `model_dump_json()` does the work; base64-encoded audio inflates JSON by ~33%, so send audio as binary frames. Both the serialization patterns and the matching client-side handling live in [Custom server](https://adk.dev/live/custom-server/#serializing-events).
