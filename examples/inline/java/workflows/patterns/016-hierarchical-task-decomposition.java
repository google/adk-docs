// Conceptual Code: Hierarchical Research Task
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.AgentTool;


// Low-level tool-like agents
LlmAgent webSearcher = LlmAgent.builder()
    .name("WebSearch")
    .description("Performs web searches for facts.")
    .build();


LlmAgent summarizer = LlmAgent.builder()
    .name("Summarizer")
    .description("Summarizes text.")
    .build();


// Mid-level agent combining tools
LlmAgent researchAssistant = LlmAgent.builder()
    .name("ResearchAssistant")
    .model("gemini-flash-latest")
    .description("Finds and summarizes information on a topic.")
    .tools(AgentTool.create(webSearcher), AgentTool.create(summarizer))
    .build();


// High-level agent delegating research
LlmAgent reportWriter = LlmAgent.builder()
    .name("ReportWriter")
    .model("gemini-flash-latest")
    .instruction("Write a report on topic X. Use the ResearchAssistant to gather information.")
    .tools(AgentTool.create(researchAssistant))
    // Alternatively, could use LLM Transfer if research_assistant is a subAgent
    .build();


// User interacts with ReportWriter.
// ReportWriter calls ResearchAssistant tool.
// ResearchAssistant calls WebSearch and Summarizer tools.
// Results flow back up.