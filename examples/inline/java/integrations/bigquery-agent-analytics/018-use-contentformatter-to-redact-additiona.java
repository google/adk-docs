import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Gemini;
import com.google.adk.models.LlmRequest;
import com.google.adk.models.LlmResponse;
import com.google.adk.runner.Runner;
import com.google.genai.types.Content;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.Part;
import java.util.ArrayList;
import java.util.List;

public final class AgentContentFormatter {
  private static final String PROJECT_ID = "your-gcp-project-id";
  private static final String DATASET_ID = "your-gcp-dataset_id";
  private static final String TABLE_ID = "your-gcp-table";
  private static final String API_KEY = "your-api_key";
  private static final String GCS_BUCKET_NAME = "your-gcs-bucket-name";

  /** Returns the formatter logic you want to test. */
  private static Object formatter(Object content, String eventType) {
    if (content instanceof LlmRequest req) {
      List<Content> maskedContents = new ArrayList<>();
      for (Content c : req.contents()) {
        maskedContents.add(maskContent(c));
      }
      return req.toBuilder().contents(maskedContents).build();
    } else if (content instanceof LlmResponse res) {
      if (res.content().isPresent()) {
        return res.toBuilder().content(maskContent(res.content().get())).build();
      }
      return res;
    } else if (content instanceof Content content2) {
      return maskContent(content2);
    } else if (content instanceof Map<?, ?> map) {
      Map<Object, Object> maskedMap = new LinkedHashMap<>();
      for (Map.Entry<?, ?> entry : map.entrySet()) {
        maskedMap.put(entry.getKey(), formatter(entry.getValue(), eventType));
      }
      return maskedMap;
    }
    return content;
  }

  private static Content maskContent(Content originalContent) {
    if (originalContent.parts().isPresent()) {
      List<Part> maskedParts = new ArrayList<>();
      for (Part part : originalContent.parts().get()) {
        if (part.text().isPresent() && part.text().get().contains("secret")) {
          String maskedText = part.text().get().replace("secret", "****");
          maskedParts.add(part.toBuilder().text(maskedText).build());
        } else {
          maskedParts.add(part);
        }
      }
      return originalContent.toBuilder().parts(maskedParts).build();
    }
    return originalContent;
  }

  public static void main(String[] args) throws Exception {
    // 1. Setup Config with custom formatter
    BigQueryLoggerConfig config =
        BigQueryLoggerConfig.builder()
            .projectId(PROJECT_ID)
            .datasetId(DATASET_ID)
            .tableName(TABLE_ID)
            .gcsBucketName(GCS_BUCKET_NAME)
            .contentFormatter(AgentContentFormatter::formatter)
            .logMultiModalContent(true)
            .build();

    // 2. Setup Plugin
    BigQueryAgentAnalyticsPlugin plugin = new BigQueryAgentAnalyticsPlugin(config);

    // 3. Setup Agent that responds
    LlmAgent agent =
        LlmAgent.builder()
            .model(
                Gemini.builder()
                    .modelName("gemini-3-flash-preview") // use appropriate model
                    .apiKey(API_KEY)
                    .build())
            .name("bq_demo_agent")
            .instruction("You are a helpful assistant")
            .generateContentConfig(GenerateContentConfig.builder().temperature(0.5f).build())
            .build();

    // 4. Setup Runner
    Runner runner = Runner.builder().agent(agent).appName("test_app").plugins(plugin).build();
    // 5. Use runner to run some scenarios
    ...
  }

  private AgentContentFormatter() {}
}