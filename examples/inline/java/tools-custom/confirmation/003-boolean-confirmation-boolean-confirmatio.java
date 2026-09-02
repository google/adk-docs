LlmAgent rootAgent = LlmAgent.builder()
    // ...
    .tools(
        // Set requireConfirmation to true to require user confirmation
        // for the tool call.
        FunctionTool.create(myClassInstance, "reimburse", true)
    )
    // ...
    .build();