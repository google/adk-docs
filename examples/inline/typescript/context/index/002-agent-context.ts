/* Conceptual Pseudocode: How the framework provides context (Internal Logic) */

const runner = new InMemoryRunner({ agent: myRootAgent });
const session = await runner.sessionService.createSession({ ... });
const userMessage = createUserContent(...);

// --- Inside runner.runAsync(...) ---
// 1. Framework creates the main context for this specific run
const invocationContext = new InvocationContext({
  invocationId: "unique-id-for-this-run",
  session: session,
  userContent: userMessage,
  agent: myRootAgent, // The starting agent
  sessionService: runner.sessionService,
  pluginManager: runner.pluginManager,
  // ... other necessary fields ...
});
//
// 2. Framework calls the agent's run method, passing the context implicitly
await myRootAgent.runAsync(invocationContext);
//   --- End Internal Logic ---

// As a developer, you work with the context objects provided in method arguments.