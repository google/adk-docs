# Safety and Security for AI Agents

Supported in ADKPythonTypeScriptGoJava

As AI agents grow in capability, ensuring they operate safely, securely, and align with your brand values is paramount. Uncontrolled agents can pose risks, including executing misaligned or harmful actions, such as data exfiltration, and generating inappropriate content that can impact your brand’s reputation. **Sources of risk include vague instructions, model hallucination, jailbreaks and prompt injections from adversarial users, and indirect prompt injections via tool use.**

[Google Cloud Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/overview) provides a multi-layered approach to mitigate these risks, enabling you to build powerful *and* trustworthy agents. It offers several mechanisms to establish strict boundaries, ensuring agents only perform actions you've explicitly allowed:

1. **Identity and Authorization**: Control who the agent **acts as** by defining agent and user auth.

1. **Guardrails to screen inputs and outputs:** Control your model and tool calls precisely.

   - *In-Tool Guardrails:* Design tools defensively, using developer-set tool context to enforce policies (e.g., allowing queries only on specific tables).
   - *Built-in Gemini Safety Features:* If using Gemini models, benefit from content filters to block harmful outputs and system Instructions to guide the model's behavior and safety guidelines
   - *Callbacks and Plugins:* Validate model and tool calls before or after execution, checking parameters against agent state or external policies.
   - *Using Gemini as a safety guardrail:* Implement an additional safety layer using a cheap and fast model (like Gemini Flash Lite) configured via callbacks to screen inputs and outputs.

1. **Sandboxed code execution:** Prevent model-generated code to cause security issues by sandboxing the environment

1. **Evaluation and tracing**: Use evaluation tools to assess the quality, relevance, and correctness of the agent's final output. Use tracing to gain visibility into agent actions to analyze the steps an agent takes to reach a solution, including its choice of tools, strategies, and the efficiency of its approach.

1. **Network Controls and VPC-SC:** Confine agent activity within secure perimeters (like VPC Service Controls) to prevent data exfiltration and limit the potential impact radius.

## Safety and Security Risks

Before implementing safety measures, perform a thorough risk assessment specific to your agent's capabilities, domain, and deployment context.

***Sources*** **of risk** include:

- Ambiguous agent instructions
- Prompt injection and jailbreak attempts from adversarial users
- Indirect prompt injections via tool use

**Risk categories** include:

- **Misalignment & goal corruption**
  - Pursuing unintended or proxy goals that lead to harmful outcomes ("reward hacking")
  - Misinterpreting complex or ambiguous instructions
- **Harmful content generation, including brand safety**
  - Generating toxic, hateful, biased, sexually explicit, discriminatory, or illegal content
  - Brand safety risks such as Using language that goes against the brand’s values or off-topic conversations
- **Unsafe actions**
  - Executing commands that damage systems
  - Making unauthorized purchases or financial transactions.
  - Leaking sensitive personal data (PII)
  - Data exfiltration

## Best practices

### Identity and Authorization

The identity that a *tool* uses to perform actions on external systems is a crucial design consideration from a security perspective. Different tools in the same agent can be configured with different strategies, so care is needed when talking about the agent's configurations.

#### Agent-Auth

The **tool interacts with external systems using the agent's own identity** (e.g., a service account). The agent identity must be explicitly authorized in the external system access policies, like adding an agent's service account to a database's IAM policy for read access. Such policies constrain the agent in only performing actions that the developer intended as possible: by giving read-only permissions to a resource, no matter what the model decides, the tool will be prohibited from performing write actions.

This approach is simple to implement, and it is **appropriate for agents where all users share the same level of access.** If not all users have the same level of access, such an approach alone doesn't provide enough protection and must be complemented with other techniques below. In tool implementation, ensure that logs are created to maintain attribution of actions to users, as all agents' actions will appear as coming from the agent.

#### User Auth

The tool interacts with an external system using the **identity of the "controlling user"** (e.g., the human interacting with the frontend in a web application). In ADK, this is typically implemented using OAuth: the agent interacts with the frontend to acquire a OAuth token, and then the tool uses the token when performing external actions: the external system authorizes the action if the controlling user is authorized to perform it on its own.

