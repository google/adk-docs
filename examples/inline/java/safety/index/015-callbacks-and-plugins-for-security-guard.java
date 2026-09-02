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
        .model("gemini-flash-latest")
        .name("AgentWithBeforeToolCallback")
        .instruction("...")
        .beforeToolCallback(this::validateToolParams) // Assign the callback
        .tools(anyToolToUse) // Define the tool to be used
        .build();
}