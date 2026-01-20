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

import {
  LlmAgent,
  Runner,
  FunctionTool,
  LongRunningFunctionTool,
  InMemorySessionService,
  Event,
  stringifyContent,
} from "@google/adk";
import {z} from "zod";
import {Content, FunctionCall, FunctionResponse, createUserContent} from "@google/genai";

// --8<-- [start:define_long_running_function]
// 1. Define the long-running function
function askForApproval(args: {purpose: string; amount: number}) {
  /**
   * Ask for approval for the reimbursement.
   */
  // create a ticket for the approval
  // Send a notification to the approver with the link of the ticket
  return {
    "status": "pending",
    "approver": "Sean Zhou",
    "purpose": args.purpose,
    "amount": args.amount,
    "ticket-id": "approval-ticket-1",
  };
}

// 2. Instantiate the LongRunningFunctionTool class with the long-running function
const longRunningTool = new LongRunningFunctionTool({
  name: "ask_for_approval",
  description: "Ask for approval for the reimbursement.",
  parameters: z.object({
    purpose: z.string().describe("The purpose of the reimbursement."),
    amount: z.number().describe("The amount to reimburse."),
  }),
  execute: askForApproval,
});
// --8<-- [end:define_long_running_function]

function reimburse(args: {purpose: string; amount: number}) {
  /**
   * Reimburse the amount of money to the employee.
   */
  // send the reimbursement request to payment vendor
  return {status: "ok"};
}

const reimburseTool = new FunctionTool({
  name: "reimburse",
  description: "Reimburse the amount of money to the employee.",
  parameters: z.object({
    purpose: z.string().describe("The purpose of the reimbursement."),
    amount: z.number().describe("The amount to reimburse."),
  }),
  execute: reimburse,
});

// 3. Use the tool in an Agent
const reimbursementAgent = new LlmAgent({
  model: "gemini-2.5-flash",
  name: "reimbursement_agent",
  instruction: `
      You are an agent whose job is to handle the reimbursement process for
      the employees. If the amount is less than $100, you will automatically
      approve the reimbursement.

      If the amount is greater than $100, you will
      ask for approval from the manager. If the manager approves, you will
      call reimburse() to reimburse the amount to the employee. If the manager
      rejects, you will inform the employee of the rejection.
    `,
  tools: [reimburseTool, longRunningTool],
});

const APP_NAME = "human_in_the_loop";
const USER_ID = "1234";
const SESSION_ID = "session1234";

// Session and Runner
async function setupSessionAndRunner() {
  const sessionService = new InMemorySessionService();
  const session = await sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID,
  });
  const runner = new Runner({
    agent: reimbursementAgent,
    appName: APP_NAME,
    sessionService: sessionService,
  });
  return {session, runner};
}

function getLongRunningFunctionCall(event: Event): FunctionCall | undefined {
  // Get the long-running function call from the event
  if (
    !event.longRunningToolIds ||
    !event.content ||
    !event.content.parts?.length
  ) {
    return;
  }
  for (const part of event.content.parts) {
    if (
      part &&
      part.functionCall &&
      event.longRunningToolIds &&
      part.functionCall.id &&
      event.longRunningToolIds.includes(part.functionCall.id)
    ) {
      return part.functionCall;
    }
  }
}

function getFunctionResponse(
  event: Event,
  functionCallId: string
): FunctionResponse | undefined {
  // Get the function response for the function call with specified id.
  if (!event.content || !event.content.parts?.length) {
    return;
  }
  for (const part of event.content.parts) {
    if (
      part &&
      part.functionResponse &&
      part.functionResponse.id === functionCallId
    ) {
      return part.functionResponse;
    }
  }
}

// Agent Interaction
async function callAgentAsync(query: string) {
  let longRunningFunctionCall: FunctionCall | undefined;
  let longRunningFunctionResponse: FunctionResponse | undefined;
  let ticketId: string | undefined;
  const content: Content = createUserContent(query);
  const {session, runner} = await setupSessionAndRunner();

  console.log("\nRunning agent...");
  const events = runner.runAsync({
    sessionId: session.id,
    userId: USER_ID,
    newMessage: content,
  });

  for await (const event of events) {
    // Use helper to check for the specific auth request event
    if (!longRunningFunctionCall) {
      longRunningFunctionCall = getLongRunningFunctionCall(event);
    } else {
      const _potentialResponse = getFunctionResponse(
        event,
        longRunningFunctionCall.id!
      );
      if (_potentialResponse) {
        // Only update if we get a non-None response
        longRunningFunctionResponse = _potentialResponse;
        ticketId = (
          longRunningFunctionResponse.response as {[key: string]: any}
        )[`ticket-id`];
      }
    }
    const text = stringifyContent(event);
    if (text) {
      console.log(`[${event.author}]: ${text}`);
    }
  }

  if (longRunningFunctionResponse) {
    // query the status of the corresponding ticket via ticket_id
    // send back an intermediate / final response
    const updatedResponse = JSON.parse(
      JSON.stringify(longRunningFunctionResponse)
    );
    updatedResponse.response = {status: "approved"};
    for await (const event of runner.runAsync({
      sessionId: session.id,
      userId: USER_ID,
      newMessage: createUserContent(JSON.stringify({functionResponse: updatedResponse})),
    })) {
      const text = stringifyContent(event);
      if (text) {
        console.log(`[${event.author}]: ${text}`);
      }
    }
  }
}

async function main() {
  // reimbursement that doesn't require approval
  await callAgentAsync("Please reimburse 50$ for meals");
  // reimbursement that requires approval
  await callAgentAsync("Please reimburse 200$ for meals");
}

main();
