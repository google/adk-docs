import { LlmAgent, FunctionTool, ToolContext, InMemoryRunner, isFinalResponse } from "@google/adk";
import { z } from "zod";
import { Content } from "@google/genai";

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

async function main() {
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

  const runner = new InMemoryRunner({ agent: mainAgent, appName: "customer_support_app" });

  console.log("--- Running with a non-urgent query ---");
  await runner.sessionService.createSession({ appName: "customer_support_app", userId: "user1", sessionId: "session1" });
  const nonUrgentMessage: Content = {
    role: "user",
    parts: [{ text: "I have a general question about my account." }],
  };
  for await (const event of runner.run({ userId: "user1", sessionId: "session1", newMessage: nonUrgentMessage })) {
    if (isFinalResponse(event) && event.content?.parts) {
      const text = event.content.parts.map(p => p.text).join('').trim();
      if (text) {
        console.log(`Final Response: ${text}`);
      }
    }
  }

  console.log("\n--- Running with an urgent query ---");
  await runner.sessionService.createSession({ appName: "customer_support_app", userId: "user1", sessionId: "session2" });
  const urgentMessage: Content = {
    role: "user",
    parts: [{ text: "My account is locked and this is urgent!" }],
  };
  for await (const event of runner.run({ userId: "user1", sessionId: "session2", newMessage: urgentMessage })) {
    if (isFinalResponse(event) && event.content?.parts) {
      const text = event.content.parts.map(p => p.text).join('').trim();
      if (text) {
        console.log(`Final Response: ${text}`);
      }
    }
  }
}

main();
