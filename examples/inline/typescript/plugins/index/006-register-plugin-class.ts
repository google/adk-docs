import { InMemoryRunner, LlmAgent, FunctionTool } from "@google/adk";
import type { Content } from "@google/genai";
import { z } from "zod";

// Import the plugin.
import { CountInvocationPlugin } from "./count_plugin.ts";

const HelloWorldInput = z.object({
    query: z.string().describe("The query string to print."),
});

async function helloWorld({ query }: z.infer<typeof HelloWorldInput>): Promise<{ result: string }> {
    const output = `Hello world: query is [${query}]`;
    console.log(output);
    // Tools should return a string or JSON-compatible object
    return { result: output };
}

const helloWorldTool = new FunctionTool({
    name: "hello_world",
    description: "Prints hello world with user query.",
    parameters: HelloWorldInput,
    execute: helloWorld,
});

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest", // Preserved from your Python code
    name: "hello_world",
    description: "Prints hello world with user query.",
    instruction: `Use hello_world tool to print hello world and user query.`,
    tools: [helloWorldTool],
});

/**
* Main entry point for the agent.
*/
async function main(): Promise<void> {
    const prompt = "hello world";
    const runner = new InMemoryRunner({
        agent: rootAgent,
        appName: "test_app_with_plugin",

        // Add your plugin here. You can add multiple plugins.
        plugins: [new CountInvocationPlugin()],
    });

    // The rest is the same as starting a regular ADK runner.
    const session = await runner.sessionService.createSession({
        userId: "user",
        appName: "test_app_with_plugin",
    });

    // runAsync returns an async iterable stream in TypeScript
    const runStream = runner.runAsync({
        userId: "user",
        sessionId: session.id,
        newMessage: {
        role: "user",
        parts: [{ text: prompt }],
        },
    });

    // Use 'for await...of' to loop through the async stream
    for await (const event of runStream) {
        console.log(`** Got event from ${event.author}`);
    }
}

main();