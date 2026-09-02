type LlmRouter = (
  models: Readonly<Record<string, BaseLlm>>,
  request: LlmRequest,
  errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
) => Promise<string | undefined> | string | undefined;