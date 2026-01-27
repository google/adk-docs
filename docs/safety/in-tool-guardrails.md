## What are In-Tool Guardrails?

Tools can be designed with security in mind: we can create tools that expose the actions we want the model to take and nothing else. By limiting the range of actions we provide to the agents, we can deterministically eliminate classes of rogue actions that we never want the agent to take.

In-tool guardrails is an approach to create common and re-usable tools that expose deterministic controls that can be used by developers to set limits on each tool instantiation.

This approach relies on the fact that tools receive two types of input: arguments,  which are set by the model, and [**`Tool Context`**](../tools-custom/index.md#tool-context), which can be set deterministically by the agent developer. We can rely on the deterministically set information to validate that the model is behaving as-expected.

For example, a query tool can be designed to expect a policy to be read from the Tool Context.

## Code Examples

=== "Python"

    ```py
    # Conceptual example: Setting policy data intended for tool context
    # In a real ADK app, this might be set in InvocationContext.session.state
    # or passed during tool initialization, then retrieved via ToolContext.

    policy = {} # Assuming policy is a dictionary
    policy['select_only'] = True
    policy['tables'] = ['mytable1', 'mytable2']

    # Conceptual: Storing policy where the tool can access it via ToolContext later.
    # This specific line might look different in practice.
    # For example, storing in session state:
    invocation_context.session.state["query_tool_policy"] = policy

    # Or maybe passing during tool init:
    query_tool = QueryTool(policy=policy)
    # For this example, we'll assume it gets stored somewhere accessible.
    ```

=== "TypeScript"

    ```typescript
    // Conceptual example: Setting policy data intended for tool context
    // In a real ADK app, this might be set in InvocationContext.session.state
    // or passed during tool initialization, then retrieved via ToolContext.

    const policy: {[key: string]: any} = {}; // Assuming policy is an object
    policy['select_only'] = true;
    policy['tables'] = ['mytable1', 'mytable2'];

    // Conceptual: Storing policy where the tool can access it via ToolContext later.
    // This specific line might look different in practice.
    // For example, storing in session state:
    invocationContext.session.state["query_tool_policy"] = policy;

    // Or maybe passing during tool init:
    const queryTool = new QueryTool({policy: policy});
    // For this example, we'll assume it gets stored somewhere accessible.
    ```

=== "Go"

    ```go
    // Conceptual example: Setting policy data intended for tool context
    // In a real ADK app, this might be set using the session state service.
    // `ctx` is an `agent.Context` available in callbacks or custom agents.

    policy := map[string]interface{}{
    	"select_only": true,
    	"tables":      []string{"mytable1", "mytable2"},
    }

    // Conceptual: Storing policy where the tool can access it via ToolContext later.
    // This specific line might look different in practice.
    // For example, storing in session state:
    if err := ctx.Session().State().Set("query_tool_policy", policy); err != nil {
        // Handle error, e.g., log it.
    }

    // Or maybe passing during tool init:
    // queryTool := NewQueryTool(policy)
    // For this example, we'll assume it gets stored somewhere accessible.
    ```

=== "Java"

    ```java
    // Conceptual example: Setting policy data intended for tool context
    // In a real ADK app, this might be set in InvocationContext.session.state
    // or passed during tool initialization, then retrieved via ToolContext.

    policy = new HashMap<String, Object>(); // Assuming policy is a Map
    policy.put("select_only", true);
    policy.put("tables", new ArrayList<>("mytable1", "mytable2"));

    // Conceptual: Storing policy where the tool can access it via ToolContext later.
    // This specific line might look different in practice.
    // For example, storing in session state:
    invocationContext.session().state().put("query_tool_policy", policy);

    // Or maybe passing during tool init:
    query_tool = QueryTool(policy);
    // For this example, we'll assume it gets stored somewhere accessible.
    ```

During the tool execution, [**`Tool Context`**](../tools-custom/index.md#tool-context) will be passed to the tool:

=== "Python"

    ```py
    def query(query: str, tool_context: ToolContext) -> str | dict:
      # Assume 'policy' is retrieved from context, e.g., via session state:
      # policy = tool_context.invocation_context.session.state.get('query_tool_policy', {})

      # --- Placeholder Policy Enforcement ---
      policy = tool_context.invocation_context.session.state.get('query_tool_policy', {}) # Example retrieval
      actual_tables = explainQuery(query) # Hypothetical function call

      if not set(actual_tables).issubset(set(policy.get('tables', []))):
        # Return an error message for the model
        allowed = ", ".join(policy.get('tables', ['(None defined)']))
        return f"Error: Query targets unauthorized tables. Allowed: {allowed}"

      if policy.get('select_only', False):
           if not query.strip().upper().startswith("SELECT"):
               return "Error: Policy restricts queries to SELECT statements only."
      # --- End Policy Enforcement ---

      print(f"Executing validated query (hypothetical): {query}")
      return {"status": "success", "results": [...]} # Example successful return
    ```

=== "TypeScript"

    ```typescript
    function query(query: string, toolContext: ToolContext): string | object {
        // Assume 'policy' is retrieved from context, e.g., via session state:
        const policy = toolContext.state.get('query_tool_policy', {}) as {[key: string]: any};

        // --- Placeholder Policy Enforcement ---
        const actual_tables = explainQuery(query); // Hypothetical function call

        const policyTables = new Set(policy['tables'] || []);
        const isSubset = actual_tables.every(table => policyTables.has(table));

        if (!isSubset) {
            // Return an error message for the model
            const allowed = (policy['tables'] || ['(None defined)']).join(', ');
            return `Error: Query targets unauthorized tables. Allowed: ${allowed}`;
        }

        if (policy['select_only']) {
            if (!query.trim().toUpperCase().startsWith("SELECT")) {
                return "Error: Policy restricts queries to SELECT statements only.";
            }
        }
        // --- End Policy Enforcement ---

        console.log(`Executing validated query (hypothetical): ${query}`);
        return { "status": "success", "results": [] }; // Example successful return
    }
    ```

=== "Go"

    ```go
    import (
    	"fmt"
    	"strings"

    	"google.golang.org/adk/tool"
    )

    func query(query string, toolContext *tool.Context) (any, error) {
    	// Assume 'policy' is retrieved from context, e.g., via session state:
    	policyAny, err := toolContext.State().Get("query_tool_policy")
    	if err != nil {
    		return nil, fmt.Errorf("could not retrieve policy: %w", err)
    	}    	policy, _ := policyAny.(map[string]interface{})
    	actualTables := explainQuery(query) // Hypothetical function call

    	// --- Placeholder Policy Enforcement ---
    	if tables, ok := policy["tables"].([]string); ok {
    		if !isSubset(actualTables, tables) {
    			// Return an error to signal failure
    			allowed := strings.Join(tables, ", ")
    			if allowed == "" {
    				allowed = "(None defined)"
    			}
    			return nil, fmt.Errorf("query targets unauthorized tables. Allowed: %s", allowed)
    		}
    	}

    	if selectOnly, _ := policy["select_only"].(bool); selectOnly {
    		if !strings.HasPrefix(strings.ToUpper(strings.TrimSpace(query)), "SELECT") {
    			return nil, fmt.Errorf("policy restricts queries to SELECT statements only")
    		}
    	}
    	// --- End Policy Enforcement ---

    	fmt.Printf("Executing validated query (hypothetical): %s\n", query)
    	return map[string]interface{}{"status": "success", "results": []string{"..."}}, nil
    }

    // Helper function to check if a is a subset of b
    func isSubset(a, b []string) bool {
    	set := make(map[string]bool)
    	for _, item := range b {
    		set[item] = true
    	}
    	for _, item := range a {
    		if _, found := set[item]; !found {
    			return false
    		}
    	}
    	return true
    }
    ```

=== "Java"

    ```java

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
    ```
