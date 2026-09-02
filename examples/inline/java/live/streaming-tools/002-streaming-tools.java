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
        .model("gemini-flash-latest")
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