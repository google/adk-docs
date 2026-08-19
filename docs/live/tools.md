# Tools

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

Tools work in a live agent much as they do anywhere else in ADK: you pass functions to an
agent and the model calls them. Defining tools, tool context, callbacks, and authentication
are all covered in [Custom Tools](../tools-custom/index.md), and none of it changes under a
live connection. This page covers only what live adds.

Two things are different. ADK executes tool calls for you inside the `run_live()` loop, so
you never write the function-call plumbing the raw Live API would require. And live agents
can use *streaming tools*: functions that stay running and push intermediate results back to
the agent, so the agent can react to a stock price moving or a person appearing in a video
frame without the user asking again.

## Automatic tool execution

Define tools on your agent and ADK calls them for you inside the `run_live()` loop: it
detects the model's function calls, runs the tools (in parallel, with your before/after
callbacks), formats the responses, and yields both the call and the response as events. You
write the function, not the plumbing.

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

A slow tool is survivable in a chat window, where the user watches a spinner. In a live
voice conversation it is not: if the agent calls a ten-second API and goes silent, the user
assumes the call dropped. The fix is not a faster tool but a tool that does not block the
conversation while it runs. ADK gives you two ways to do that, plus plain blocking for the
fast case:

| Your situation | Use | How |
|---|---|---|
| Tool returns in under a second | **Blocking** (the default) | A normal `return` tool |
| Long wait worth narrating | **[Streaming tool](#streaming-tools)** | `yield` progress from an async generator |
| Long wait with nothing to narrate | **[Non-blocking tool](#non-blocking-tools)** | Set `response_scheduling` on the tool |

The rule of thumb: if the wait has a story, stream it; if the wait is just a wait, run it in
the background and let the result land at the next pause.

## Streaming tools

A streaming tool stays running and pushes intermediate results back to the agent, so the
agent can narrate progress or react to a changing input (a stock price, a person entering a
video frame) without the user asking again. Making a tool stream is a one-line change: an
`async` function that `yield`s instead of `return`s. ADK treats any async-generator tool as
non-blocking automatically.

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

Pass it to `tools=[...]` like any other tool. The model gets each `yield` as a live update,
so instead of silence the user hears "let me pull those up... still aggregating... got it:
EMEA did $4.81M, up 12.4%." This suits RAG pipelines, multi-stage aggregation, and
build-and-test runs — anywhere the progress is worth telling.

Add ADK's reserved `stop_streaming` tool (an empty function ADK intercepts by name) so users
can cancel: "never mind, cancel that."

### Video streaming tools

A streaming tool that takes an `input_stream: LiveRequestQueue` parameter receives the live
video stream. ADK creates a dedicated queue for it and feeds the user's realtime input in, so
the tool can pull frames and react to them.

Requirements for any streaming tool:

- It must be an `async` function typed to return an `AsyncGenerator[T, None]`, where `T` is
  the type you `yield`.
- For video, add `input_stream: LiveRequestQueue`; ADK fills it in.

### Example: monitor a stock price and a video stream

=== "Python"

    ```python
    import asyncio
    import os
    from typing import AsyncGenerator

    from google.adk.agents import LiveRequestQueue
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools.function_tool import FunctionTool
    from google.genai import Client
    from google.genai import types as genai_types


    async def monitor_stock_price(stock_symbol: str) -> AsyncGenerator[str, None]:
      """Monitor the price for the given stock_symbol, streaming updates as they change."""
      # Mocked price changes; a real tool would poll a market data API.
      for price, wait in ((300, 4), (400, 4), (900, 20), (500, 20)):
        await asyncio.sleep(wait)
        yield f"the price for {stock_symbol} is {price}"


    # for video streaming, `input_stream: LiveRequestQueue` is required and reserved key parameter for ADK to pass the video streams in.
    async def monitor_video_stream(
        input_stream: LiveRequestQueue,
    ) -> AsyncGenerator[str, None]:
      """Monitor how many people are in the video streams."""
      print("start monitor_video_stream!")
      client = Client(enterprise=False)
      prompt_text = (
          "Count the number of people in this image. Just respond with a numeric"
          " number."
      )
      last_count = None
      while True:
        last_valid_req = None
        print("Start monitoring loop")

        # use this loop to pull the latest images and discard the old ones
        while input_stream._queue.qsize() != 0:
          live_req = await input_stream.get()

          if live_req.blob is not None and live_req.blob.mime_type == "image/jpeg":
            last_valid_req = live_req

        # If we found a valid image, process it
        if last_valid_req is not None:
          print("Processing the most recent frame from the queue")

          # Create an image part using the blob's data and mime type
          image_part = genai_types.Part.from_bytes(
              data=last_valid_req.blob.data, mime_type=last_valid_req.blob.mime_type
          )

          contents = genai_types.Content(
              role="user",
              parts=[image_part, genai_types.Part.from_text(prompt_text)],
          )

          # Call the model to generate content based on the provided image and prompt
          response = client.models.generate_content(
              model="gemini-flash-latest",
              contents=contents,
              config=genai_types.GenerateContentConfig(
                  system_instruction=(
                      "You are a helpful video analysis assistant. You can count"
                      " the number of people in this image or video. Just respond"
                      " with a numeric number."
                  )
              ),
          )
          if not last_count:
            last_count = response.candidates[0].content.parts[0].text
          elif last_count != response.candidates[0].content.parts[0].text:
            last_count = response.candidates[0].content.parts[0].text
            yield response
            print("response:", response)

        # Wait before checking for new images
        await asyncio.sleep(0.5)


    # Use this exact function to help ADK stop your streaming tools when requested.
    # for example, if we want to stop `monitor_stock_price`, then the agent will
    # invoke this function with stop_streaming(function_name=monitor_stock_price).
    def stop_streaming(function_name: str):
      """Stop the streaming

      Args:
        function_name: The name of the streaming function to stop.
      """
      pass


    root_agent = Agent(
        # Streaming tools run under runner.run_live(), so the root agent needs a
        # Live API model. gemini-flash-latest is used above only for the one-shot
        # generate_content call inside the tool.
        model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
        name="video_streaming_agent",
        instruction="""
          You are a monitoring agent. You can do video monitoring and stock price monitoring
          using the provided tools/functions.
          When users want to monitor a video stream,
          You can use monitor_video_stream function to do that. When monitor_video_stream
          returns the alert, you should tell the users.
          When users want to monitor a stock price, you can use monitor_stock_price.
          Don't ask too many questions. Don't be too talkative.
        """,
        tools=[
            monitor_video_stream,
            monitor_stock_price,
            FunctionTool(stop_streaming),
        ]
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LiveRequestQueue;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.Annotations.Schema;
    import com.google.adk.tools.FunctionTool;
    import com.google.genai.Client;
    import com.google.genai.types.Content;
    import com.google.genai.types.GenerateContentConfig;
    import com.google.genai.types.GenerateContentResponse;
    import com.google.genai.types.Part;
    import io.reactivex.rxjava3.core.Flowable;
    import java.util.Arrays;
    import java.util.Collections;
    import java.util.Map;
    import java.util.concurrent.TimeUnit;

    public class StreamingTools {

      @Schema(description = "This function will monitor the price for the given stock_symbol in a continuous, streaming and asynchronously way.")
      public static Flowable<Map<String, Object>> monitorStockPrice(@Schema(name = "stockSymbol") String stockSymbol) {
        System.out.println("Start monitor stock price for " + stockSymbol + "!");

        return Flowable.concat(
            Flowable.<Map<String, Object>>just(Collections.singletonMap("result", "the price for " + stockSymbol + " is 300")).delay(4, TimeUnit.SECONDS),
            Flowable.<Map<String, Object>>just(Collections.singletonMap("result", "the price for " + stockSymbol + " is 400")).delay(4, TimeUnit.SECONDS),
            Flowable.<Map<String, Object>>just(Collections.singletonMap("result", "the price for " + stockSymbol + " is 900")).delay(20, TimeUnit.SECONDS),
            Flowable.<Map<String, Object>>just(Collections.singletonMap("result", "the price for " + stockSymbol + " is 500")).delay(20, TimeUnit.SECONDS)
        );
      }

      // for video streaming, `inputStream` is required and reserved parameter for ADK to pass the video streams in.
      @Schema(description = "Monitor how many people are in the video streams.")
      public static Flowable<Map<String, Object>> monitorVideoStream(@Schema(name = "inputStream") LiveRequestQueue inputStream) {
        System.out.println("start monitor_video_stream!");
        Client client = Client.builder().build();
        String promptText = "Count the number of people in this image. Just respond with a numeric number.";
        
        // We use RxJava to process the stream
        return inputStream.get()
            .filter(req -> req.blob().isPresent() && "image/jpeg".equals(req.blob().get().mimeType()))
            .sample(500, TimeUnit.MILLISECONDS) // Process one frame every 0.5 seconds
            .map(req -> {
              System.out.println("Processing the most recent frame from the queue");
              Part imagePart = Part.builder().inlineData(req.blob().get()).build();
              Content contents = Content.builder()
                  .role("user")
                  .parts(Arrays.asList(imagePart, Part.fromText(promptText)))
                  .build();

              GenerateContentResponse response = client.models().generateContent(
                  "gemini-flash-latest",
                  contents,
                  GenerateContentConfig.builder()
                      .systemInstruction(Content.builder().parts(Arrays.asList(
                          Part.fromText("You are a helpful video analysis assistant. You can count the number of people in this image or video. Just respond with a numeric number.")
                      )).build())
                      .build()
              );
              return (Map<String, Object>) Collections.<String, Object>singletonMap("result", response.text());
            })
            .distinctUntilChanged()
            .doOnNext(res -> System.out.println("response: " + res));
      }

      // Use this exact function to help ADK stop your streaming tools when requested.
      @Schema(description = "Stop the streaming")
      public static void stopStreaming(
          @Schema(name = "functionName", description = "The name of the streaming function to stop.") String functionName) {
        // Stop the streaming logic
      }

      public static void main(String[] args) {
        LlmAgent rootAgent = LlmAgent.builder()
            // Streaming tools run under runLive(), so the root agent needs a Live API
            // model. gemini-flash-latest is used above only for the one-shot
            // generateContent call inside the tool.
            .model("gemini-live-2.5-flash-native-audio")
            .name("video_streaming_agent")
            .instruction(
                "You are a monitoring agent. You can do video monitoring and stock price monitoring\n" +
                "using the provided tools/functions.\n" +
                "When users want to monitor a video stream,\n" +
                "You can use monitorVideoStream function to do that. When monitorVideoStream\n" +
                "returns the alert, you should tell the users.\n" +
                "When users want to monitor a stock price, you can use monitorStockPrice.\n" +
                "Don't ask too many questions. Don't be too talkative."
            )
            .tools(Arrays.asList(
                FunctionTool.create(StreamingTools.class, "monitorVideoStream"),
                FunctionTool.create(StreamingTools.class, "monitorStockPrice"),
                FunctionTool.create(StreamingTools.class, "stopStreaming")
            ))
            .build();
      }
    }
    ```

### Try it

Here are some sample queries to test:
- Help me monitor the stock price for $XYZ stock.
- Help me monitor how many people are there in the video stream.

## Non-blocking tools

When the wait has nothing worth narrating — a long analytics query, a batch export, a media
generation job — narrating it is the wrong behavior. An agent that keeps cutting in with
"still working!" is worse than one that quietly gets out of the way. Keep your plain
`return`-once tool and set `response_scheduling` to move it to the background:

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

The agent stays free while the tool runs, answers whatever else the user brings up, and folds
the result in when it is ready. A runnable example ships as the
[`live_non_blocking_tool_agent` sample](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_non_blocking_tool_agent).

!!! note "Requires Python 2.4+"

    `response_scheduling` was added in adk-python 2.4, and support is per model. See
    [Supported models](models.md#live-models).

`response_scheduling` also controls *when* a finished result reaches the user:

| Value | Behavior | Use it for |
|-------|----------|------------|
| `WHEN_IDLE` | Waits for a natural pause | Reports and lookups — the usual choice |
| `INTERRUPT` | Delivers immediately | Alarms, failures, "the transfer failed" |
| `SILENT` | Enters context, announced only if relevant | Background info the model may use later |

## Tool execution context

A tool or callback receives an `InvocationContext` for state, history, and artifacts. It
works the same as in any ADK agent — see [Agent context](../context/index.md) — with one
difference that matters live: **one `InvocationContext` spans the entire `run_live()` loop**,
created when you call `run_live()` and living across every agent and every turn until the
session ends. In a request/response agent an invocation is a single turn; in a live session
it is the whole conversation.

Two fields come up most in live tools:

| Field | What it gives you |
| :---- | :---- |
| `context.run_config` | The session's [configuration](configuration.md) — response modalities, transcription, limits |
| `context.end_invocation` | Set to `True` to terminate the whole streaming session immediately |
