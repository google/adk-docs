// --- Example #1: using a stable Gemini Flash model with ENV variables---
LlmAgent agentGeminiFlash =
    LlmAgent.builder()
        // Use the latest stable Flash model identifier
        .model("gemini-flash-latest") // Set ENV variables to use this model
        .name("gemini_flash_agent")
        .instruction("You are a fast and helpful Gemini assistant.")
        // ... other agent parameters
        .build();