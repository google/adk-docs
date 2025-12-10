1: # Part 3: Event handling with run_live()
2: 
3: The `run_live()` method is ADK's primary entry point for streaming conversations, implementing an async generator that yields events as the conversation unfolds. This part focuses on understanding and handling these events—the core communication mechanism that enables real-time interaction between your application, users, and AI models.
4: 
5: You'll learn how to process different event types (text, audio, transcriptions, tool calls), manage conversation flow with interruption and turn completion signals, serialize events for network transport, and leverage ADK's automatic tool execution. Understanding event handling is essential for building responsive streaming applications that feel natural and real-time to users.
6: 
7: !!! note "Async Context Required"
8: 
9:     All `run_live()` code requires async context. See [Part 1: FastAPI Application Example](part1.md#fastapi-application-example) for details and production examples.
10:     
11: ## How run_live() Works
12: 
13: `run_live()` is an async generator that streams conversation events in real-time. It yields events immediately as they're generated—no buffering, no polling, no callbacks. Events are streamed without internal buffering. Overall memory depends on session persistence (e.g., in-memory vs database), making it suitable for both quick exchanges and extended sessions.
14: 
15: ### Method Signature and Flow
16: 
17: **Usage:**
18: 
19: ```python title='Source reference: <a href="https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/runners.py" target="_blank">runners.py</a>'
20: # The method signature reveals the thoughtful design
21: async def run_live(
22:     self,
23:     *,                                      # Keyword-only arguments
24:     user_id: Optional[str] = None,          # User identification (required unless session provided)
25:     session_id: Optional[str] = None,       # Session tracking (required unless session provided)
26:     live_request_queue: LiveRequestQueue,   # The bidirectional communication channel
27:     run_config: Optional[RunConfig] = None, # Streaming behavior configuration
28:     session: Optional[Session] = None,      # Deprecated: use user_id and session_id instead
29: ) -> AsyncGenerator[Event, None]:           # Generator yielding conversation events
30: ```
31: 
32: As its signature tells, every streaming conversation needs identity (user_id), continuity (session_id), communication (live_request_queue), and configuration (run_config). The return type—an async generator of Events—promises real-time delivery without overwhelming system resources.
33:     
34: ```mermaid
35: sequenceDiagram
36: participant Client
37: participant Runner
38: participant Agent
39: participant LLMFlow
40: participant Gemini
41: 
42: Client->>Runner: runner.run_live(user_id, session_id, queue, config)
43: Runner->>Agent: agent.run_live(context)
44: Agent->>LLMFlow: _llm_flow.run_live(context)
45: LLMFlow->>Gemini: Connect and stream
46: 
47: loop Continuous Streaming
48:     Gemini-->>LLMFlow: LlmResponse
49:     LLMFlow-->>Agent: Event
50:     Agent-->>Runner: Event
51:     Runner-->>Client: Event (yield)
52: end
53: ```
54:     
55: ### Basic Usage Pattern
56: 
57: The simplest way to consume events from `run_live()` is to iterate over the async generator with a for-loop:
58: 
59: ```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/4274c70ae3f4c68595f543ee504474747ea9f0da/python/agents/bidi-demo/app/main.py#L197-L205" target="_blank">main.py:197-205</a>'
60: async for event in runner.run_live(
61:     user_id=user_id,
62:     session_id=session_id,
63:     live_request_queue=live_request_queue,
64:     run_config=run_config
65: ):
66:     event_json = event.model_dump_json(exclude_none=True, by_alias=True)
67:     logger.debug(f"[SERVER] Event: {event_json}")
68:     await websocket.send_text(event_json)
69: ```
70: 
71: !!! note "Session Identifiers"
72: 
73:     Both `user_id` and `session_id` must match the identifiers you used when creating the session via `SessionService.create_session()`. These can be any string values based on your application's needs (e.g., UUIDs, email addresses, custom tokens). See [Part 1: Get or Create Session](part1.md#get-or-create-session) for detailed guidance on session identifiers.
74: 
75: ### Connection Lifecycle in run_live()
76: 
77: The `run_live()` method manages the underlying Live API connection lifecycle automatically:
78: 
79: **Connection States:**
80: 1. **Initialization**: Connection established when `run_live()` is called
81: 2. **Active Streaming**: Bidirectional communication via `LiveRequestQueue` (upstream to the model) and `run_live()` (downstream from the model)
82: 3. **Graceful Closure**: Connection closes when `LiveRequestQueue.close()` is called
83: 4. **Error Recovery**: ADK supports transparent session resumption; enable via `RunConfig.session_resumption` to handle transient failures. See [Part 4: Live API Session Resumption](part4.md#live-api-session-resumption) for details.
84: 
85: #### What run_live() Yields
86: 
87: The `run_live()` method yields a stream of `Event` objects in real-time as the agent processes user input and generates responses. Understanding the different event types helps you build responsive UIs that handle text, audio, transcriptions, tool calls, metadata, and errors appropriately. Each event type is explained in detail in the sections below.
88: 
89: | Event Type | Description |
90: |------------|-------------|
91: | **[Text Events](#text-events)** | Model's text responses when using `response_modalities=["TEXT"]`; includes `partial`, `turn_complete`, and `interrupted` flags for streaming UI management |
92: | **[Audio Events with Inline Data](#audio-events)** | Raw audio bytes (`inline_data`) streamed in real-time when using `response_modalities=["AUDIO"]`; ephemeral (not persisted to session) |
93: | **[Audio Events with File Data](#audio-events-with-file-data)** | Audio aggregated into files and stored in artifacts; contains `file_data` references instead of raw bytes; can be persisted to session history |
94: | **[Metadata Events](#metadata-events)** | Token usage information (`prompt_token_count`, `candidates_token_count`, `total_token_count`) for cost monitoring and quota tracking |
95: | **[Transcription Events](#transcription-events)** | Speech-to-text for user input (`input_transcription`) and model output (`output_transcription`) when transcription is enabled in `RunConfig` |
96: | **[Tool Call Events](#tool-call-events)** | Function call requests from the model; ADK handles execution automatically |
97: | **[Error Events](#error-events)** | Model errors and connection issues with `error_code` and `error_message` fields |
98: 
99: !!! note "Source Reference"
100: 
101:     See the complete event type handling implementation in [`runners.py`](https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/runners.py)
102: 
103: #### When run_live() Exits
104: 
105: The `run_live()` event loop can exit under various conditions. Understanding these exit scenarios is crucial for proper resource cleanup and error handling:
106: 
107: | Exit Condition | Trigger | Graceful? | Description |
108: |---|---|---|---|
109: | **Manual close** | `live_request_queue.close()` | ✅ Yes | User explicitly closes the queue, sending `LiveRequest(close=True)` signal |
110: | **All agents complete** | Last agent in SequentialAgent calls `task_completed()` | ✅ Yes | After all sequential agents finish their tasks |
111: | **Session timeout** | Live API duration limit reached | ⚠️ Connection closed | Session exceeds maximum duration (see limits below) |
112: | **Early exit** | `end_invocation` flag set | ✅ Yes | Set during preprocessing or by tools/callbacks to terminate early |
113: | **Empty event** | Queue closure signal | ✅ Yes | Internal signal indicating event stream has ended |
114: | **Errors** | Connection errors, exceptions | ❌ No | Unhandled exceptions or connection failures |
115: 
116: !!! warning "SequentialAgent Behavior"
117: 
118:     When using `SequentialAgent`, the `task_completed()` function does NOT exit your application's `run_live()` loop. It only signals the end of the current agent's work, triggering a seamless transition to the next agent in the sequence. Your event loop continues receiving events from subsequent agents. The loop only exits when the **last** agent in the sequence completes.
119: 
120: !!! note "Learn More"
121: 
122:     For session resumption and connection recovery details, see [Part 4: Live API Session Resumption](part4.md#live-api-session-resumption). For multi-agent workflows, see [Best Practices for Multi-Agent Workflows](#best-practices-for-multi-agent-workflows).
123: 
124: #### Events Saved to ADK `Session`
125: 
126: Not all events yielded by `run_live()` are persisted to the ADK `Session`. When `run_live()` exits, only certain events are saved to the session while others remain ephemeral. Understanding which events are saved versus which are ephemeral is crucial for applications that use session persistence, resumption, or need to review conversation history.
127: 
128: !!! note "Source Reference"
129: 
130:     See session event persistence logic in [`runners.py`](https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/runners.py)
131: 
132: **Events Saved to the ADK `Session`:**
133: 
134: These events are persisted to the ADK `Session` and available in session history:
135: 
136: - **Audio Events with File Data**: Saved to ADK `Session` only if `RunConfig.save_live_blob` is `True`; audio data is aggregated into files in artifacts with `file_data` references
137: - **Usage Metadata Events**: Always saved to track token consumption across the ADK `Session`
138: - **Non-Partial Transcription Events**: Final transcriptions are saved; partial transcriptions are not persisted
139: - **Function Call and Response Events**: Always saved to maintain tool execution history
140: - **Other Control Events**: Most control events (e.g., `turn_complete`, `finish_reason`) are saved
141: 
142: **Events NOT Saved to the ADK `Session`:**
143: 
144: These events are ephemeral and only yielded to callers during active streaming:
145: 
146: - **Audio Events with Inline Data**: Raw audio `Blob` data in `inline_data` is never saved to the ADK `Session` (only yielded for real-time playback)
147: - **Partial Transcription Events**: Only yielded for real-time display; final transcriptions are saved
148: 
149: !!! note "Audio Persistence"
150: 
151:     To save audio conversations to the ADK `Session` for review or resumption, enable `RunConfig.save_live_blob = True`. This persists audio streams to artifacts. See [Part 4: save_live_blob](part4.md#save_live_blob) for configuration details.
152: 
153: ## Understanding Events
154: 
155: Events are the core communication mechanism in ADK's Bidi-streaming system. This section explores the complete lifecycle of events—from how they're generated through multiple pipeline layers, to concurrent processing patterns that enable true real-time interaction, to practical handling of interruptions and turn completion. You'll learn about event types (text, audio, transcriptions, tool calls), serialization strategies for network transport, and the connection lifecycle that manages streaming sessions across both Gemini Live API and Vertex AI Live API platforms.
156: 
157: ### The Event Class
158: 
159: ADK's `Event` class is a Pydantic model that represents all communication in a streaming conversation. It extends `LlmResponse` and serves as the unified container for model responses, user input, transcriptions, and control signals.
160: 
161: !!! note "Source Reference"
162: 
163:     See Event class implementation in [`event.py:30-128`](https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/events/event.py#L30-L128) and [`llm_response.py:28-193`](https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/models/llm_response.py#L28-L193)
164: 
165: #### Key Fields
166: 
167: **Essential for all applications:**
168: - `content`: Contains text, audio, or function calls as `Content.parts`
169: - `author`: Identifies who created the event (`"user"` or agent name)
170: - `partial`: Distinguishes incremental chunks from complete text
171: - `turn_complete`: Signals when to enable user input again
172: - `interrupted`: Indicates when to stop rendering current output
173: 
174: **For voice/audio applications:**
175: - `input_transcription`: User's spoken words (when enabled in `RunConfig`)
176: - `output_transcription`: Model's spoken words (when enabled in `RunConfig`)
177: - `content.parts[].inline_data`: Audio data for playback
178: 
179: **For tool execution:**
180: - `content.parts[].function_call`: Model's tool invocation requests
181: - `content.parts[].function_response`: Tool execution results
182: - `long_running_tool_ids`: Track async tool execution
183: 
184: **For debugging and diagnostics:**
185: - `usage_metadata`: Token counts and billing information
186: - `cache_metadata`: Context cache hit/miss statistics
187: - `finish_reason`: Why the model stopped generating (e.g., STOP, MAX_TOKENS, SAFETY)
188: - `error_code` / `error_message`: Failure diagnostics
189: 
190: !!! note "Author Semantics"
191: 
192:     Transcription events have author `"user"`; model responses/events use the agent's name as `author` (not `"model"`). See [Event Authorship](#event-authorship) for details.
193: 
194: #### Understanding Event Identity
195: 
196: Events have two important ID fields:
197: 
198: - **`event.id`**: Unique identifier for this specific event (format: UUID). Each event gets a new ID, even partial text chunks.
199: - **`event.invocation_id`**: Shared identifier for all events in the current invocation (format: `"e-" + UUID`). In `run_live()`, all events from a single streaming session share the same invocation_id. (See [InvocationContext](#invocationcontext-the-execution-state-container) for more about invocations)
200: 
201: **Usage:**
202: 
203: ```python
204: # All events in this streaming session will have the same invocation_id
205: async for event in runner.run_live(...):
206:     print(f"Event ID: {event.id}")              # Unique per event
207:     print(f"Invocation ID: {event.invocation_id}")  # Same for all events in session
208: ```
209: 
210: **Use cases:**
211: - **event.id**: Track individual events in logs, deduplicate events
212: - **event.invocation_id**: Group events by conversation session, filter session-specific events
213: 
214: ### Event Authorship
215: 
216: In live streaming mode, the `Event.author` field follows special semantics to maintain conversation clarity:
217: 
218: **Model responses**: Authored by the **agent name** (e.g., `"my_agent"`), not the literal string `"model"`
219: 
220: - This enables multi-agent scenarios where you need to track which agent generated the response
221: - Example: `Event(author="customer_service_agent", content=...)`
222: 
223: **User transcriptions**: Authored as `"user"` when the event contains transcribed user audio
224: 
225: **How it works**:
226: 
227: 1. Gemini Live API returns user audio transcriptions with `content.role == 'user'`
228: 2. ADK's `get_author_for_event()` function checks for this role marker
229: 3. If `content.role == 'user'`, ADK sets `Event.author` to `"user"`
230: 4. Otherwise, ADK sets `Event.author` to the agent name (e.g., `"my_agent"`)
231: 
232: This transformation ensures that transcribed user input is correctly attributed to the user in your application's conversation history, even though it flows through the model's response stream.
233: 
234: - Example: Input audio transcription → `Event(author="user", input_transcription=..., content.role="user")`
235: 
236: **Why this matters**:
237: 
238: - In multi-agent applications, you can filter events by agent: `events = [e for e in stream if e.author == "my_agent"]`
239: - When displaying conversation history, use `event.author` to show who said what
240: - Transcription events are correctly attributed to the user even though they flow through the model
241: 
242: !!! note "Source Reference"
243: 
244:     See author attribution logic in [`base_llm_flow.py:292-326`](https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/flows/llm_flows/base_llm_flow.py#L292-L326)
245: 
246: ### Event Types and Handling
247: 
248: ADK streams distinct event types through `runner.run_live()` to support different interaction modalities: text responses for traditional chat, audio chunks for voice output, transcriptions for accessibility and logging, and tool call notifications for function execution. Each event includes metadata flags (`partial`, `turn_complete`, `interrupted`) that control UI state transitions and enable natural, human-like conversation flows. Understanding how to recognize and handle these event types is essential for building responsive streaming applications.
249: 
250: ### Text Events
251: 
252: The most common event type, containing the model's text responses when you specifying `response_modalities` in `RunConfig` to `["TEXT"]` mode:
253: 
254: **Usage:**
255: 
256: ```python
257: async for event in runner.run_live(...):
258:     if event.content and event.content.parts:
259:         if event.content.parts[0].text:
260:             text = event.content.parts[0].text
261: 
262:             if not event.partial:
263:                 # Your logic to update streaming display
264:                 update_streaming_display(text)
265: ```
266: 
267: #### Default Response Modality Behavior
268: 
269: When `response_modalities` is not explicitly set (i.e., `None`), ADK automatically defaults to `["AUDIO"]` mode at the start of `run_live()`. This means:
270: 
271: - **If you provide no RunConfig**: Defaults to `["AUDIO"]`
272: - **If you provide RunConfig without response_modalities**: Defaults to `["AUDIO"]`
273: - **If you explicitly set response_modalities**: Uses your setting (no default applied)
274: 
275: **Why this default exists**: Some native audio models require the response modality to be explicitly set. To ensure compatibility with all models, ADK defaults to `["AUDIO"]`.
276: 
277: **For text-only applications**: Always explicitly set `response_modalities=["TEXT"]` in your RunConfig to avoid receiving unexpected audio events.
278: 
279: **Example:**
280: 
281: ```python
282: # Explicit text mode
283: run_config = RunConfig(
284:     response_modalities=["TEXT"],
285:     streaming_mode=StreamingMode.BIDI
286: )
287: ```
288: 
289: **Key Event Flags:**
290: 
291: These flags help you manage streaming text display and conversation flow in your UI:
292: 
293: - `event.partial`: `True` for incremental text chunks during streaming; `False` for complete merged text
294: - `event.turn_complete`: `True` when the model has finished its complete response
295: - `event.interrupted`: `True` when user interrupted the model's response
296: 
297: !!! note "Learn More"
298: 
299:     For detailed guidance on using `partial` `turn_complete` and `interrupted` flags to manage conversation flow and UI state, see [Handling Text Events](#handling-text-events).
300: 
301: ### Audio Events
302: 
303: When `response_modalities` is configured to `["AUDIO"]` in your `RunConfig`, the model generates audio output instead of text, and you'll receive audio data in the event stream:
304: 
305: **Configuration:**
306: 
307: ```python
308: # Configure RunConfig for audio responses
309: run_config = RunConfig(
310:     response_modalities=["AUDIO"],
311:     streaming_mode=StreamingMode.BIDI
312: )
313: 
314: # Audio arrives as inline_data in event.content.parts
315: async for event in runner.run_live(..., run_config=run_config):
316:     if event.content and event.content.parts:
317:         part = event.content.parts[0]
318:         if part.inline_data:
319:             # Audio event structure:
320:             # part.inline_data.data: bytes (raw PCM audio)
321:             # part.inline_data.mime_type: str (e.g., "audio/pcm")
322:             audio_data = part.inline_data.data
323:             mime_type = part.inline_data.mime_type
324: 
325:             print(f"Received {len(audio_data)} bytes of {mime_type}")
326:             # Your logic to play audio
327:             await play_audio(audio_data)
328: ```
329: 
330: !!! note "Learn More"
331: 
332:     - **`response_modalities` controls how the model generates output**—you must choose either `["TEXT"]` for text responses or `["AUDIO"]` for audio responses per session. You cannot use both modalities simultaneously. See [Part 4: Response Modalities](part4.md#response-modalities) for configuration details.
333:     - For comprehensive coverage of audio formats, sending/receiving audio, and audio processing flow, see [Part 5: How to Use Audio, Image and Video](part5.md).
334: 
335: ### Audio Events with File Data
336: 
337: When audio data is aggregated and saved as files in artifacts, ADK yields events containing `file_data` references instead of raw `inline_data`. This is useful for persisting audio to session history.
338: 
339: !!! note "Source Reference"
340: 
341:     See audio file aggregation logic in [`audio_cache_manager.py:157-177`](https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/flows/llm_flows/audio_cache_manager.py#L157-L177)
342: 
343: **Receiving Audio File References:**
344: 
345: ```python
346: async for event in runner.run_live(
347:     user_id=user_id,
348:     session_id=session_id,
349:     live_request_queue=queue,
350:     run_config=run_config
351: ):
352:     if event.content and event.content.parts:
353:         for part in event.content.parts:
354:             if part.file_data:
355:                 # Audio aggregated into a file saved in artifacts
356:                 file_uri = part.file_data.file_uri
357:                 mime_type = part.file_data.mime_type
358: 
359:                 print(f"Audio file saved: {file_uri} ({mime_type})")
360:                 # Retrieve audio file from artifact service for playback
361: ```
362: 
363: **File Data vs Inline Data:**
364: 
365: - **Inline Data** (`part.inline_data`): Raw audio bytes streamed in real-time; ephemeral and not saved to session
366: - **File Data** (`part.file_data`): Reference to audio file stored in artifacts; can be persisted to session history
367: 
368: Both input and output audio data are aggregated into audio files and saved in the artifact service. The file reference is included in the event as `file_data`, allowing you to retrieve the audio later.
369: 
370: !!! note "Session Persistence"
371: 
372:     To save audio events with file data to session history, enable `RunConfig.save_live_blob = True`. This allows audio conversations to be reviewed or replayed from persisted sessions.
373: 
374: ### Metadata Events
375: 
376: Usage metadata events contain token usage information for monitoring costs and quota consumption. The `run_live()` method yields these events separately from content events.
377: 
378: !!! note "Source Reference"
379: 
380:     See usage metadata structure in [`llm_response.py:105`](https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/models/llm_response.py#L105)
381: 
382: **Accessing Token Usage:**
383: 
384: ```python
385: async for event in runner.run_live(
386:     user_id=user_id,
387:     session_id=session_id,
388:     live_request_queue=queue,
389:     run_config=run_config
390: ):
391:     if event.usage_metadata:
392:         print(f"Prompt tokens: {event.usage_metadata.prompt_token_count}")
393:         print(f"Response tokens: {event.usage_metadata.candidates_token_count}")
394:         print(f"Total tokens: {event.usage_metadata.total_token_count}")
395: 
396:         # Track cumulative usage across the session
397:         total_tokens += event.usage_metadata.total_token_count or 0
398: ```
399: 
400: **Available Metadata Fields:**
401: 
402: - `prompt_token_count`: Number of tokens in the input (prompt and context)
403: - `candidates_token_count`: Number of tokens in the model's response
404: - `total_token_count`: Sum of prompt and response tokens
405: - `cached_content_token_count`: Number of tokens served from cache (when using context caching)
406: 
407: !!! note "Cost Monitoring"
408: 
409:     Usage metadata events allow real-time cost tracking during streaming sessions. You can implement quota limits, display usage to users, or log metrics for billing and analytics.
410: 
411: ### Transcription Events
412: 
413: When transcription is enabled in `RunConfig`, you receive transcriptions as separate events:
414: 
415: **Configuration:**
416: 
417: ```python
418: async for event in runner.run_live(...):
419:     # User's spoken words (when input_audio_transcription enabled)
420:     if event.input_transcription:
421:         # Your logic to display user transcription
422:         display_user_transcription(event.input_transcription)
423: 
424:     # Model's spoken words (when output_audio_transcription enabled)
425:     if event.output_transcription:
426:         # Your logic to display model transcription
427:         display_model_transcription(event.output_transcription)
428: ```
429: 
430: These enable accessibility features and conversation logging without separate transcription services.
431: 
432: !!! note "Learn More"
433: 
434:     For details on enabling transcription in `RunConfig` and understanding transcription delivery, see [Part 5: Audio Transcription](part5.md#audio-transcription).
435: 
436: ### Tool Call Events
437: 
438: When the model requests tool execution:
439: 
440: **Usage:**
441: 
442: ```python
443: async for event in runner.run_live(...):
444:     if event.content and event.content.parts:
445:         for part in event.content.parts:
446:             if part.function_call:
447:                 # Model is requesting a tool execution
448:                 tool_name = part.function_call.name
449:                 tool_args = part.function_call.args
450:                 # ADK handles execution automatically
451: ```
452: 
453: ADK processes tool calls automatically—you typically don't need to handle these directly unless implementing custom tool execution logic.
454: 
455: !!! note "Learn More"
456: 
457:     For details on how ADK automatically executes tools, handles function responses, and supports long-running and streaming tools, see [Automatic Tool Execution in run_live()](#automatic-tool-execution-in-run_live).
458: 
459: ### Streaming Function Call Arguments
460: 
461: ADK now supports streaming for function call arguments, allowing for a more responsive user experience when working with tools that have arguments that are generated over time.
462: 
463: When the model streams function call arguments, you will receive multiple `Event` objects for a single tool call. Each event will contain a `function_call` part with `partial_args`. The `partial_args` will contain a piece of an argument. The ADK will aggregate these partial arguments and will yield a final `Event` with the complete `function_call` once all partial arguments have been received.
464: 
465: **Example of streaming function call arguments:**
466: 
467: ```python
468: async for event in runner.run_live(...):
469:     if event.content and event.content.parts:
470:         for part in event.content.parts:
471:             if part.function_call:
472:                 # This could be a partial or a complete function call
473:                 if hasattr(part.function_call, 'partial_args') and part.function_call.partial_args:
474:                     # This is a streaming function call with partial arguments.
475:                     # ADK will handle the aggregation of these arguments.
476:                     # You can inspect the partial arguments here if needed.
477:                     logger.info(f"Streaming function call: {part.function_call.name} with partial args: {part.function_call.partial_args}")
478:                 else:
479:                     # This is a complete function call.
480:                     # ADK has already aggregated all the partial arguments.
481:                     tool_name = part.function_call.name
482:                     tool_args = part.function_call.args
483:                     logger.info(f"Complete function call: {tool_name} with args: {tool_args}")
484: 
485: ```
486: 
487: In this example, you check if the `function_call` has `partial_args`. If it does, it means that the arguments are being streamed. The ADK automatically handles the aggregation of these partial arguments. When all the arguments have been received, the ADK will yield a final event with the complete `function_call` and no `partial_args`.
488: 
489: This feature is particularly useful for tools that take a long time to generate their arguments, for example, a tool that summarizes a long document. The user can see the progress of the summarization as the arguments are being streamed.
490: 
491: ### Error Events
492: 
493: Production applications need robust error handling to gracefully handle model errors and connection issues. ADK surfaces errors through the `error_code` and `error_message` fields:
494: 
495: **Usage:**
496: 
497: ```python
498: import logging
499: 
500: logger = logging.getLogger(__name__)
501: 
502: try:
503:     async for event in runner.run_live(...):
504:         # Handle errors from the model or connection
505:         if event.error_code:
506:             logger.error(f"Model error: {event.error_code} - {event.error_message}")
507: 
508:             # Send error notification to client
509:             await websocket.send_json({
510:                 "type": "error",
511:                 "code": event.error_code,
512:                 "message": event.error_message
513:             })
514: 
515:             # Decide whether to continue or break based on error severity
516:             if event.error_code in ["SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST"]:
517:                 # Content policy violations - usually cannot retry
518:                 break  # Terminal error - exit loop
519:             elif event.error_code == "MAX_TOKENS":
520:                 # Token limit reached - may need to adjust configuration
521:                 break
522:             # For other errors, you might continue or implement retry logic
523:             continue  # Transient error - keep processing
524: 
525:         # Normal event processing only if no error
526:         if event.content and event.content.parts:
527:             # ... handle content
528:             pass
529: finally:
530:     queue.close()  # Always cleanup connection
531: ```
532: 
533: !!! note
534: 
535:     The above example shows the basic structure for checking `error_code` and `error_message`. For production-ready error handling with user notifications, retry logic, and context logging, see the real-world scenarios below.
536: 
537: **When to use `break` vs `continue`:**
538: 
539: The key decision is: *Can the model's response continue meaningfully?*
540: 
541: **Scenario 1: Content Policy Violation (Use `break`)**
542: 
543: You're building a customer support chatbot. A user asks an inappropriate question that triggers a SAFETY filter:
544: 
545: **Example:**
546: 
547: ```python
548: if event.error_code in ["SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST"]:
549:     # Model has stopped generating - continuation is impossible
550:     await websocket.send_json({
551:         "type": "error",
552:         "message": "I can't help with that request. Please ask something else."
553:     })
554:     break  # Exit loop - model won't send more events for this turn
555: ```
556: 
557: **Why `break`?** The model has terminated its response. No more events will come for this turn. Continuing would just waste resources waiting for events that won't arrive.
558: 
559: ---
560: 
561: **Scenario 2: Network Hiccup During Streaming (Use `continue`)**
562: 
563: You're building a voice transcription service. Midway through transcribing, there's a brief network glitch:
564: 
565: **Example:**
566: 
567: ```python
568: if event.error_code == "UNAVAILABLE":
569:     # Temporary network issue
570:     logger.warning(f"Network hiccup: {event.error_message}")
571:     # Don't notify user for brief transient issues that may self-resolve
572:     continue  # Keep listening - model may recover and continue
573: ```
574: 
575: **Why `continue`?** This is a transient error. The connection might recover, and the model may continue streaming the transcription. Breaking would prematurely end a potentially recoverable stream.
576: 
577: !!! note "User Notifications"
578: 
579:     For brief transient errors (lasting <1 second), don't notify the user—they won't notice the hiccup. But if the error persists or impacts the user experience (e.g., streaming pauses for >3 seconds), notify them gracefully: "Experiencing connection issues, retrying..."
580: 
581: ---
582: 
583: **Scenario 3: Token Limit Reached (Use `break`)**
584: 
585: You're generating a long-form article and hit the maximum token limit:
586: 
587: **Example:**
588: 
589: ```python
590: if event.error_code == "MAX_TOKENS":
591:     # Model has reached output limit
592:     await websocket.send_json({
593:         "type": "complete",
594:         "message": "Response reached maximum length",
595:         "truncated": True
596:     })
597:     break  # Model has finished - no more tokens will be generated
598: ```
599: 
600: **Why `break`?** The model has reached its output limit and stopped. Continuing won't yield more tokens.
601: 
602: ---
603: 
604: **Scenario 4: Rate Limit with Retry Logic (Use `continue` with backoff)**
605: 
606: You're running a high-traffic application that occasionally hits rate limits:
607: 
608: **Example:**
609: 
610: ```python
611: retry_count = 0
612: max_retries = 3
613: 
614: async for event in runner.run_live(...):
615:     if event.error_code == "RESOURCE_EXHAUSTED":
616:         retry_count += 1
617:         if retry_count > max_retries:
618:             logger.error("Max retries exceeded")
619:             break  # Give up after multiple failures
620: 
621:         # Wait and retry
622:         await asyncio.sleep(2 ** retry_count)  # Exponential backoff
623:         continue  # Keep listening - rate limit may clear
624: 
625:     # Reset counter on successful event
626:     retry_count = 0
627: ```
628: 
629: **Why `continue` (initially)?** Rate limits are often temporary. With exponential backoff, the stream may recover. But after multiple failures, `break` to avoid infinite waiting.
630: 
631: ---
632: 
633: **Decision Framework:**
634: 
635: | Error Type | Action | Reason |
636: |------------|--------|--------|
637: | `SAFETY`, `PROHIBITED_CONTENT` | `break` | Model terminated response |
638: | `MAX_TOKENS` | `break` | Model finished generating |
639: | `UNAVAILABLE`, `DEADLINE_EXCEEDED` | `continue` | Transient network/timeout issue |
640: | `RESOURCE_EXHAUSTED` (rate limit) | `continue` with retry logic | May recover after brief wait |
641: | Unknown errors | `continue` (with logging) | Err on side of caution |
642: 
643: **Critical: Always use `finally` for cleanup**
644: 
645: **Usage:**
646: 
647: ```python
648: try:
649:     async for event in runner.run_live(...):
650:         # ... error handling ...
651: finally:
652:     queue.close()  # Cleanup runs whether you break or finish normally
653: ```
654: 
655: Whether you `break` or the loop finishes naturally, `finally` ensures the connection closes properly.
656: 
657: **Error Code Reference:**
658: 
659: ADK error codes come from the underlying Gemini API. Here are the most common error codes you'll encounter:
660: 
661: | Error Code | Category | Description | Recommended Action |
662: |------------|----------|-------------|-------------------|
663: | `SAFETY` | Content Policy | Content violates safety policies | `break` - Inform user, log incident |
664: | `PROHIBITED_CONTENT` | Content Policy | Content contains prohibited material | `break` - Show policy violation message |
665: | `BLOCKLIST` | Content Policy | Content matches blocklist | `break` - Alert user, don't retry |
666: | `MAX_TOKENS` | Limits | Output reached maximum token limit | `break` - Truncate gracefully, summarize |
667: | `RESOURCE_EXHAUSTED` | Rate Limiting | Quota or rate limit exceeded | `continue` with backoff - Retry after delay |
668: | `UNAVAILABLE` | Transient | Service temporarily unavailable | `continue` - Retry, may self-resolve |
669: | `DEADLINE_EXCEEDED` | Transient | Request timeout exceeded | `continue` - Consider retry with backoff |
670: | `CANCELLED` | Client | Client cancelled the request | `break` - Clean up resources |
671: | `UNKNOWN` | System | Unspecified error occurred | `continue` with logging - Log for analysis |
672: 
673: For complete error code listings and descriptions, refer to the official documentation:
674: 
675: !!! note "Official Documentation"
676: 
677:     - **FinishReason** (when model stops generating tokens): [Google AI for Developers](https://ai.google.dev/api/python/google/ai/generativelanguage/Candidate/FinishReason) | [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini)
678:     - **BlockedReason** (when prompts are blocked by content filters): [Google AI for Developers](https://ai.google.dev/api/python/google/ai/generativelanguage/GenerateContentResponse/PromptFeedback/BlockReason) | [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/configure-safety-attributes)
679:     - **ADK Implementation**: [`llm_response.py:156-193`](https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/models/llm_response.py#L156-L193)
680: 
681: **Best practices for error handling:**
682: 
683: - **Always check for errors first**: Process `error_code` before handling content to avoid processing invalid events
684: - **Log errors with context**: Include session_id and user_id in error logs for debugging
685: - **Categorize errors**: Distinguish between retryable errors (transient failures) and terminal errors (content policy violations)
686: - **Notify users gracefully**: Show user-friendly error messages instead of raw error codes
687: - **Implement retry logic**: For transient errors, consider automatic retry with exponential backoff
688: - **Monitor error rates**: Track error types and frequencies to identify systemic issues
689: - **Handle content policy errors**: For `SAFETY`, `PROHIBITED_CONTENT`, and `BLOCKLIST` errors, inform users that their content violates policies
690: 
691: ## Handling Text Events
692: 
693: Understanding the `partial`, `interrupted`, and `turn_complete` flags is essential for building responsive streaming UIs. These flags enable you to provide real-time feedback during streaming, handle user interruptions gracefully, and detect conversation boundaries for proper state management.
694: 
695: ### Handling `partial`
696: 
697: This flag helps you distinguish between incremental text chunks and complete merged text, enabling smooth streaming displays with proper final confirmation.
698: 
699: **Usage:**
700: 
701: ```python
702: async for event in runner.run_live(...):
703:     if event.content and event.content.parts:
704:         if event.content.parts[0].text:
705:             text = event.content.parts[0].text
706: 
707:             if event.partial:
708:                 # Your streaming UI update logic here
709:                 update_streaming_display(text)
710:             else:
711:                 # Your complete message display logic here
712:                 display_complete_message(text)
713: ```
714: 
715: **`partial` Flag Semantics:**
716: 
717: - `partial=True`: The text in this event is **incremental**—it contains ONLY the new text since the last event
718: - `partial=False`: The text in this event is **complete**—it contains the full merged text for this response segment
719: 
720: !!! note
721: 
722:     The `partial` flag is only meaningful for text content (`event.content.parts[].text`). For other content types:
723: 
724:     - **Audio events**: Each audio chunk in `inline_data` is independent (no merging occurs)
725:     - **Tool calls**: Function calls and responses are always complete (partial doesn't apply)
726:     - **Transcriptions**: Transcription events are always complete when yielded
727: 
728: **Example Stream:**
729: 
730: ```text
731: Event 1: partial=True,  text="Hello",        turn_complete=False
732: Event 2: partial=True,  text=" world",       turn_complete=False
733: Event 3: partial=False, text="Hello world",  turn_complete=False
734: Event 4: partial=False, text="",             turn_complete=True  # Turn done
735: ```
736: 
737: **Important timing relationships**:
738: - `partial=False` can occur **multiple times** in a turn (e.g., after each sentence)
739: - `turn_complete=True` occurs **once** at the very end of the model's complete response, in a **separate event**
740: - You may receive: `partial=False` (sentence 1) → `partial=False` (sentence 2) → `turn_complete=True`
741: - The merged text event (`partial=False` with content) is always yielded **before** the `turn_complete=True` event
742: 
743: !!! note
744: 
745:     ADK internally accumulates all text from `partial=True` events. When you receive an event with `partial=False`, the text content equals the sum of all preceding `partial=True` chunks. This means:
746: 
747:     - You can safely ignore all `partial=True` events and only process `partial=False` events if you don't need streaming display
748:     - If you do display `partial=True` events, the `partial=False` event provides the complete merged text for validation or storage
749:     - This accumulation is handled automatically by ADK's `StreamingResponseAggregator`—you don't need to manually concatenate partial text chunks
750: 
751: #### Handling `interrupted` Flag
752: 
753: This enables natural conversation flow by detecting when users interrupt the model mid-response, allowing you to stop rendering outdated content immediately.
754: 
755: When users send new input while the model is still generating a response (common in voice conversations), you'll receive an event with `interrupted=True`:
756: 
757: **Usage:**
758: 
759: ```python
760: async for event in runner.run_live(...):
761:     if event.interrupted:
762:         # Your logic to stop displaying partial text and clear typing indicators
763:         stop_streaming_display()
764: 
765:         # Your logic to show interruption in UI (optional)
766:         show_user_interruption_indicator()
767: ```
768: 
769: **Example - Interruption Scenario:**
770: 
771: ```text
772: Model: "The weather in San Francisco is currently..."
773: User: [interrupts] "Actually, I meant San Diego"
774: → event.interrupted=True received
775: → Your app: stop rendering model response, clear UI
776: → Model processes new input
777: Model: "The weather in San Diego is..."
778: ```
779: 
780: **When to use interruption handling:**
781: 
782: - **Voice conversations**: Stop audio playback immediately when user starts speaking
783: - **Clear UI state**: Remove typing indicators and partial text displays
784: - **Conversation logging**: Mark which responses were interrupted (incomplete)
785: - **User feedback**: Show visual indication that interruption was recognized
786: 
787: #### Handling `turn_complete` Flag
788: 
789: This signals conversation boundaries, allowing you to update UI state (enable input controls, hide indicators) and mark proper turn boundaries in logs and analytics.
790: 
791: When the model finishes its complete response, you'll receive an event with `turn_complete=True`:
792: 
793: **Usage:**
794: 
795: ```python
796: async for event in runner.run_live(...):
797:     if event.turn_complete:
798:         # Your logic to update UI to show "ready for input" state
799:         enable_user_input()
800:         # Your logic to hide typing indicator
801:         hide_typing_indicator()
802: 
803:         # Your logic to mark conversation boundary in logs
804:         log_turn_boundary()
805: ```
806: 
807: **Event Flag Combinations:**
808: 
809: Understanding how `turn_complete` and `interrupted` combine helps you handle all conversation states:
810: 
811: | Scenario | turn_complete | interrupted | Your App Should |
812: |----------|---------------|-------------|-----------------|
813: | Normal completion | True | False | Enable input, show "ready" state |
814: | User interrupted mid-response | False | True | Stop display, clear partial content |
815: | Interrupted at end | True | True | Same as normal completion (turn is done) |
816: | Mid-response (partial text) | False | False | Continue displaying streaming text |
817: 
818: **Implementation:**
819: 
820: ```python
821: async for event in runner.run_live(...):
822:     # Handle streaming text
823:     if event.content and event.content.parts and event.content.parts[0].text:
824:         if event.partial:
825:             # Your logic to show typing indicator and update partial text
826:             update_streaming_text(event.content.parts[0].text)
827:         else:
828:             # Your logic to display complete text chunk
829:             display_text(event.content.parts[0].text)
830: 
831:     # Handle interruption
832:     if event.interrupted:
833:         # Your logic to stop audio playback and clear indicators
834:         stop_audio_playback()
835:         clear_streaming_indicators()
836: 
837:     # Handle turn completion
838:     if event.turn_complete:
839:         # Your logic to enable user input
840:         show_input_ready_state()
841:         enable_microphone()
842: ```
843: 
844: **Common Use Cases:**
845: 
846: - **UI state management**: Show/hide "ready for input" indicators, typing animations, microphone states
847: - **Audio playback control**: Know when to stop rendering audio chunks from the model
848: - **Conversation logging**: Mark clear boundaries between turns for history/analytics
849: - **Streaming optimization**: Stop buffering when turn is complete
850: 
851: **Turn completion and caching:** Audio/transcript caches are flushed automatically at specific points during streaming:
852: - **On turn completion** (`turn_complete=True`): Both user and model audio caches are flushed
853: - **On interruption** (`interrupted=True`): Model audio cache is flushed
854: - **On generation completion**: Model audio cache is flushed
855: 
856: ## Serializing Events to JSON
857: 
858: ADK `Event` objects are Pydantic models, which means they come with powerful serialization capabilities. The `model_dump_json()` method is particularly useful for streaming events over network protocols like WebSockets or Server-Sent Events (SSE).
859: 
860: ### Using event.model_dump_json()
861: 
862: This provides a simple one-liner to convert ADK events into JSON format that can be sent over network protocols like WebSockets or SSE.
863: 
864: The `model_dump_json()` method serializes an `Event` object to a JSON string:
865: 
866: ```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/4274c70ae3f4c68595f543ee504474747ea9f0da/python/agents/bidi-demo/app/main.py#L191-L206" target="_blank">main.py:191-206</a>'
867: async def downstream_task() -> None:
868:     """Receives Events from run_live() and sends to WebSocket."""
869:     async for event in runner.run_live(
870:         user_id=user_id,
871:         session_id=session_id,
872:         live_request_queue=live_request_queue,
873:         run_config=run_config
874:     ):
875:         event_json = event.model_dump_json(exclude_none=True, by_alias=True)
876:         await websocket.send_text(event_json)
877: ```
878: 
879: **What gets serialized:**
880: 
881: - Event metadata (author, server_content fields)
882: - Content (text, audio data, function calls)
883: - Event flags (partial, turn_complete, interrupted)
884: - Transcription data (input_transcription, output_transcription)
885: - Tool execution information
886: 
887: **When to use `model_dump_json()`:**
888: 
889: - ✅ Streaming events over network (WebSocket, SSE)
890: - ✅ Logging/persistence to JSON files
891: - ✅ Debugging and inspection
892: - ✅ Integration with JSON-based APIs
893: 
894: **When NOT to use it:**
895: 
896: - ❌ In-memory processing (use event objects directly)
897: - ❌ High-frequency events where serialization overhead matters
898: - ❌ When you only need a few fields (extract them directly instead)
899: 
900: !!! warning "Performance Warning"
901: 
902:     Binary audio data in `event.content.parts[].inline_data` will be base64-encoded when serialized to JSON, significantly increasing payload size (~133% overhead). For production applications with audio, send binary data separately using WebSocket binary frames or multipart HTTP. See [Optimization for Audio Transmission](#optimization-for-audio-transmission) for details.
903: 
904: ### Serialization options
905: 
906: This allows you to reduce payload sizes by excluding unnecessary fields, improving network performance and client processing speed.
907: 
908: Pydantic's `model_dump_json()` supports several useful parameters:
909: 
910: **Usage:**
911: 
912: ```python
913: # Exclude None values for smaller payloads (with camelCase field names)
914: event_json = event.model_dump_json(exclude_none=True, by_alias=True)
915: 
916: # Custom exclusions (e.g., skip large binary audio)
917: event_json = event.model_dump_json(
918:     exclude={'content': {'parts': {'__all__': {'inline_data'}}}},
919:     by_alias=True
920: )
921: 
922: # Include only specific fields
923: event_json = event.model_dump_json(
924:     include={'content', 'author', 'turn_complete', 'interrupted'},
925:     by_alias=True
926: )
927: 
928: # Pretty-printed JSON (for debugging)
929: event_json = event.model_dump_json(indent=2, by_alias=True)
930: ```
931: 
932: The bidi-demo uses `exclude_none=True` to minimize payload size by omitting fields with None values.
933: 
934: ### Deserializing on the Client
935: 
936: This shows how to parse and handle serialized events on the client side, enabling responsive UI updates based on event properties like turn completion and interruptions.
937: 
938: On the client side (JavaScript/TypeScript), parse the JSON back to objects:
939: 
940: ```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/4274c70ae3f4c68595f543ee504474747ea9f0da/python/agents/bidi-demo/app/static/js/app.js#L297-L576" target="_blank">app.js:297-576</a>'
941: // Handle incoming messages
942: websocket.onmessage = function (event) {
943:     // Parse the incoming ADK Event
944:     const adkEvent = JSON.parse(event.data);
945: 
946:     // Handle turn complete event
947:     if (adkEvent.turnComplete === true) {
948:         // Remove typing indicator from current message
949:         if (currentBubbleElement) {
950:             const textElement = currentBubbleElement.querySelector(".bubble-text");
951:             const typingIndicator = textElement.querySelector(".typing-indicator");
952:             if (typingIndicator) {
953:                 typingIndicator.remove();
954:             }
955:         }
956:         currentMessageId = null;
957:         currentBubbleElement = null;
958:         return;
959:     }
960: 
961:     // Handle interrupted event
962:     if (adkEvent.interrupted === true) {
963:         // Stop audio playback if it's playing
964:         if (audioPlayerNode) {
965:             audioPlayerNode.port.postMessage({ command: "endOfAudio" });
966:         }
967: 
968:         // Keep the partial message but mark it as interrupted
969:         if (currentBubbleElement) {
970:             const textElement = currentBubbleElement.querySelector(".bubble-text");
971: 
972:             // Remove typing indicator
973:             const typingIndicator = textElement.querySelector(".typing-indicator");
974:             if (typingIndicator) {
975:                 typingIndicator.remove();
976:             }
977: 
978:             // Add interrupted marker
979:             currentBubbleElement.classList.add("interrupted");
980:         }
981: 
982:         currentMessageId = null;
983:         currentBubbleElement = null;
984:         return;
985:     }
986: 
987:     // Handle content events (text or audio)
988:     if (adkEvent.content && adkEvent.content.parts) {
989:         const parts = adkEvent.content.parts;
990: 
991:         for (const part of parts) {
992:             // Handle text
993:             if (part.text) {
994:                 // Add a new message bubble for a new turn
995:                 if (currentMessageId == null) {
996:                     currentMessageId = Math.random().toString(36).substring(7);
997:                     currentBubbleElement = createMessageBubble(part.text, false, true);
998:                     currentBubbleElement.id = currentMessageId;
999:                     messagesDiv.appendChild(currentBubbleElement);
1000:                 } else {
1001:                     // Update the existing message bubble with accumulated text
1002:                     const existingText = currentBubbleElement.querySelector(".bubble-text").textContent;
1003:                     const cleanText = existingText.replace(/\.\.\.$/, '');
1004:                     updateMessageBubble(currentBubbleElement, cleanText + part.text, true);
1005:                 }
1006: 
1007:                 scrollToBottom();
1008:             }
1009:         }
1010:     }
1011: };
1012: ```
1013: 
1014: !!! note "Demo Implementation"
1015: 
1016:     See the complete WebSocket message handler in [`app.js:297-576`](https://github.com/google/adk-samples/blob/4274c70ae3f4c68595f543ee504474747ea9f0da/python/agents/bidi-demo/app/static/js/app.js#L297-L576)
1017: 
1018: ### Optimization for Audio Transmission
1019: 
1020: Base64-encoded binary audio in JSON significantly increases payload size. For production applications, use a single WebSocket connection with both binary frames (for audio) and text frames (for metadata):
1021: 
1022: **Usage:**
1023: 
1024: ```python
1025: async for event in runner.run_live(...):
1026:     # Check for binary audio
1027:     has_audio = (
1028:         event.content and
1029:         event.content.parts and
1030:         any(p.inline_data for p in event.content.parts)
1031:     )
1032: 
1033:     if has_audio:
1034:         # Send audio via binary WebSocket frame
1035:         for part in event.content.parts:
1036:             if part.inline_data:
1037:                 await websocket.send_bytes(part.inline_data.data)
1038: 
1039:         # Send metadata only (much smaller)
1040:         metadata_json = event.model_dump_json(
1041:             exclude={'content': {'parts': {'__all__': {'inline_data'}}}},
1042:             by_alias=True
1043:         )
1044:         await websocket.send_text(metadata_json)
1045:     else:
1046:         # Text-only events can be sent as JSON
1047:         await websocket.send_text(event.model_dump_json(exclude_none=True, by_alias=True))
1048: ```
1049: 
1050: This approach reduces bandwidth by ~75% for audio-heavy streams while maintaining full event metadata.
1051: 
1052: ## Automatic Tool Execution in run_live()
1053: 
1054: !!! note "Source Reference"
1055: 
1056:     See automatic tool execution implementation in [`functions.py`](https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/flows/llm_flows/functions.py)
1057: 
1058: One of the most powerful features of ADK's `run_live()` is **automatic tool execution**. Unlike the raw Gemini Live API, which requires you to manually handle tool calls and responses, ADK abstracts this complexity entirely.
1059: 
1060: ### The Challenge with Raw Live API
1061: 
1062: When using the Gemini Live API directly (without ADK), tool use requires manual orchestration:
1063: 
1064: 1. **Receive** function calls from the model
1065: 2. **Execute** the tools yourself
1066: 3. **Format** function responses correctly
1067: 4. **Send** responses back to the model
1068: 
1069: This creates significant implementation overhead, especially in streaming contexts where you need to handle multiple concurrent tool calls, manage errors, and coordinate with ongoing audio/text streams.
1070: 
1071: ### How ADK Simplifies Tool Use
1072: 
1073: With ADK, tool execution becomes declarative. Simply define tools on your Agent:
1074: 
1075: ```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/4274c70ae3f4c68595f543ee504474747ea9f0da/python/agents/bidi-demo/app/google_search_agent/agent.py#L11-L16" target="_blank">agent.py:11-16</a>'
1076: import os
1077: from google.adk.agents import Agent
1078: from google.adk.tools import google_search
1079: 
1080: agent = Agent(
1081:     name="google_search_agent",
1082:     model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-09-2025"),
1083:     tools=[google_search],
1084:     instruction="You are a helpful assistant that can search the web."
1085: )
1086: ```
1087: 
1088: When you call `runner.run_live()`, ADK automatically:
1089: 
1090: - **Detects** when the model returns function calls in streaming responses
1091: - **Executes** tools in parallel for maximum performance
1092: - **Handles** before/after tool callbacks for custom logic
1093: - **Formats** function responses according to Live API requirements
1094: - **Sends** responses back to the model seamlessly
1095: - **Yields** both function call and response events to your application
1096: 
1097: ### Tool Execution Events
1098: 
1099: When tools execute, you'll receive events through the `run_live()` async generator:
1100: 
1101: **Usage:**
1102: 
1103: ```python
1104: async for event in runner.run_live(...):
1105:     # Function call event - model requesting tool execution
1106:     if event.get_function_calls():
1107:         print(f"Model calling: {event.get_function_calls()[0].name}")
1108: 
1109:     # Function response event - tool execution result
1110:     if event.get_function_responses():
1111:         print(f"Tool result: {event.get_function_responses()[0].response}")
1112: ```
1113: 
1114: You don't need to handle the execution yourself—ADK does it automatically. You just observe the events as they flow through the conversation.
1115: 
1116: !!! note "Learn More"
1117: 
1118:     The bidi-demo sends all events (including function calls and responses) directly to the WebSocket client without server-side filtering. This allows the client to observe tool execution in real-time through the event stream. See the downstream task in [`main.py:191-206`](https://github.com/google/adk-samples/blob/4274c70ae3f4c68595f543ee504474747ea9f0da/python/agents/bidi-demo/app/main.py#L191-L206)
1119: 
1120: ### Long-Running and Streaming Tools
1121: 
1122: ADK supports advanced tool patterns that integrate seamlessly with `run_live()`:
1123: 
1124: **Long-Running Tools**: Tools that require human approval or take extended time to complete. Mark them with `is_long_running=True`. In resumable async flows, ADK can pause after long-running calls. In live flows, streaming continues; `long_running_tool_ids` indicate pending operations and clients can display appropriate UI.
1125: 
1126: **Streaming Tools**: Tools that accept an `input_stream` parameter with type `LiveRequestQueue` can send real-time updates back to the model during execution, enabling progressive responses.
1127: 
1128: !!! note "How Streaming Tools Work"
1129: 
1130:     When you call `runner.run_live()`, ADK inspects your agent's tools at initialization (lines 828-865 in `runners.py`) to identify streaming tools by checking parameter type annotations for `LiveRequestQueue`.
1131: 
1132:     **Queue creation and lifecycle**:
1133: 
1134:     1. **Creation**: ADK creates an `ActiveStreamingTool` with a dedicated `LiveRequestQueue` for each streaming tool at the start of `run_live()` (before processing any events)
1135:     2. **Storage**: These queues are stored in `invocation_context.active_streaming_tools[tool_name]` for the duration of the invocation
1136:     3. **Injection**: When the model calls the tool, ADK automatically injects the tool's queue as the `input_stream` parameter (lines 238-253 in `function_tool.py`)
1137:     4. **Usage**: The tool can use this queue to send real-time updates back to the model during execution
1138:     5. **Lifecycle**: The queues persist for the entire `run_live()` invocation (one InvocationContext = one `run_live()` call) and are destroyed when `run_live()` exits
1139: 
1140:     **Queue distinction**:
1141: 
1142:     - **Main queue** (`live_request_queue` parameter): Created by your application, used for client-to-model communication
1143:     - **Tool queues** (`active_streaming_tools[tool_name].stream`): Created automatically by ADK, used for tool-to-model communication during execution
1144: 
1145:     Both types of queues are `LiveRequestQueue` instances, but they serve different purposes in the streaming architecture.
1146: 
1147:     This enables tools to provide incremental updates, progress notifications, or partial results during long-running operations.
1148: 
1149:     **Code reference**: See `runners.py:828-865` (tool detection) and `function_tool.py:238-253` (parameter injection) for implementation details.
1150: 
1151:     See the [Tools Guide](https://google.github.io/adk-docs/tools/) for implementation examples.
1152: 
1153: ### Key Takeaway
1154: 
1155: The difference between raw Live API tool use and ADK is stark:
1156: 
1157: | Aspect | Raw Live API | ADK `run_live()` |
1158: |--------|--------------|------------------|
1159: | **Tool Declaration** | Manual schema definition | Automatic from Python functions |
1160: | **Tool Execution** | Manual handling in app code | Automatic parallel execution |
1161: | **Response Formatting** | Manual JSON construction | Automatic |
1162: | **Error Handling** | Manual try/catch and formatting | Automatic capture and reporting |
1163: | **Streaming Integration** | Manual coordination | Automatic event yielding |
1164: | **Developer Experience** | Complex, error-prone | Declarative, simple |
1165: 
1166: This automatic handling is one of the core value propositions of ADK—it transforms the complexity of Live API tool use into a simple, declarative developer experience.
1167: 
1168: ## InvocationContext: The Execution State Container
1169: 
1170: !!! note "Source Reference"
1171: 
1172:     See InvocationContext implementation in [`invocation_context.py`](https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/agents/invocation_context.py)
1173: 
1174: While `run_live()` returns an AsyncGenerator for consuming events, internally it creates and manages an `InvocationContext`—ADK's unified state carrier that encapsulates everything needed for a complete conversation invocation. **One InvocationContext corresponds to one `run_live()` loop**—it's created when you call `run_live()` and persists for the entire streaming session.
1175: 
1176: Think of it as a traveling notebook that accompanies a conversation from start to finish, collecting information, tracking progress, and providing context to every component along the way. It's ADK's runtime implementation of the Context concept, providing the execution-time state and services needed during a live conversation. For a broader overview of context in ADK, see [Context in ADK](https://google.github.io/adk-docs/context/).
1177: 
1178: ### What is an Invocation?
1179: 
1180: An **invocation** represents a complete interaction cycle:
1181: - Starts with user input (text, audio, or control signal)
1182: - May involve one or multiple agent calls
1183: - Ends when a final response is generated or when explicitly terminated
1184: - Is orchestrated by `runner.run_live()` or `runner.run_async()`
1185: 
1186: This is distinct from an **agent call** (execution of a single agent's logic) and a **step** (a single LLM call plus any resulting tool executions).
1187: 
1188: The hierarchy looks like this:
1189: 
1190: ```text
1191:    ┌─────────────────────── invocation ──────────────────────────┐
1192:    ┌──────────── llm_agent_call_1 ────────────┐ ┌─ agent_call_2 ─┐
1193:    ┌──── step_1 ────────┐ ┌───── step_2 ──────┐
1194:    [call_llm] [call_tool] [call_llm] [transfer]
1195: ```
1196: 
1197: ### Who Uses InvocationContext?
1198: 
1199: InvocationContext serves different audiences at different levels:
1200: 
1201: - **ADK's internal components** (primary users): Runner, Agent, LLMFlow, and GeminiLlmConnection all receive, read from, and write to the InvocationContext as it flows through the stack. This shared context enables seamless coordination without tight coupling.
1202: 
1203: - **Application developers** (indirect beneficiaries): You don't typically create or manipulate InvocationContext directly in your application code. Instead, you benefit from the clean, simplified APIs that InvocationContext enables behind the scenes—like the elegant `async for event in runner.run_live()` pattern.
1204: 
1205: - **Tool and callback developers** (direct access): When you implement custom tools or callbacks, you receive InvocationContext as a parameter. This gives you direct access to conversation state, session services, and control flags (like `end_invocation`) to implement sophisticated behaviors.
1206: 
1207: #### What InvocationContext Contains
1208: 
1209: When you implement custom tools or callbacks, you receive InvocationContext as a parameter. Here's what's available to you:
1210: 
1211: **Essential Fields for Tool/Callback Developers:**
1212: 
1213: - **`context.invocation_id`**: Current invocation identifier (unique per `run_live()` call)
1214: - **`context.session`**:
1215:   - **`context.session.events`**: All events in the session history (across all invocations)
1216:   - **`context.session.state`**: Persistent key-value store for session data
1217:   - **`context.session.user_id`**: User identity
1218: - **`context.run_config`**: Current streaming configuration (response modalities, transcription settings, cost limits)
1219: - **`context.end_invocation`**: Set this to `True` to immediately terminate the conversation (useful for error handling or policy enforcement)
1220: 
1221: **Example Use Cases in Tool Development:**
1222: 
1223: ```python
1224: # Example: Comprehensive tool implementation showing common InvocationContext patterns
1225: def my_tool(context: InvocationContext, query: str):
1226:     # Access user identity
1227:     user_id = context.session.user_id
1228: 
1229:     # Check if this is the user's first message
1230:     event_count = len(context.session.events)
1231:     if event_count == 0:
1232:         return "Welcome! This is your first message."
1233: 
1234:     # Access conversation history
1235:     recent_events = context.session.events[-5:]  # Last 5 events
1236: 
1237:     # Access persistent session state
1238:     # Session state persists across invocations (not just this streaming session)
1239:     user_preferences = context.session.state.get('user_preferences', {})
1240: 
1241:     # Update session state (will be persisted)
1242:     context.session.state['last_query_time'] = datetime.now().isoformat()
1243: 
1244:     # Access services for persistence
1245:     if context.artifact_service:
1246:         # Store large files/audio
1247:         await context.artifact_service.save_artifact(
1248:             app_name=context.session.app_name,
1249:             user_id=context.session.user_id,
1250:             session_id=context.session.id,
1251:             filename="result.bin",
1252:             artifact=types.Part(inline_data=types.Blob(mime_type="application/octet-stream", data=data)),
1253:         )
1254: 
1255:     # Process the query with context
1256:     result = process_query(query, context=recent_events, preferences=user_preferences)
1257: 
1258:     # Terminate conversation in specific scenarios
1259:     if result.get('error'):
1260:         # Processing error - stop conversation
1261:         context.end_invocation = True
1262: 
1263:     return result
1264: ```
1265: 
1266: Understanding InvocationContext is essential for grasping how ADK maintains state, coordinates execution, and enables advanced features like multi-agent workflows and resumability. Even if you never touch it directly, knowing what flows through your application helps you design better agents and debug issues more effectively.
1267: 
1268: ## Best Practices for Multi-Agent Workflows
1269: 
1270: ADK's bidirectional streaming supports three agent architectures: **single agent** (one agent handles the entire conversation), **multi-agent with sub-agents** (a coordinator agent dynamically routes to specialist agents using `transfer_to_agent`), and **sequential workflow agents** (agents execute in a fixed pipeline using `task_completed`). This section focuses on best practices for sequential workflows, where understanding agent transitions and state sharing is crucial for smooth BIDI communication.
1271: 
1272: !!! note "Learn More"
1273: 
1274:     For comprehensive coverage of multi-agent patterns, see [Workflow Agents as Orchestrators](https://google.github.io/adk-docs/agents/multi-agents/#workflow-agents-as-orchestrators) in the ADK documentation.
1275: 
1276: When building multi-agent systems with ADK, understanding how agents transition and share state during live streaming is crucial for smooth BIDI communication.
1277: 
1278: ### SequentialAgent with BIDI Streaming
1279: 
1280: `SequentialAgent` enables workflow pipelines where agents execute one after another. Each agent completes its task before the next one begins. The challenge with live streaming is determining when an agent has finished processing continuous audio or video input.
1281: 
1282: !!! note "Source Reference"
1283: 
1284:     See SequentialAgent implementation in [`sequential_agent.py:119-158`](https://github.com/google/adk-python/blob/960b206752918d13f127a9d6ed8d21d34bcbc7fa/src/google/adk/agents/sequential_agent.py#L119-L158)
1285: 
1286: **How it works:**
1287: 
1288: ADK automatically adds a `task_completed()` function to each agent in the sequence. When the model calls this function, it signals completion and triggers the transition to the next agent:
1289: 
1290: **Usage:**
1291: 
1292: ```python
1293: # SequentialAgent automatically adds this tool to each sub-agent
1294: def task_completed():
1295:     """
1296:     Signals that the agent has successfully completed the user's question
1297:     or task.
1298:     """
1299:     return 'Task completion signaled.'
1300: ```
1301: 
1302: ### Recommended Pattern: Transparent Sequential Flow
1303: 
1304: The key insight is that **agent transitions happen transparently** within the same `run_live()` event stream. Your application doesn't need to manage transitions—just consume events uniformly:
1305: 
1306: **Usage:**
1307: 
1308: ```python
1309: async def handle_sequential_workflow():
1310:     """Recommended pattern for SequentialAgent with BIDI streaming."""
1311: 
1312:     # 1. Single queue shared across all agents in the sequence
1313:     queue = LiveRequestQueue()
1314: 
1315:     # 2. Background task captures user input continuously
1316:     async def capture_user_input():
1317:         while True:
1318:             # Your logic to read audio from microphone
1319:             audio_chunk = await microphone.read()
1320:             queue.send_realtime(
1321:                 blob=types.Blob(data=audio_chunk, mime_type="audio/pcm")
1322:             )
1323: 
1324:     input_task = asyncio.create_task(capture_user_input())
1325: 
1326:     try:
1327:         # 3. Single event loop handles ALL agents seamlessly
1328:         async for event in runner.run_live(
1329:             user_id="user_123",
1330:             session_id="session_456",
1331:             live_request_queue=queue,
1332:         ):
1333:             # Events flow seamlessly across agent transitions
1334:             current_agent = event.author
1335: 
1336:             # Handle audio and text output
1337:             if event.content and event.content.parts:
1338:                 for part in event.content.parts:
1339:                     # Check for audio data
1340:                     if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
1341:                         # Your logic to play audio
1342:             await play_audio(part.inline_data.data)
1343: 
1344:                     # Check for text data
1345:                     if part.text:
1346:                         await display_text(f"[{current_agent}] {part.text}")
1347: 
1348:             # No special transition handling needed!
1349: 
1350:     finally:
1351:         input_task.cancel()
1352:         queue.close()
1353: ```
1354: 
1355: ### Event Flow During Agent Transitions
1356: 
1357: Here's what your application sees when agents transition:
1358: 
1359: ```text
1360: # Agent 1 (Researcher) completes its work
1361: Event: author="researcher", text="I've gathered all the data."
1362: Event: author="researcher", function_call: task_completed()
1363: Event: author="researcher", function_response: task_completed
1364: 
1365: # --- Automatic transition (invisible to your code) ---
1366: 
1367: # Agent 2 (Writer) begins
1368: Event: author="writer", text="Let me write the report based on the research..."
1369: Event: author="writer", text=" The findings show..."
1370: Event: author="writer", function_call: task_completed()
1371: Event: author="writer", function_response: task_completed
1372: 
1373: # --- Automatic transition ---
1374: 
1375: # Agent 3 (Reviewer) begins - the last agent in sequence
1376: Event: author="reviewer", text="Let me review the report..."
1377: Event: author="reviewer", text="The report looks good. All done!"
1378: Event: author="reviewer", function_call: task_completed()
1379: Event: author="reviewer", function_response: task_completed
1380: 
1381: # --- Last agent completed: run_live() exits ---
1382: # Your async for loop ends here
1383: ```
1384: 
1385: ### Design Principles
1386: 
1387: #### 1. Single Event Loop
1388: 
1389: Use one event loop for all agents in the sequence:
1390: 
1391: **Usage:**
1392: 
1393: ```python
1394: # ✅ CORRECT: One loop handles all agents
1395: async for event in runner.run_live(...):
1396:     # Your event handling logic here
1397:     await handle_event(event)  # Works for Agent1, Agent2, Agent3...
1398: 
1399: # ❌ INCORRECT: Don't break the loop or create multiple loops
1400: for agent in agents:
1401:     async for event in runner.run_live(...):  # WRONG!
1402:         ...
1403: ```
1404: 
1405: #### 2. Persistent Queue
1406: 
1407: The same `LiveRequestQueue` serves all agents:
1408: 
1409: ```text
1410: # User input flows to whichever agent is currently active
1411: User speaks → Queue → Agent1 (researcher)
1412:                 ↓
1413: User speaks → Queue → Agent2 (writer)
1414:                 ↓
1415: User speaks → Queue → Agent3 (reviewer)
1416: ```
1417: 
1418: **Don't create new queues per agent:**
1419: 
1420: ```python
1421: # ❌ INCORRECT: New queue per agent
1422: for agent in agents:
1423:     new_queue = LiveRequestQueue()  # WRONG!
1424: 
1425: # ✅ CORRECT: Single queue for entire workflow
1426: queue = LiveRequestQueue()
1427: async for event in runner.run_live(live_request_queue=queue):
1428:     ...
1429: ```
1430: 
1431: #### 3. Agent-Aware UI (Optional)
1432: 
1433: Track which agent is active for better user experience:
1434: 
1435: **Usage:**
1436: 
1437: ```python
1438: current_agent_name = None
1439: 
1440: async for event in runner.run_live(...):
1441:     # Detect agent transitions
1442:     if event.author and event.author != current_agent_name:
1443:         current_agent_name = event.author
1444:         # Your logic to update UI indicator
1445:         await update_ui_indicator(f"Now: {current_agent_name}")
1446: 
1447:     # Your event handling logic here
1448:     await handle_event(event)
1449: ```
1450: 
1451: #### 4. Transition Notifications
1452: 
1453: Optionally notify users when agents hand off:
1454: 
1455: **Usage:**
1456: 
1457: ```python
1458: async for event in runner.run_live(...):
1459:     # Detect task completion (transition signal)
1460:     if event.content and event.content.parts:
1461:         for part in event.content.parts:
1462:             if (part.function_response and
1463:                 part.function_response.name == "task_completed"):
1464:                 # Your logic to display transition notification
1465:                 await display_notification(
1466:                     f"✓ {event.author} completed. Handing off to next agent..."
1467:                 )
1468:                 continue
1469: 
1470:     # Your event handling logic here
1471:     await handle_event(event)
1472: ```
1473: 
1474: ### Key Differences: transfer_to_agent vs task_completed
1475: 
1476: Understanding these two functions helps you choose the right multi-agent pattern:
1477: 
1478: | Function | Agent Pattern | When `run_live()` Exits | Use Case |
1479: |----------|--------------|----------------------|----------|
1480: | `transfer_to_agent` | Coordinator (dynamic routing) | `LiveRequestQueue.close()` | Route user to specialist based on intent |
1481: | `task_completed` | Sequential (pipeline) | `LiveRequestQueue.close()` or `task_completed` of the last agent | Fixed workflow: research → write → review |
1482: 
1483: **transfer_to_agent example:**
1484: 
1485: ```text
1486: # Coordinator routes based on user intent
1487: User: "I need help with billing"
1488: Event: author="coordinator", function_call: transfer_to_agent(agent_name="billing")
1489: # Stream continues with billing agent - same run_live() loop
1490: Event: author="billing", text="I can help with your billing question..."
1491: ```
1492: 
1493: **task_completed example:**
1494: 
1495: ```text
1496: # Sequential workflow progresses through pipeline
1497: Event: author="researcher", function_call: task_completed()
1498: # Current agent exits, next agent in sequence begins
1499: Event: author="writer", text="Based on the research..."
1500: ```
1501: 
1502: ### Best Practices Summary
1503: 
1504: | Practice | Reason |
1505: |----------|--------|
1506: | Use single event loop | ADK handles transitions internally |
1507: | Keep queue alive across agents | Same queue serves all sequential agents |
1508: | Track `event.author` | Know which agent is currently responding |
1509: | Don't reset session/context | Conversation state persists across agents |
1510: | Handle events uniformly | All agents produce the same event types |
1511: | Let `task_completed` signal transitions | Don't manually manage sequential flow |
1512: 
1513: The SequentialAgent design ensures smooth transitions—your application simply sees a continuous stream of events from different agents in sequence, with automatic handoffs managed by ADK.
1514: 
1515: ## Summary
1516: 
1517: In this part, you mastered event handling in ADK's Bidi-streaming architecture. We explored the different event types that agents generate—text responses, audio chunks, transcriptions, tool calls, and control signals—and learned how to process each event type effectively. You now understand how to handle interruptions and turn completion signals for natural conversation flow, serialize events for network transport using Pydantic's model serialization, leverage ADK's automatic tool execution to simplify agent workflows, and access InvocationContext for advanced state management scenarios. With these event handling patterns in place, you're equipped to build responsive streaming applications that provide real-time feedback to users. Next, you'll learn how to configure sophisticated streaming behaviors through RunConfig, including multimodal interactions, session resumption, and cost controls.
1518: 
1519: ---
1520: 
1521: ← [Previous: Part 2 - Sending Messages with LiveRequestQueue](part2.md) | [Next: Part 4 - Understanding RunConfig](part4.md) →