/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {FunctionTool, LlmAgent} from '@google/adk';
import {z} from 'zod';

// --8<-- [start:boolean_confirmation]
/**
 * A reimbursement tool with dynamic confirmation logic.
 */
export const reimburseTool = new FunctionTool({
  name: 'reimburse',
  description: 'Reimburse an amount. Large amounts (>1000) require manager approval.',
  parameters: z.object({
    amount: z.coerce.number().describe('The amount to reimburse.'),
  }),
  execute: async ({amount}, toolContext) => {
    // 1. Check if we already have a confirmed response.
    if (toolContext?.toolConfirmation?.confirmed) {
      const isLarge = amount > 1000;
      return {
        status: 'SUCCESS',
        message: isLarge 
          ? `Large reimbursement of ${amount} approved by manager and processed.`
          : `Reimbursement of ${amount} has been successfully processed.`,
      };
    }

    // 2. Request a tool confirmation.
    const isLarge = amount > 1000;
    toolContext?.requestConfirmation({
      hint: isLarge 
        ? `The amount ${amount} exceeds the $1000 limit and requires manager approval.`
        : `Do you want to reimburse ${amount}?`,
      payload: {amount},
    });

    // 3. Return a status that tells the agent we are waiting.
    // Note: The model won't see this until the turn resumes after confirmation.
    return {
      status: isLarge ? 'AWAITING_MANAGER_APPROVAL' : 'AWAITING_CONFIRMATION',
      message: 'This request requires approval to proceed.',
    };
  },
});

export const rootAgent = new LlmAgent({
  name: 'Finance_Assistant',
  model: 'gemini-flash-latest',
  instruction: `You are a Finance Assistant. 
  - You MUST use the 'reimburse' tool for ALL reimbursement requests.
  - MANDATORY: Every tool call MUST be accompanied by a text response in the same message.
  - THRESHOLD LOGIC:
    - For amounts <= 1000: Say "I am initiating the reimbursement request for [amount]. Please confirm it to proceed."
    - For amounts > 1000: Say "I am initiating the reimbursement request for [amount]. Since this exceeds $1000, manager approval is required. Please confirm the request to submit it for review."
  - EXAMPLES:
    User: "Reimburse me $45"
    Model: "I am initiating the reimbursement request for 45. Please confirm it to proceed." [Tool Call: reimburse(amount=45)]

    User: "Reimburse me $2500"
    Model: "I am initiating the reimbursement request for 2500. Since this exceeds $1000, manager approval is required. Please confirm the request to submit it for review." [Tool Call: reimburse(amount=2500)]
  - If the user provides a currency symbol (like $), ignore it and pass only the number to the tool.
  - In the Web UI, the user will see a 'Confirm' button. In the terminal, the user should simulate a confirmation response.`,
  tools: [reimburseTool],
});
// --8<-- [end:boolean_confirmation]

// --8<-- [start:dynamic_confirmation]
/* 
  Note: In TypeScript, dynamic threshold logic is implemented 
  directly within the tool's 'execute' function as shown above.
*/
// --8<-- [end:dynamic_confirmation]
