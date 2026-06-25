/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {FunctionTool, LlmAgent} from '@google/adk';
import {z} from 'zod';

// --8<-- [start:advanced_confirmation]
/**
 * A tool that requests time off for an employee.
 * It uses the Advanced Confirmation pattern to request manager approval.
 */
export const requestTimeOffTool = new FunctionTool({
  name: 'request_time_off',
  description: 'Request days off for the employee.',
  parameters: z.object({
    days: z.number().describe('The number of days requested.'),
  }),
  execute: async ({days}, toolContext) => {
    const confirmation = toolContext?.toolConfirmation;

    if (!confirmation) {
      // Step 1: Request confirmation with a payload
      toolContext?.requestConfirmation({
        hint:
          'Please approve or reject the tool call request_time_off() by ' +
          'responding with a FunctionResponse with an expected ' +
          'ToolConfirmation payload.',
        payload: {
          approved_days: 0,
        },
      });

      // Return a descriptive status to the agent
      return {
        status: 'PENDING_MANAGER_APPROVAL',
        message: `A request for ${days} days is pending manager approval.`,
      };
    }

    // Step 2: Process the confirmation response
    if (!confirmation.confirmed) {
      return {
        status: 'CANCELLED',
        message: 'The request was cancelled by the user.',
      };
    }

    let approvedDays = (confirmation.payload as any)['approved_days'] as number;
    approvedDays = Math.min(approvedDays, days);

    if (approvedDays === 0) {
      return {
        status: 'REJECTED',
        message: 'The time off request was rejected by the manager.',
        approved_days: 0,
      };
    }

    return {
      status: 'SUCCESS',
      message: `The request for ${days} days was approved (Total approved: ${approvedDays}).`,
      approved_days: approvedDays,
    };
  },
});

export const rootAgent = new LlmAgent({
  name: 'HR_Assistant',
  model: 'gemini-flash-latest',
  instruction: `You are an HR Assistant. 
  1. Use the 'request_time_off' tool to help employees with leave requests.
  2. MANDATORY: Every tool call MUST be accompanied by a text response in the same message.
  3. EXAMPLE:
     User: "I want 5 days off"
     Model: "I am initiating your leave request for 5 days. Management approval is required, so please confirm this request." [Tool Call: request_time_off(days=5)]
  4. In the terminal, if they want to 'confirm', tell them to simulate a confirmation response. 
  5. Once confirmed, the system will automatically provide the result of the approval.`,
  tools: [requestTimeOffTool],
});
// --8<-- [end:advanced_confirmation]
