/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import { LlmAgent, FunctionTool, ToolContext, BaseToolset, InMemoryRunner, isFinalResponse, BaseTool, stringifyContent } from "@google/adk";
import { z } from "zod";
import { Content, createUserContent } from "@google/genai";

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

  async getTools(): Promise<BaseTool[]> {
    return this.tools;
  }

  async close(): Promise<void> {
    console.log("SimpleMathToolset closed.");
  }
}

async function main() {
  const mathToolset = new SimpleMathToolset("calculator_");
  const greetTool = new FunctionTool({
    name: "greet_user",
    description: "Greets the user.",
    parameters: z.object({ name: z.string() }),
    execute: greetUser,
  });

  const instruction =
    `You are a calculator and a greeter.
    If the user asks for a math operation, use the calculator tools.
    If the user asks for a greeting, use the greet_user tool.
    The result of the last math operation is stored in the 'last_math_result' state variable.`;

  const calculatorAgent = new LlmAgent({
    name: "calculator_agent",
    instruction: instruction,
    tools: [greetTool, mathToolset],
    model: "gemini-2.5-flash",
  });

  const runner = new InMemoryRunner({ agent: calculatorAgent, appName: "toolset_app" });
  await runner.sessionService.createSession({ appName: "toolset_app", userId: "user1", sessionId: "session1" });

  const message: Content = createUserContent("What is 5 + 3?");

  for await (const event of runner.runAsync({ userId: "user1", sessionId: "session1", newMessage: message })) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const text = stringifyContent(event).trim();
      if (text) {
        console.log(`Response from agent: ${text}`);
      }
    }
  }

  await mathToolset.close();
}

main();
