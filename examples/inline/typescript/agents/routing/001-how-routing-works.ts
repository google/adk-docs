type AgentRouter = (
  agents: Readonly<Record<string, BaseAgent>>,
  context: InvocationContext,
  errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
) => Promise<string | undefined> | string | undefined;