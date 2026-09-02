// In ADK Java, dynamic threshold confirmation logic is evaluated directly
// inside the tool logic using the ToolContext rather than via a lambda parameter.
public Map<String, Object> reimburse(
    @Schema(name="amount") int amount, ToolContext toolContext) {

  // 1. Dynamic threshold check
  if (amount > 1000) {
    Optional<ToolConfirmation> toolConfirmation = toolContext.toolConfirmation();
    if (toolConfirmation.isEmpty()) {
       toolContext.requestConfirmation("Amount > 1000 requires approval.");
       return Map.of("status", "Pending manager approval.");
    } else if (!toolConfirmation.get().confirmed()) {
       return Map.of("status", "Reimbursement rejected.");
    }
  }

  // 2. Proceed with actual tool logic
  return Map.of("status", "ok", "reimbursedAmount", amount);
}

LlmAgent rootAgent = LlmAgent.builder()
    // ...
    .tools(
        // No requireConfirmation flag is set because the custom threshold
        // logic is already handled inside the method!
        FunctionTool.create(this, "reimburse")
    )
    // ...
    .build();