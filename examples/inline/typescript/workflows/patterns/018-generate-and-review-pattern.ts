// Conceptual Code: Generator-Critic
import { SequentialAgent, LlmAgent } from '@google/adk';

const generator = new LlmAgent({
    name: 'DraftWriter',
    instruction: 'Write a short paragraph about subject X.',
    outputKey: 'draft_text'
});

const reviewer = new LlmAgent({
    name: 'FactChecker',
    instruction: 'Review the text in {draft_text} for factual accuracy. Output "valid" or "invalid" with reasons.',
    outputKey: 'review_status'
});

// Optional: Further steps based on review_status

const reviewPipeline = new SequentialAgent({
    name: 'WriteAndReview',
    subAgents: [generator, reviewer]
});
// generator runs -> saves draft to state['draft_text']
// reviewer runs -> reads state['draft_text'], saves status to state['review_status']