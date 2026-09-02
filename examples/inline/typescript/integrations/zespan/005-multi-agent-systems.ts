const specialist = new LlmAgent({
  name: "lookup_agent",
  model: "gemini-flash-latest",
  tools: [lookupTool],
});

const coordinator = new LlmAgent({
  name: "coordinator",
  model: "gemini-flash-latest",
  subAgents: [specialist],
});

const { runner: tracedRunner } = instrumentADK({
  coordinator,
  runner: new InMemoryRunner({ agent: coordinator, appName: "my_app" }),
});