# Tools

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-preview">Experimental</span>
</div>

Tools work in a live agent much as they do anywhere else in ADK — you pass functions to
an agent and the model calls them. Two things are different. ADK executes tool calls for
you inside the `run_live()` loop, so you never write the function-call plumbing the raw
Live API would require. And live agents can use *streaming tools*: functions that stay
running and push intermediate results back to the agent, so the agent can react to a
stock price moving or a person appearing in a video frame without the user asking again.

## Automatic Tool Execution in run_live()

!!! note "Source Reference"

    See automatic tool execution implementation in [`functions.py`](https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/flows/llm_flows/functions.py)

One of the most powerful features of ADK's `run_live()` is **automatic tool execution**. Unlike the raw Gemini Live API, which requires you to manually handle tool calls and responses, ADK abstracts this complexity entirely.

### The Challenge with Raw Live API

When using the Gemini Live API directly (without ADK), tool use requires manual orchestration:

1. **Receive** function calls from the model
2. **Execute** the tools yourself
3. **Format** function responses correctly
4. **Send** responses back to the model

This creates significant implementation overhead, especially in streaming contexts where you need to handle multiple concurrent tool calls, manage errors, and coordinate with ongoing audio/text streams.

### How ADK Simplifies Tool Use

With ADK, tool execution becomes declarative. Simply define tools on your Agent:

```python
import os
from google.adk.agents import Agent
from google.adk.tools import google_search

agent = Agent(
    name="google_search_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[google_search],
    instruction="You are a helpful assistant that can search the web."
)
```

When you call `runner.run_live()`, ADK automatically:

- **Detects** when the model returns function calls in streaming responses
- **Executes** tools in parallel for maximum performance
- **Handles** before/after tool callbacks for custom logic
- **Formats** function responses according to Live API requirements
- **Sends** responses back to the model seamlessly
- **Yields** both function call and response events to your application

### Tool Execution Events

When tools execute, you'll receive events through the `run_live()` async generator:

**Usage:**

```python
async for event in runner.run_live(...):
    # Function call event - model requesting tool execution
    if event.get_function_calls():
        print(f"Model calling: {event.get_function_calls()[0].name}")

    # Function response event - tool execution result
    if event.get_function_responses():
        print(f"Tool result: {event.get_function_responses()[0].response}")
```

You don't need to handle the execution yourself—ADK does it automatically. You just observe the events as they flow through the conversation.

!!! note "Learn More"

    In a web app, you can send all events (including function calls and responses) directly to the WebSocket client without server-side filtering. This allows the client to observe tool execution in real-time through the event stream.

### Long-Running and Streaming Tools

ADK supports advanced tool patterns that integrate seamlessly with `run_live()`:

**Long-Running Tools**: Tools that require human approval or take extended time to complete. Mark them with `is_long_running=True`. In resumable async flows, ADK can pause after long-running calls. In live flows, streaming continues; `long_running_tool_ids` indicate pending operations and clients can display appropriate UI.

**Streaming Tools**: Tools that accept an `input_stream` parameter with type `LiveRequestQueue` can send real-time updates back to the model during execution, enabling progressive responses.