User auth has the advantage that agents only perform actions that the user could have performed themselves. This greatly reduces the risk that a malicious user could abuse the agent to obtain access to additional data. However, most common implementations of delegation have a fixed set permissions to delegate (i.e., OAuth scopes). Often, such scopes are broader than the access that the agent actually requires, and the techniques below are required to further constrain agent actions.

### Guardrails to screen inputs and outputs

#### In-tool guardrails

Tools can be designed with security in mind: we can create tools that expose the actions we want the model to take and nothing else. By limiting the range of actions we provide to the agents, we can deterministically eliminate classes of rogue actions that we never want the agent to take.

In-tool guardrails is an approach to create common and re-usable tools that expose deterministic controls that can be used by developers to set limits on each tool instantiation.

This approach relies on the fact that tools receive two types of input: arguments, which are set by the model, and [**`Tool Context`**](https://google.github.io/adk-docs/tools-custom/#tool-context), which can be set deterministically by the agent developer. We can rely on the deterministically set information to validate that the model is behaving as-expected.

For example, a query tool can be designed to expect a policy to be read from the Tool Context.

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

During the tool execution, [**`Tool Context`**](https://google.github.io/adk-docs/tools-custom/#tool-context) will be passed to the tool:

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
    }       policy, _ := policyAny.(map[string]interface{})
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

#### Built-in Gemini Safety Features

Gemini models come with in-built safety mechanisms that can be leveraged to improve content and brand safety.

- **Content safety filters**: [Content filters](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/configure-safety-attributes) can help block the output of harmful content. They function independently from Gemini models as part of a layered defense against threat actors who attempt to jailbreak the model. Gemini models on Vertex AI use two types of content filters:
- **Non-configurable safety filters** automatically block outputs containing prohibited content, such as child sexual abuse material (CSAM) and personally identifiable information (PII).
- **Configurable content filters** allow you to define blocking thresholds in four harm categories (hate speech, harassment, sexually explicit, and dangerous content,) based on probability and severity scores. These filters are default off but you can configure them according to your needs.
- **System instructions for safety**: [System instructions](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/safety-system-instructions) for Gemini models in Vertex AI provide direct guidance to the model on how to behave and what type of content to generate. By providing specific instructions, you can proactively steer the model away from generating undesirable content to meet your organization’s unique needs. You can craft system instructions to define content safety guidelines, such as prohibited and sensitive topics, and disclaimer language, as well as brand safety guidelines to ensure the model's outputs align with your brand's voice, tone, values, and target audience.

While these measures are robust against content safety, you need additional checks to reduce agent misalignment, unsafe actions, and brand safety risks.

#### Callbacks and Plugins for Security Guardrails

Callbacks provide a simple, agent-specific method for adding pre-validation to tool and model I/O, whereas plugins offer a reusable solution for implementing general security policies across multiple agents.

When modifications to the tools to add guardrails aren't possible, the [**`Before Tool Callback`**](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#before-tool-callback) function can be used to add pre-validation of calls. The callback has access to the agent's state, the requested tool and parameters. This approach is very general and can even be created to create a common library of re-usable tool policies. However, it might not be applicable for all tools if the information to enforce the guardrails isn't directly visible in the parameters.

```py
# Hypothetical callback function
def validate_tool_params(
    callback_context: CallbackContext, # Correct context type
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
    ) -> Optional[Dict]: # Correct return type for before_tool_callback

  print(f"Callback triggered for tool: {tool.name}, args: {args}")

  # Example validation: Check if a required user ID from state matches an arg
  expected_user_id = callback_context.state.get("session_user_id")
  actual_user_id_in_args = args.get("user_id_param") # Assuming tool takes 'user_id_param'

  if actual_user_id_in_args != expected_user_id:
      print("Validation Failed: User ID mismatch!")
      # Return a dictionary to prevent tool execution and provide feedback
      return {"error": f"Tool call blocked: User ID mismatch."}

  # Return None to allow the tool call to proceed if validation passes
  print("Callback validation passed.")
  return None

# Hypothetical Agent setup
root_agent = LlmAgent( # Use specific agent type
    model='gemini-2.0-flash',
    name='root_agent',
    instruction="...",
    before_tool_callback=validate_tool_params, # Assign the callback
    tools = [
      # ... list of tool functions or Tool instances ...
      # e.g., query_tool_instance
    ]
)
```

```typescript
// Hypothetical callback function
function validateToolParams(
    {tool, args, context}: {
        tool: BaseTool,
        args: {[key: string]: any},
        context: ToolContext
    }
): {[key: string]: any} | undefined {
    console.log(`Callback triggered for tool: ${tool.name}, args: ${JSON.stringify(args)}`);

    // Example validation: Check if a required user ID from state matches an arg
    const expectedUserId = context.state.get("session_user_id");
    const actualUserIdInArgs = args["user_id_param"]; // Assuming tool takes 'user_id_param'

    if (actualUserIdInArgs !== expectedUserId) {
        console.log("Validation Failed: User ID mismatch!");
        // Return a dictionary to prevent tool execution and provide feedback
        return {"error": `Tool call blocked: User ID mismatch.`};
    }

    // Return undefined to allow the tool call to proceed if validation passes
    console.log("Callback validation passed.");
    return undefined;
}

// Hypothetical Agent setup
const rootAgent = new LlmAgent({
    model: 'gemini-2.5-flash',
    name: 'root_agent',
    instruction: "...",
    beforeToolCallback: validateToolParams, // Assign the callback
    tools: [
      // ... list of tool functions or Tool instances ...
      // e.g., queryToolInstance
    ]
});
```

```go
import (
    "fmt"
    "reflect"

    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/tool"
)

// Hypothetical callback function
func validateToolParams(
    ctx tool.Context,
    t tool.Tool,
    args map[string]any,
) (map[string]any, error) {
    fmt.Printf("Callback triggered for tool: %s, args: %v\n", t.Name(), args)

    // Example validation: Check if a required user ID from state matches an arg
    expectedUserID, err := ctx.State().Get("session_user_id")
    if err != nil {
        // This is an unexpected failure, return an error.
        return nil, fmt.Errorf("internal error: session_user_id not found in state: %w", err)
    }
            expectedUserID, ok := expectedUserIDVal.(string)
    if !ok {
        return nil, fmt.Errorf("internal error: session_user_id in state is not a string, got %T", expectedUserIDVal)
    }

    actualUserIDInArgs, exists := args["user_id_param"]
    if !exists {
        // Handle case where user_id_param is not in args
        fmt.Println("Validation Failed: user_id_param missing from arguments!")
        return map[string]any{"error": "Tool call blocked: user_id_param missing from arguments."}, nil
    }

    actualUserID, ok := actualUserIDInArgs.(string)
    if !ok {
        // Handle case where user_id_param is not a string
        fmt.Println("Validation Failed: user_id_param is not a string!")
        return map[string]any{"error": "Tool call blocked: user_id_param is not a string."}, nil
    }

    if actualUserID != expectedUserID {
        fmt.Println("Validation Failed: User ID mismatch!")
        // Return a map to prevent tool execution and provide feedback to the model.
        // This is not a Go error, but a message for the agent.
        return map[string]any{"error": "Tool call blocked: User ID mismatch."}, nil
    }
    // Return nil, nil to allow the tool call to proceed if validation passes
    fmt.Println("Callback validation passed.")
    return nil, nil
}

// Hypothetical Agent setup
// rootAgent, err := llmagent.New(llmagent.Config{
//  Model: "gemini-2.0-flash",
//  Name: "root_agent",
//  Instruction: "...",
//  BeforeToolCallbacks: []llmagent.BeforeToolCallback{validateToolParams},
//  Tools: []tool.Tool{queryToolInstance},
// })
```

```java
// Hypothetical callback function
public Optional<Map<String, Object>> validateToolParams(
  CallbackContext callbackContext,
  Tool baseTool,
  Map<String, Object> input,
  ToolContext toolContext) {

System.out.printf("Callback triggered for tool: %s, Args: %s", baseTool.name(), input);

// Example validation: Check if a required user ID from state matches an input parameter
Object expectedUserId = callbackContext.state().get("session_user_id");
Object actualUserIdInput = input.get("user_id_param"); // Assuming tool takes 'user_id_param'

if (!actualUserIdInput.equals(expectedUserId)) {
  System.out.println("Validation Failed: User ID mismatch!");
  // Return to prevent tool execution and provide feedback
  return Optional.of(Map.of("error", "Tool call blocked: User ID mismatch."));
}

// Return to allow the tool call to proceed if validation passes
System.out.println("Callback validation passed.");
return Optional.empty();
}

// Hypothetical Agent setup
public void runAgent() {
LlmAgent agent =
    LlmAgent.builder()
        .model("gemini-2.0-flash")
        .name("AgentWithBeforeToolCallback")
        .instruction("...")
        .beforeToolCallback(this::validateToolParams) // Assign the callback
        .tools(anyToolToUse) // Define the tool to be used
        .build();
}
```

However, when adding security guardrails to your agent applications, plugins are the recommended approach for implementing policies that are not specific to a single agent. Plugins are designed to be self-contained and modular, allowing you to create individual plugins for specific security policies, and apply them globally at the runner level. This means that a security plugin can be configured once and applied to every agent that uses the runner, ensuring consistent security guardrails across your entire application without repetitive code.

Some examples include:

- **Gemini as a Judge Plugin**: This plugin uses Gemini Flash Lite to evaluate user inputs, tool input and output, and agent's response for appropriateness, prompt injection, and jailbreak detection. The plugin configures Gemini to act as a safety filter to mitigate against content safety, brand safety, and agent misalignment. The plugin is configured to pass user input, tool input and output, and model output to Gemini Flash Lite, who decides if the input to the agent is safe or unsafe. If Gemini decides the input is unsafe, the agent returns a predetermined response: "Sorry I cannot help with that. Can I help you with something else?".
- **Model Armor Plugin**: A plugin that queries the model armor API to check for potential content safety violations at specified points of agent execution. Similar to the *Gemini as a Judge* plugin, if Model Armor finds matches of harmful content, it returns a predetermined response to the user.
- **PII Redaction Plugin**: A specialized plugin with design for the [Before Tool Callback](/adk-docs/plugins/#tool-callbacks) and specifically created to redact personally identifiable information before it’s processed by a tool or sent to an external service.

### Sandboxed Code Execution

Code execution is a special tool that has extra security implications: sandboxing must be used to prevent model-generated code to compromise the local environment, potentially creating security issues.

Google and the ADK provide several options for safe code execution. [Vertex Gemini Enterprise API code execution feature](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/code-execution-api) enables agents to take advantage of sandboxed code execution server-side by enabling the tool_execution tool. For code performing data analysis, you can use the [Code Executor](/adk-docs/tools/gemini-api/code-execution/) tool in ADK to call the [Vertex Code Interpreter Extension](https://cloud.google.com/vertex-ai/generative-ai/docs/extensions/code-interpreter).

If none of these options satisfy your requirements, you can build your own code executor using the building blocks provided by the ADK. We recommend creating execution environments that are hermetic: no network connections and API calls permitted to avoid uncontrolled data exfiltration; and full clean up of data across execution to not create cross-user exfiltration concerns.

### Evaluations

See [Evaluate Agents](https://google.github.io/adk-docs/evaluate/index.md).

### VPC-SC Perimeters and Network Controls

If you are executing your agent into a VPC-SC perimeter, that will guarantee that all API calls will only be manipulating resources within the perimeter, reducing the chance of data exfiltration.

However, identity and perimeters only provide coarse controls around agent actions. Tool-use guardrails mitigate such limitations, and give more power to agent developers to finely control which actions to allow.

### Other Security Risks

#### Always Escape Model-Generated Content in UIs

Care must be taken when agent output is visualized in a browser: if HTML or JS content isn't properly escaped in the UI, the text returned by the model could be executed, leading to data exfiltration. For example, an indirect prompt injection can trick a model to include an img tag tricking the browser to send the session content to a 3rd party site; or construct URLs that, if clicked, send data to external sites. Proper escaping of such content must ensure that model-generated text isn't interpreted as code by browsers.
