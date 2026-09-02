import com.google.adk.tools.ToolContext;
import java.util.*;

class ToolContextQuery {

  public Object query(String query, ToolContext toolContext) {

    // Assume 'policy' is retrieved from context, e.g., via session state:
    Map<String, Object> queryToolPolicy =
        toolContext.invocationContext.session().state().getOrDefault("query_tool_policy", null);
    List<String> actualTables = explainQuery(query);

    // --- Placeholder Policy Enforcement ---
    if (!queryToolPolicy.get("tables").containsAll(actualTables)) {
      List<String> allowedPolicyTables =
          (List<String>) queryToolPolicy.getOrDefault("tables", new ArrayList<String>());

      String allowedTablesString =
          allowedPolicyTables.isEmpty() ? "(None defined)" : String.join(", ", allowedPolicyTables);

      return String.format(
          "Error: Query targets unauthorized tables. Allowed: %s", allowedTablesString);
    }

    if (!queryToolPolicy.get("select_only")) {
      if (!query.trim().toUpperCase().startswith("SELECT")) {
        return "Error: Policy restricts queries to SELECT statements only.";
      }
    }
    // --- End Policy Enforcement ---

    System.out.printf("Executing validated query (hypothetical) %s:", query);
    Map<String, Object> successResult = new HashMap<>();
    successResult.put("status", "success");
    successResult.put("results", Arrays.asList("result_item1", "result_item2"));
    return successResult;
  }
}