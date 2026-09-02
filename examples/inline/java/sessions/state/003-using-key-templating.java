import com.google.adk.agents.LlmAgent;

LlmAgent storyGenerator = LlmAgent.builder()
    .name("StoryGenerator")
    .model(geminiModel)
    .instruction("Write a short story about a cat, focusing on the theme: " + topic)
    .build();

// Assuming session.state().put("topic", "friendship"), the LLM
// will receive the following instruction:
// "Write a short story about a cat, focusing on the theme: friendship."