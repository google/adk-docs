// Example: Tool using memory search
import com.google.adk.tools.ToolContext;
import com.google.adk.memory.SearchMemoryResponse;
import io.reactivex.rxjava3.core.Single;
import java.util.Map;

public class MemorySearchTool {
  public Single<Map<String, String>> findRelatedInfo(ToolContext context, String topic) {
    return context.searchMemory("Information about " + topic)
        .map(searchResults -> {
          if (searchResults != null && searchResults.results() != null && !searchResults.results().isEmpty()) {
            System.out.println("Found " + searchResults.results().size() + " memory results for '" + topic + "'");
            // Process searchResults.results
            String topResultText = searchResults.results().get(0).text();
            return Map.of("memory_snippet", topResultText);
          } else {
            return Map.of("message", "No relevant memories found.");
          }
        })
        .onErrorReturnItem(Map.of("error", "Memory service error"));
  }
}