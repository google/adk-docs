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
import { LlmAgent, FunctionTool, ToolContext, InMemoryRunner, isFinalResponse, stringifyContent } from "@google/adk";
import { z } from "zod";
import { Content, createUserContent } from "@google/genai";

function checkAndTransfer(
  params: { query: string },
  toolContext?: ToolContext
): Record<string, any> {
  if (!toolContext) {
    // This should not happen in a normal ADK flow where the tool is called by an agent.
    throw new Error("ToolContext is required to transfer agents.");
  }
  if (params.query.toLowerCase().includes("urgent")) {
    console.log("Tool: Urgent query detected, transferring to support_agent.");
    toolContext.actions.transferToAgent = "support_agent";
    return { status: "success", message: "Transferring to support agent." };
  }

  console.log("Tool: Query is not urgent, handling normally.");
  return { status: "success", message: "Query will be handled by the main agent." };
}

const transferTool = new FunctionTool({
  name: "check_and_transfer",
  description: "Checks the user's query and transfers to a support agent if urgent.",
  parameters: z.object({
    query: z.string().describe("The user query to analyze."),
  }),
  execute: checkAndTransfer,
});

const supportAgent = new LlmAgent({
  name: "support_agent",
  description: "Handles urgent user requests about accounts.",
  instruction: "You are the support agent. Handle the user's urgent request.",
  model: "gemini-2.5-flash"
});

const mainAgent = new LlmAgent({
  name: "main_agent",
  description: "The main agent that routes non-urgent queries.",
  instruction: "You are the main agent. Use the check_and_transfer tool to analyze the user query. If the query is not urgent, handle it yourself.",
  tools: [transferTool],
  subAgents: [supportAgent],
  model: "gemini-2.5-flash"
});

async function main() {
  const runner = new InMemoryRunner({ agent: mainAgent, appName: "customer_support_app" });

  console.log("--- Running with a non-urgent query ---");
  await runner.sessionService.createSession({ appName: "customer_support_app", userId: "user1", sessionId: "session1" });
  const nonUrgentMessage: Content = createUserContent("I have a general question about my account.");
  for await (const event of runner.runAsync({ userId: "user1", sessionId: "session1", newMessage: nonUrgentMessage })) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const text = stringifyContent(event).trim();
      if (text) {
        console.log(`Final Response: ${text}`);
      }
    }
  }

  console.log("\n--- Running with an urgent query ---");
  await runner.sessionService.createSession({ appName: "customer_support_app", userId: "user1", sessionId: "session2" });
  const urgentMessage: Content = createUserContent("My account is locked and this is urgent!");
  for await (const event of runner.runAsync({ userId: "user1", sessionId: "session2", newMessage: urgentMessage })) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const text = stringifyContent(event).trim();
      if (text) {
        console.log(`Final Response: ${text}`);
      }
    }
  }
}

main();