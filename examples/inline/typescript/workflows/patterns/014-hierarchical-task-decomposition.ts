// Conceptual Code: Hierarchical Research Task
import { LlmAgent, AgentTool } from '@google/adk';

// Low-level tool-like agents
const webSearcher = new LlmAgent({name: 'WebSearch', description: 'Performs web searches for facts.'});
const summarizer = new LlmAgent({name: 'Summarizer', description: 'Summarizes text.'});

// Mid-level agent combining tools
const researchAssistant = new LlmAgent({
    name: 'ResearchAssistant',
    model: 'gemini-flash-latest',
    description: 'Finds and summarizes information on a topic.',
    tools: [new AgentTool({agent: webSearcher}), new AgentTool({agent: summarizer})]
});

// High-level agent delegating research
const reportWriter = new LlmAgent({
    name: 'ReportWriter',
    model: 'gemini-flash-latest',
    instruction: 'Write a report on topic X. Use the ResearchAssistant to gather information.',
    tools: [new AgentTool({agent: researchAssistant})]
    // Alternatively, could use LLM Transfer if researchAssistant is a subAgent
});
// User interacts with ReportWriter.
// ReportWriter calls ResearchAssistant tool.
// ResearchAssistant calls WebSearch and Summarizer tools.
// Results flow back up.