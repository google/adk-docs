const handler = new ZespanADKCallbackHandler();

const specialist = new LlmAgent({
  name: "lookup_agent",
  model: "gemini-flash-latest",
  tools: [lookupTool],
  ...handler.callbacks,
});

const coordinator = new LlmAgent({
  name: "coordinator",
  model: "gemini-flash-latest",
  subAgents: [specialist],
  ...handler.callbacks,
});