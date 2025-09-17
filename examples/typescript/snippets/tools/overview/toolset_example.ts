import { LlmAgent, FunctionTool, ToolContext, BaseToolset, ReadonlyContext, InMemoryRunner, isFinalResponse, BaseTool } from "@google/adk";
import { z } from "zod";
import { Content } from "@google/genai";

function addNumbers(params: { a: number; b: number }, toolContext?: ToolContext): Record<string, any> {
  if (!toolContext) {
    throw new Error("ToolContext is required for this tool.");
  }
  const result = params.a + params.b;
  toolContext.state.set("last_math_result", result);
  return { result: result };
}

function subtractNumbers(params: { a: number; b: number }): Record<string, any> {
  return { result: params.a - params.b };
}

function greetUser(params: { name: string }): Record<string, any> {
  return { greeting: `Hello, ${params.name}!` };
}

class SimpleMathToolset extends BaseToolset {
  private readonly tools: BaseTool[];

  constructor(prefix = "") {
    super([]); // No filter
    this.tools = [
      new FunctionTool({
        name: `${prefix}add_numbers`,
        description: "Adds two numbers and stores the result in the session state.",
        parameters: z.object({ a: z.number(), b: z.number() }),
        execute: addNumbers,
      }),
      new FunctionTool({
        name: `${prefix}subtract_numbers`,
        description: "Subtracts the second number from the first.",
        parameters: z.object({ a: z.number(), b: z.number() }),
        execute: subtractNumbers,
      }),
    ];
  }

  async getTools(readonlyContext?: ReadonlyContext): Promise<BaseTool[]> {
    return this.tools;
  }

  async close(): Promise<void> {
    console.log("SimpleMathToolset closed.");
  }
}

async function main() {
  const mathToolsetInstance = new SimpleMathToolset("calculator_");
  const greetTool = new FunctionTool({
    name: "greet_user",
    description: "Greets the user.",
    parameters: z.object({ name: z.string() }),
    execute: greetUser,
  });

  const instruction =
    "You are a calculator and a greeter. " +
    "If the user asks for a math operation, use the calculator tools. " +
    "If the user asks for a greeting, use the greet_user tool. " +
    "The result of the last math operation is stored in the 'last_math_result' state variable.";

  const calculatorAgent = new LlmAgent({
    name: "calculator_agent",
    instruction: instruction,
    tools: [greetTool, mathToolsetInstance],
    model: "gemini-1.5-flash",
  });

  const runner = new InMemoryRunner({ agent: calculatorAgent, appName: "toolset_app" });
  await runner.sessionService.createSession({ appName: "toolset_app", userId: "user1", sessionId: "session1" });

  const message: Content = {
    role: "user",
    parts: [{ text: "What is 5 + 3?" }],
  };

  for await (const event of runner.run({ userId: "user1", sessionId: "session1", newMessage: message })) {
    if (isFinalResponse(event) && event.content?.parts) {
      const text = event.content.parts.map(p => p.text).join('').trim();
      if (text) {
        console.log(`Response from agent: ${text}`);
      }
    }
  }

  await mathToolsetInstance.close();
}

main();
