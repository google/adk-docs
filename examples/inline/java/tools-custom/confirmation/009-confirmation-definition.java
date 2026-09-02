public Map<String, Object> requestTimeOff(
    @Schema(name="days") int days,
    ToolContext toolContext) {
    // Request day off for the employee.
    // ...
    Optional<ToolConfirmation> toolConfirmation = toolContext.toolConfirmation();
    if (toolConfirmation.isEmpty()) {
        toolContext.requestConfirmation(
            "Please approve or reject the tool call requestTimeOff() by " +
            "responding with a FunctionResponse with an expected " +
            "ToolConfirmation payload.",
            Map.of("approved_days", 0)
        );
        // Return intermediate status indicating that the tool is waiting for
        // a confirmation response:
        return Map.of("status", "Manager approval is required.");
    }

    Map<String, Object> payload = (Map<String, Object>) toolConfirmation.get().payload();
    int approvedDays = (int) payload.get("approved_days");
    approvedDays = Math.min(approvedDays, days);

    if (approvedDays == 0) {
        return Map.of("status", "The time off request is rejected.", "approved_days", 0);
    }

    return Map.of(
        "status", "ok",
        "approved_days", approvedDays
    );
}