/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {FunctionTool, LlmAgent} from '@google/adk';
import {z} from 'zod';

// --8<-- [start:boolean_confirmation]
/**
 * Basic boolean confirmation logic.
 */
export const reimburseTool = new FunctionTool({
  name: 'reimburse',
  description: 'Reimburse an amount. The user must confirm the amount before processing.',
  parameters: z.object({
    // Using coerce to number to handle cases where the model might pass a string like "600".
    amount: z.coerce.number().describe('The amount to reimburse.'),
  }),
  execute: async ({amount}, toolContext) => {
    // Check if we already have a confirmed response from the system.
    if (toolContext?.toolConfirmation?.confirmed) {
      return {
        status: 'SUCCESS',
        message: `Reimbursement of ${amount} has been successfully processed.`,
      };
    }

    // Otherwise, request a tool confirmation.
    // This will pause the agent and trigger a confirmation UI in supported frontends.
    toolContext?.requestConfirmation({
      hint: `Do you want to reimburse ${amount}?`,
      payload: {amount},
    });

    // Return a status that tells the agent we are waiting.
    return {
      status: 'AWAITING_CONFIRMATION',
      message: 'This request requires user approval to proceed.',
    };
  },
});

export const rootAgent = new LlmAgent({
  name: 'Finance_Assistant',
  model: 'gemini-flash-latest',
  instruction: `You are a Finance Assistant. 
  - You MUST use the 'reimburse' tool for ALL reimbursement requests.
  - MANDATORY: Every tool call MUST be accompanied by a text response in the same message.
  - EXAMPLE:
    User: "Reimburse me $300"
    Model: "I am initiating the reimbursement request for 300. Please confirm it to proceed." [Tool Call: reimburse(amount=300)]
  - If the user provides a currency symbol (like $), ignore it and pass only the number to the tool.
  - In the Web UI, the user will see a 'Confirm' button. In the terminal, the user should simulate a confirmation response.`,
  tools: [reimburseTool],
});
// --8<-- [end:boolean_confirmation]

// --8<-- [start:dynamic_confirmation]
/**
 * Dynamic threshold confirmation logic.
 */
export const dynamicReimburseTool = new FunctionTool({
  name: 'reimburse_with_threshold',
  description: 'Reimburse an amount with a $1000 automatic approval limit.',
  parameters: z.object({
    amount: z.coerce.number().describe('The amount to reimburse.'),
  }),
  execute: async ({amount}, toolContext) => {
    // 1. If it's a large amount, check for confirmation.
    if (amount > 1000) {
      if (toolContext?.toolConfirmation?.confirmed) {
        return {
          status: 'SUCCESS',
          message: `Large reimbursement of ${amount} approved and processed.`,
        };
      }

      toolContext?.requestConfirmation({
        hint: `The amount ${amount} exceeds the $1000 limit. Do you authorize this?`,
        payload: {amount},
      });
      return {status: 'AWAITING_MANAGER_APPROVAL'};
    }

    // 2. Automatic approval for small amounts.
    return {
      status: 'SUCCESS',
      message: `Reimbursement of ${amount} processed automatically.`,
    };
  },
});
// --8<-- [end:dynamic_confirmation]
