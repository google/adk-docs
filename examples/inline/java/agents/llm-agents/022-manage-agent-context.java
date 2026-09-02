import com.google.adk.agents.LlmAgent.IncludeContents;

LlmAgent statelessAgent =
    LlmAgent.builder()
        // ... other params
        .includeContents(IncludeContents.NONE)
        .build();