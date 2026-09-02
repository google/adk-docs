package adk.plugins.agentanalytics.demo;

import static java.nio.charset.StandardCharsets.UTF_8;
import static java.util.Collections.singletonList;

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.events.Event;
import com.google.adk.models.Gemini;
import com.google.adk.plugins.Plugin;
import com.google.adk.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin;
import com.google.adk.plugins.agentanalytics.BigQueryLoggerConfig;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;
import com.google.genai.types.Content;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.Part;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.common.CompletableResultCode;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.data.SpanData;
import io.opentelemetry.sdk.trace.export.SimpleSpanProcessor;
import io.opentelemetry.sdk.trace.export.SpanExporter;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Collection;
import java.util.Scanner;

/** Demo agent showing how to use BigQueryAgentAnalyticsPlugin. */
public final class BqDemoAgent {
  private static final String PROJECT_ID = "your-gcp-project-id";
  private static final String DATASET_ID = "your-gcp-dataset_id";
  private static final String TABLE_ID = "your-gcp-table";
  private static final String GCS_BUCKET_NAME = "your-gcs-bucket-name";
  private static final String API_KEY = "your-api_key";

  // A simple tool to demonstrate tool execution logging
  public static String reverseString(String input, ToolContext toolContext) {
    return new StringBuilder(input).reverse().toString();
  }

  public static void main(String[] args) throws Exception {
    // 0. Initialize OpenTelemetry
    initOpenTelemetry();

    // 1. Configure the BigQuery Logger
    BigQueryLoggerConfig config =
        BigQueryLoggerConfig.builder()
            .projectId(PROJECT_ID)
            .datasetId(DATASET_ID)
            .tableName(TABLE_ID)
            .gcsBucketName(GCS_BUCKET_NAME)
            .createViews(true)
            .build();

    // 2. Create the plugin instance
    Plugin bqLoggingPlugin = new BigQueryAgentAnalyticsPlugin(config);

    // 3. Initialize the model (Gemini)
    Gemini model =
        Gemini.builder()
            .modelName("gemini-3-flash-preview") // Use appropriate model
            .apiKey(API_KEY)
            .build();

    // 4. Create the agent with the tool and plugin
    LlmAgent agent =
        LlmAgent.builder()
            .model(model)
            .name("bq_demo_agent")
            .instruction(
                "You are a helpful assistant. You have a tool 'reverseString' that you can use to"
                    + " reverse text.")
            .tools(FunctionTool.create(BqDemoAgent.class, "reverseString"))
            .generateContentConfig(GenerateContentConfig.builder().temperature(0.5f).build())
            .build();

    // 5. Initialize the runner
    InMemoryRunner runner =
        new InMemoryRunner(agent, "bq_demo_agent", singletonList(bqLoggingPlugin));

    // 6. Create a session
    Session session =
        runner.sessionService().createSession(runner.appName(), "demo_user").blockingGet();

    RunConfig runConfig = RunConfig.builder().build();

    System.out.println("Agent ready. Type 'quit' to exit.");

    try (Scanner scanner = new Scanner(System.in, UTF_8)) {
      while (true) {
        System.out.print("\nUser: ");
        String userInput = scanner.nextLine();
        if (userInput.trim().equalsIgnoreCase("quit")) {
          break;
        }

        Content userMsg = Content.fromParts(Part.fromText(userInput));

        // Run the agent and stream events
        Flowable<Event> events =
            runner.runAsync(session.userId(), session.id(), userMsg, runConfig);

        System.out.print("Agent: ");
        events.blockingForEach(
            event -> {
              if (event.finalResponse()) {
                System.out.println(event.stringifyContent());
              }
            });
      }
    } finally {
      System.out.println("Closing runner (flushing remaining logs)...");
      runner.close().blockingAwait();
      System.out.println("Done.");
    }
  }

  private static void initOpenTelemetry() {
    PrintingSpanExporter exporter = new PrintingSpanExporter();
    SdkTracerProvider tracerProvider =
        SdkTracerProvider.builder().addSpanProcessor(SimpleSpanProcessor.create(exporter)).build();
    OpenTelemetrySdk.builder().setTracerProvider(tracerProvider).buildAndRegisterGlobal();
  }

  private static class PrintingSpanExporter implements SpanExporter {
    @Override
    public CompletableResultCode export(Collection<SpanData> spans) {
      for (SpanData span : spans) {
        System.out.println("--- Span: " + span.getName() + " ---");
        System.out.println("  TraceId: " + span.getTraceId());
        System.out.println("  SpanId: " + span.getSpanId());
        System.out.println("  ParentSpanId: " + span.getParentSpanId());
        System.out.println("  Attributes: " + span.getAttributes());
        System.out.println("------------------------");
      }
      return CompletableResultCode.ofSuccess();
    }

    @Override
    public CompletableResultCode flush() {
      return CompletableResultCode.ofSuccess();
    }

    @Override
    public CompletableResultCode shutdown() {
      return CompletableResultCode.ofSuccess();
    }
  }

  private BqDemoAgent() {}
}