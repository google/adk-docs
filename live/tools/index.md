# Tools for live agents

Supported in ADKPython v0.1.0Java v0.2.0

Tools work in a live agent much as they do anywhere else in ADK: you pass functions to an agent and the model calls them. How you write a tool does not change under a live connection, so tool definitions, tool context, callbacks, and authentication all follow [Custom Tools](https://adk.dev/tools-custom/index.md).

A live connection adds two capabilities on top. ADK executes tool calls for you inside the `run_live()` loop, so you never write the function-call plumbing the raw Live API would require. Live agents can also use *streaming tools*: functions that stay running and push intermediate results back to the agent, so the agent can react to a stock price moving or a person appearing in a video frame without the user asking again.

## Automatic tool execution

Define tools on your agent and ADK calls them for you inside the `run_live()` loop: it detects the model's function calls, runs the tools (in parallel, with your before/after callbacks), formats the responses, and yields both the call and the response as events. You write the function, not the plumbing.

```python
import os
from google.adk.agents import Agent
from google.adk.tools import google_search

agent = Agent(
    name="google_search_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
    tools=[google_search],
    instruction="You are a helpful assistant that can search the web.",
)
```

You observe tool activity through the event stream; you never drive it:

```python
async for event in runner.run_live(...):
    if event.get_function_calls():
        print(f"Model calling: {event.get_function_calls()[0].name}")
    if event.get_function_responses():
        print(f"Tool result: {event.get_function_responses()[0].response}")
```

## Keeping the agent responsive

A slow tool is survivable in a chat window, where the user watches a spinner. In a live voice conversation it is not: if the agent calls a ten-second API and goes silent, the user assumes the call dropped. You need a tool that does not block the conversation while it runs. ADK gives you two ways to do that, plus plain blocking for the fast case:

| Your situation                    | Use                                          | How                                      |
| --------------------------------- | -------------------------------------------- | ---------------------------------------- |
| Tool returns in under a second    | **Blocking** (the default)                   | A normal `return` tool                   |
| Long wait with nothing to narrate | **[Non-blocking tool](#non-blocking-tools)** | Set `response_scheduling` on the tool    |
| Long wait worth narrating         | **[Streaming tool](#streaming-tools)**       | `yield` progress from an async generator |

## Non-blocking tools

Some waits have nothing worth narrating: a long analytics query, a batch export, a media generation job. Progress updates the user did not ask for interrupt the conversation for no benefit. Keep your plain `return`-once tool and set `response_scheduling` to move it to the background:

```python
from google.adk.tools import FunctionTool
from google.genai import types

async def export_report(region: str) -> dict:
    """Generate and store the quarterly report. Returns when the export finishes."""
    await run_export(region)  # a long, plain return-once operation
    return {"status": "done", "region": region}

report_tool = FunctionTool(export_report)
report_tool.response_scheduling = types.FunctionResponseScheduling.WHEN_IDLE
```

The agent stays free while the tool runs, answers whatever else the user brings up, and folds the result in when it is ready. A runnable example ships as the [`live_non_blocking_tool_agent` sample](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_non_blocking_tool_agent).

Requires Python 2.4+

`response_scheduling` was added in adk-python 2.4, and support is per model. See [Supported models](https://adk.dev/live/models/#live-models).

`response_scheduling` also controls *when* a finished result reaches the user:

| Value       | Behavior                                   | Use it for                              |
| ----------- | ------------------------------------------ | --------------------------------------- |
| `WHEN_IDLE` | Waits for a natural pause                  | Reports and lookups, the usual choice   |
| `INTERRUPT` | Delivers immediately                       | Alarms, failures, "the transfer failed" |
| `SILENT`    | Enters context, announced only if relevant | Background info the model may use later |

## Streaming tools

A streaming tool stays running and pushes intermediate results back to the agent, so the agent can narrate progress or react to a changing input (a stock price, a person entering a video frame) without the user asking again. Making a tool stream is a one-line change: an `async` function that `yield`s instead of `return`s. ADK treats any async-generator tool as non-blocking automatically.

```python
import asyncio
from typing import AsyncGenerator

async def query_sales_database(region: str) -> AsyncGenerator[str, None]:
    """Run the quarterly sales report. Call this once; it streams its own updates."""
    yield "Connecting to the warehouse..."
    await asyncio.sleep(4)
    yield "Aggregating by product line..."
    await asyncio.sleep(4)
    yield f"Done. {summarise(region)}"
```

Pass it to `tools=[...]` like any other tool. The model gets each `yield` as a live update, so instead of silence the user hears "let me pull those up... still aggregating... got it: EMEA did $4.81M, up 12.4%." This suits RAG pipelines, multi-stage aggregation, and build-and-test runs, anywhere the progress is worth telling.

Add ADK's reserved `stop_streaming` tool (an empty function ADK intercepts by name) so users can cancel: "never mind, cancel that."

### Video streaming tools

Add an `input_stream: LiveRequestQueue` parameter and ADK feeds the user's realtime input into a dedicated queue for that tool, so it can pull video frames and react to them.

Requirements for any streaming tool:

- It must be an `async` function typed to return an `AsyncGenerator[T, None]`, where `T` is the type you `yield`.
- For video, add `input_stream: LiveRequestQueue`; ADK fills it in.

The pattern below drains the queue to the newest frame, discarding stale ones, and yields only when the answer changes so the agent stays quiet otherwise.

```python
import asyncio
import os
from typing import AsyncGenerator

from google.adk.agents import LiveRequestQueue
from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool
from google.genai import Client
from google.genai import types as genai_types

PROMPT = "How many people are in this image? Reply with a number only."


async def monitor_video_stream(
    input_stream: LiveRequestQueue,
) -> AsyncGenerator[str, None]:
  """Report how many people are visible, whenever that number changes."""
  client = Client()
  last_count = None

  while True:
    # Drain the queue and keep only the newest frame; older ones are stale.
    latest = None
    while input_stream._queue.qsize() != 0:
      req = await input_stream.get()
      if req.blob and req.blob.mime_type == "image/jpeg":
        latest = req

    if latest is not None:
      response = client.models.generate_content(
          model="gemini-flash-latest",
          contents=genai_types.Content(
              role="user",
              parts=[
                  genai_types.Part.from_bytes(
                      data=latest.blob.data, mime_type=latest.blob.mime_type
                  ),
                  genai_types.Part.from_text(text=PROMPT),
              ],
          ),
      )
      count = response.candidates[0].content.parts[0].text.strip()
      if count != last_count:
        last_count = count
        yield count

    await asyncio.sleep(0.5)


# ADK intercepts this by name; the body stays empty.
def stop_streaming(function_name: str):
  """Stop a running streaming tool.

  Args:
    function_name: The name of the streaming function to stop.
  """


root_agent = Agent(
    # Streaming tools run under run_live(), so the root agent needs a Live
    # model. gemini-flash-latest above is only for the one-shot call in the tool.
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
    name="video_monitoring_agent",
    instruction=(
        "You monitor the user's video stream. Call monitor_video_stream once when"
        " asked, then report each update it sends. Never call it again to poll."
    ),
    tools=[monitor_video_stream, FunctionTool(stop_streaming)],
)
```

```java
import com.google.adk.agents.LiveRequestQueue;
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.genai.Client;
import com.google.genai.types.Content;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Arrays;
import java.util.Map;
import java.util.concurrent.TimeUnit;

public class StreamingTools {

  private static final String PROMPT =
      "How many people are in this image? Reply with a number only.";

  // `inputStream` is a reserved parameter name; ADK passes the video stream in.
  @Schema(description = "Report how many people are visible, whenever that number changes.")
  public static Flowable<Map<String, Object>> monitorVideoStream(
      @Schema(name = "inputStream") LiveRequestQueue inputStream) {
    Client client = Client.builder().build();

    return inputStream
        .get()
        .filter(req -> req.blob().isPresent()
            && "image/jpeg".equals(req.blob().get().mimeType()))
        .sample(500, TimeUnit.MILLISECONDS)  // newest frame every 0.5s
        .map(req -> client.models().generateContent(
                "gemini-flash-latest",
                Content.builder()
                    .role("user")
                    .parts(Arrays.asList(
                        Part.builder().inlineData(req.blob().get()).build(),
                        Part.fromText(PROMPT)))
                    .build(),
                GenerateContentConfig.builder().build())
            .text())
        .distinctUntilChanged()  // yield only when the count changes
        .map(count -> Map.of("result", count));
  }

  // ADK intercepts this by name; the body stays empty.
  @Schema(description = "Stop a running streaming tool.")
  public static void stopStreaming(
      @Schema(name = "functionName", description = "The streaming function to stop.")
      String functionName) {}

  public static void main(String[] args) {
    LlmAgent rootAgent =
        LlmAgent.builder()
            .model("gemini-live-2.5-flash-native-audio")
            .name("video_monitoring_agent")
            .instruction(
                "You monitor the user's video stream. Call monitorVideoStream once when"
                    + " asked, then report each update it sends. Never call it again to poll.")
            .tools(Arrays.asList(
                FunctionTool.create(StreamingTools.class, "monitorVideoStream"),
                FunctionTool.create(StreamingTools.class, "stopStreaming")))
            .build();
  }
}
```

Try it by asking the agent to monitor how many people are in the video stream, then walking in and out of frame.

## Tool execution context

A tool or callback receives an `InvocationContext` for state, history, and artifacts. It works the same as in any ADK agent — see [Agent context](https://adk.dev/context/index.md) — with one difference that matters live: **one `InvocationContext` spans the entire `run_live()` loop**, created when you call `run_live()` and living across every agent and every turn until the session ends. In a request/response agent an invocation is a single turn; in a live session it is the whole conversation.

Two fields come up most in live tools:

| Field                    | What it gives you                                                                                                       |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `context.run_config`     | The session's [configuration](https://adk.dev/live/configuration/index.md) — response modalities, transcription, limits |
| `context.end_invocation` | Set to `True` to terminate the whole streaming session immediately                                                      |
