import { LlmAgent } from "@google/adk";

const storyGenerator = new LlmAgent({
    name: "StoryGenerator",
    model: "gemini-flash-latest",
    instruction: "Write a short story about a cat, focusing on the theme: {topic}."
});

// Assuming session.state['topic'] is set to "friendship", the LLM
// will receive the following instruction:
// "Write a short story about a cat, focusing on the theme: friendship."