!!! note "How Streaming Tools Work"

    Streaming tools are registered **lazily** — ADK does not scan your agent's tools up
    front. Registration happens the first time the model actually calls the tool.

    **Queue creation and lifecycle**:

    1. **Registration**: When the model calls an async-generator tool, ADK starts a task for
       it and records an `ActiveStreamingTool` in
       `invocation_context.active_streaming_tools[tool_name]`
    2. **Queue creation**: If — and only if — the tool's signature has an `input_stream`
       parameter annotated as `LiveRequestQueue`, ADK creates a dedicated `LiveRequestQueue`
       and assigns it to `active_streaming_tools[tool_name].stream`. This is also what makes
       ADK start duplicating the user's realtime input into that queue
    3. **Injection**: `FunctionTool` passes that queue in as the `input_stream` argument when
       it invokes the tool
    4. **Usage**: The tool can `yield` from inside its loop to send real-time updates back to
       the model during execution
    5. **Teardown**: A `stop_streaming` call cancels the task and resets both `.task` and
       `.stream` to `None`, so a later re-invocation gets a fresh queue. Otherwise the queues
       live for the whole `run_live()` invocation (one `InvocationContext` = one `run_live()`
       call)

    **Queue distinction**:

    - **Main queue** (`live_request_queue` parameter): Created by your application, used for client-to-model communication
    - **Tool queues** (`active_streaming_tools[tool_name].stream`): Created automatically by ADK, used for tool-to-model communication during execution

    Both types of queues are `LiveRequestQueue` instances, but they serve different purposes in the streaming architecture.

    This enables tools to provide incremental updates, progress notifications, or partial results during long-running operations.

    **Code reference**: [`functions.py:1109-1138`](https://github.com/google/adk-python/blob/c5672030b7b9c76967a18665120c8ac36e5c7fef/src/google/adk/flows/llm_flows/functions.py#L1109-L1138) (lazy registration and queue creation), [`functions.py:1019-1073`](https://github.com/google/adk-python/blob/c5672030b7b9c76967a18665120c8ac36e5c7fef/src/google/adk/flows/llm_flows/functions.py#L1019-L1073) (`stop_streaming`), and [`function_tool.py:378-387`](https://github.com/google/adk-python/blob/c5672030b7b9c76967a18665120c8ac36e5c7fef/src/google/adk/tools/function_tool.py#L378-L387) (parameter injection).

    See the [Tools Guide](/integrations/) for implementation examples.

### Key Takeaway

The difference between raw Live API tool use and ADK is stark:

| Aspect | Raw Live API | ADK `run_live()` |
|--------|--------------|------------------|
| **Tool Declaration** | Manual schema definition | Automatic from Python functions |
| **Tool Execution** | Manual handling in app code | Automatic parallel execution |
| **Response Formatting** | Manual JSON construction | Automatic |
| **Error Handling** | Manual try/catch and formatting | Automatic capture and reporting |
| **Streaming Integration** | Manual coordination | Automatic event yielding |
| **Developer Experience** | Complex, error-prone | Declarative, simple |

This automatic handling is one of the core value propositions of ADK—it transforms the complexity of Live API tool use into a simple, declarative developer experience.


## Streaming tools

Streaming tools allows tools(functions) to stream intermediate results back to agents and agents can respond to those intermediate results. 
For example, we can use streaming tools to monitor the changes of the stock price and have the agent react to it. Another example is we can have the agent monitor the video stream, and when there is changes in video stream, the agent can report the changes.

!!! info

    This is only supported in ADK Gemini Live APIs.

### Define a streaming tool

To define a streaming tool, you must adhere to the following:

1.  **Asynchronous Function:** The tool must be an `async` Python function.
2.  **AsyncGenerator Return Type:** The function must be typed to return an `AsyncGenerator`. The first type parameter to `AsyncGenerator` is the type of the data you `yield` (e.g., `str` for text messages, or a custom object for structured data). The second type parameter is typically `None` if the generator doesn't receive values via `send()`.


We support two types of streaming tools:
- Simple type. This is a one type of streaming tools that only take non-video/-audio streams(the streams that you feed to adk web or adk runner) as input.
- Video streaming tools. This only works in video streaming and the video stream(the streams that you feed to adk web or adk runner) will be passed into this function.

Now let's define an agent that can monitor stock price changes and monitor the video stream changes. 

### Example: monitoring a stock price and a video stream

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
      """This function will monitor the price for the given stock_symbol in a continuous, streaming and asynchronously way."""
      print(f"Start monitor stock price for {stock_symbol}!")

      # Let's mock stock price change.
      await asyncio.sleep(4)
      price_alert1 = f"the price for {stock_symbol} is 300"
      yield price_alert1
      print(price_alert1)

      await asyncio.sleep(4)
      price_alert1 = f"the price for {stock_symbol} is 400"
      yield price_alert1
      print(price_alert1)

      await asyncio.sleep(20)
      price_alert1 = f"the price for {stock_symbol} is 900"
      yield price_alert1
      print(price_alert1)

      await asyncio.sleep(20)
      price_alert1 = f"the price for {stock_symbol} is 500"
      yield price_alert1
      print(price_alert1)


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
        model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
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
            .model("gemini-2.5-flash-native-audio-preview-12-2025")
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

## Tool execution context

When you implement a custom tool or callback, ADK passes you an `InvocationContext` —
the state carrier for the current invocation. One `InvocationContext` corresponds to one
`run_live()` loop: it is created when you call `run_live()` and lives for the whole
streaming session, across every agent and every turn in it.

`InvocationContext` is not specific to live agents. For what an invocation is, how it
relates to agent calls and steps, and the full field reference, see
[Agent context](../context/index.md). The fields that matter most when writing a tool for
a live agent are:

| Field | What it gives you |
| :---- | :---- |
| `context.invocation_id` | Identifier for the current invocation, unique per `run_live()` call |
| `context.session.events` | Every event in the session history, across all invocations |
| `context.session.state` | Persistent key-value store that outlives the streaming session |
| `context.session.user_id` | User identity |
| `context.run_config` | The session's [configuration](configuration.md) — response modalities, transcription, cost limits |
| `context.end_invocation` | Set to `True` to terminate the conversation immediately |

```python
def my_tool(context: InvocationContext, query: str):
    # Identify the user and check whether this is their first message
    user_id = context.session.user_id
    if len(context.session.events) == 0:
        return "Welcome! This is your first message."

    # Read recent history and persistent state
    recent_events = context.session.events[-5:]
    user_preferences = context.session.state.get('user_preferences', {})

    # Writes to session state are persisted beyond this streaming session
    context.session.state['last_query_time'] = datetime.now().isoformat()

    result = process_query(query, context=recent_events, preferences=user_preferences)

    # Stop the conversation on an unrecoverable error
    if result.get('error'):
        context.end_invocation = True

    return result
```

!!! note "Storing large artifacts"

    To persist audio, images, or other binary output produced by a tool, use
    `context.artifact_service.save_artifact()` rather than session state. See
    [Artifacts](../artifacts/index.md).
