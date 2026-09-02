export function handleFunctionCalls(event: Event) {
    const calls = getFunctionCalls(event);
    if (calls.length > 0) {
        for (const call of calls) {
            const toolName = call.name;
            const argumentsDict = call.args; // This is an object
            console.log(`  Tool: ${toolName}, Args: ${JSON.stringify(argumentsDict)}`);
        }
    }
}