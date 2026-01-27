# Security Callbacks and Plugins

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

Callbacks provide a simple, agent-specific method for adding pre-validation to tool and model I/O, whereas plugins offer a reusable solution for implementing general security policies across multiple agents.

When modifications to the tools to add guardrails aren't possible, the [**`Before Tool Callback`**](../callbacks/types-of-callbacks.md#before-tool-callback) function can be used to add pre-validation of calls. The callback has access to the agent's state, the requested tool and parameters. This approach is very general and can even be created to create a common library of re-usable tool policies. However, it might not be applicable for all tools if the information to enforce the guardrails isn't directly visible in the parameters.

## Code Examples

=== "Python"

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

=== "TypeScript"

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

=== "Go"

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
    // 	Model: "gemini-2.0-flash",
    // 	Name: "root_agent",
    // 	Instruction: "...",
    // 	BeforeToolCallbacks: []llmagent.BeforeToolCallback{validateToolParams},
    // 	Tools: []tool.Tool{queryToolInstance},
    // })
    ```

=== "Java"

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

* **Gemini as a Judge Plugin**: This plugin uses Gemini Flash Lite to evaluate user inputs, tool input and output, and agent's response for appropriateness, prompt injection, and jailbreak detection. The plugin configures Gemini to act as a safety filter to mitigate against content safety, brand safety, and agent misalignment. The plugin is configured to pass user input, tool input and output, and model output to Gemini Flash Lite, who decides if the input to the agent is safe or unsafe. If Gemini decides the input is unsafe, the agent returns a predetermined response: "Sorry I cannot help with that. Can I help you with something else?".

* **Model Armor Plugin**: A plugin that queries the model armor API to check for potential content safety violations at specified points of agent execution. Similar to the _Gemini as a Judge_ plugin, if Model Armor finds matches of harmful content, it returns a predetermined response to the user.

* **PII Redaction Plugin**: A specialized plugin with design for the [Before Tool Callback](/adk-docs/plugins/#tool-callbacks) and specifically created to redact personally identifiable information before it’s processed by a tool or sent to an external service.
