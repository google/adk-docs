async onToolErrorCallback(
    tool: BaseTool,
    toolArgs: { [key: string]: any },
    context: Context,
    error: Error
): Promise<{ [key:string]: any } | undefined> {
    // Your implementation here
}