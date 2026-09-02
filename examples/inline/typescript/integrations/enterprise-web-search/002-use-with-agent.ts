import { LlmAgent, ENTERPRISE_WEB_SEARCH } from "@google/adk";

const rootAgent = new LlmAgent({
  model: "gemini-flash-latest",
  name: "enterprise_search_agent",
  instruction: "Answer user questions accurately using enterprise-compliant web search results.",
  tools: [ENTERPRISE_WEB_SEARCH],
});

export { rootAgent };