# Audio and video for live agents

Supported in ADKPython v0.1.0

Audio and video are what make a live agent feel live, and they are where the exact formats matter. The Live API expects specific PCM sample rates for audio, and images and video frames go through a different send method than text.

**ADK does not convert media for you.** Getting the sample rate, encoding, and MIME type right is your responsibility, and the wrong format produces silence, noise, or a connection error rather than a helpful message. What follows is that contract.

For the models that support these modalities, see [Supported models](https://adk.dev/live/models/index.md). For voices, transcription, and turn detection, see [Configuration](https://adk.dev/live/configuration/index.md). For a client that already implements all of this, run your agent in `adk web`; to write your own, see [Build a custom server](https://adk.dev/live/custom-server/#connect-a-client).

## Audio input

Send microphone audio as raw bytes through [`send_realtime()`](https://adk.dev/live/sessions/#liverequestqueue). The bytes must already be in the format the Live API expects — ADK passes them straight through:

| Property    | Value                             |
| ----------- | --------------------------------- |
| Encoding    | 16-bit PCM, signed, little-endian |
| Sample rate | 16,000 Hz (16 kHz)                |
| Channels    | Mono                              |
| MIME type   | `audio/pcm;rate=16000`            |

```python
from google.genai import types

live_request_queue.send_realtime(
    types.Blob(mime_type="audio/pcm;rate=16000", data=audio_data)
)
```

Stream audio in small chunks for low latency. `LiveRequestQueue` forwards each chunk promptly without coalescing, so the chunk size you send is the granularity the model receives:

- **Ultra-low latency** (real-time conversation): 10-20 ms per chunk.
- **Balanced** (recommended): 50-100 ms per chunk. At 16 kHz, 100 ms is `16000 × 0.1 × 2 = 3200` bytes.
- **Lower overhead**: 100-200 ms per chunk.

Use a consistent chunk size for the session, and do not wait for a model response before sending the next chunk — the model processes audio continuously, not turn by turn. With [voice activity detection](https://adk.dev/live/configuration/#voice-activity-detection-vad) on (the default), stream continuously and let the API detect speech; send [activity signals](https://adk.dev/live/sessions/#liverequestqueue) only when you disable VAD.

## Audio output

With `response_modalities=["AUDIO"]` (the live default), the model returns audio as `inline_data` parts on the event stream:

| Property    | Value                                                             |
| ----------- | ----------------------------------------------------------------- |
| Encoding    | 16-bit PCM, signed, little-endian                                 |
| Sample rate | 24,000 Hz (24 kHz) — note this differs from the 16 kHz input rate |
| Channels    | Mono                                                              |
| MIME type   | `audio/pcm;rate=24000`                                            |

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                await play_audio(part.inline_data.data)  # raw 24 kHz PCM bytes
```

The bytes arrive ready to play; no decoding is needed on your side. The Live API transmits audio as base64 over the wire, but `google.genai` decodes it for you, so `part.inline_data.data` is already `bytes`. For which events carry audio and how they interleave with transcription, see [Events](https://adk.dev/live/events/#audio). To persist audio to the artifact service, set [`save_live_blob=True`](https://adk.dev/live/configuration/#save_live_blob).

## Images and video

Images and video are sent as individual JPEG frames through the same [`send_realtime()`](https://adk.dev/live/sessions/#liverequestqueue) method as audio. There is no video codec: a video stream is a sequence of still frames, each sent as its own blob.

| Property   | Value                                     |
| ---------- | ----------------------------------------- |
| Format     | JPEG (`image/jpeg`)                       |
| Frame rate | ~1 frame per second (recommended maximum) |
| Resolution | 768×768 pixels (recommended)              |

```python
from google.genai import types

live_request_queue.send_realtime(
    types.Blob(mime_type="image/jpeg", data=jpeg_bytes)
)
```

At ~1 FPS the model can see what the user is pointing a camera at or discussing, but not anything motion-dependent. Action recognition, sports analysis, and motion tracking need temporal resolution this approach does not provide.

In the [Shopper's Concierge demo](https://youtu.be/LwHPYyw7u6U?si=lG9gl9aSIuu-F4ME&t=40), the app sends a user-uploaded image with `send_realtime()`; the agent recognizes the context and searches an e-commerce catalog for matching items.

To feed a live video stream into a tool so the agent can react to frames as they arrive, see [Streaming tools](https://adk.dev/live/tools/#streaming-tools).
