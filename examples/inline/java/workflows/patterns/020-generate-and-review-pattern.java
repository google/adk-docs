// Conceptual Code: Generator-Critic
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.SequentialAgent;


LlmAgent generator = LlmAgent.builder()
    .name("DraftWriter")
    .instruction("Write a short paragraph about subject X.")
    .outputKey("draft_text")
    .build();


LlmAgent reviewer = LlmAgent.builder()
    .name("FactChecker")
    .instruction("Review the text in {draft_text} for factual accuracy. Output 'valid' or 'invalid' with reasons.")
    .outputKey("review_status")
    .build();


// Optional: Further steps based on review_status


SequentialAgent reviewPipeline = SequentialAgent.builder()
    .name("WriteAndReview")
    .subAgents(generator, reviewer)
    .build();


// generator runs -> saves draft to state['draft_text']
// reviewer runs -> reads state['draft_text'], saves status to state['review_status']