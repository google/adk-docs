// Conceptual Code: Using a Tool for Human Approval
import { LlmAgent, SequentialAgent, FunctionTool } from '@google/adk';
import { z } from 'zod';

// --- Assume externalApprovalTool exists ---
// This tool would:
// 1. Take details (e.g., request_id, amount, reason).
// 2. Send these details to a human review system (e.g., via API).
// 3. Poll or wait for the human response (approved/rejected).
// 4. Return the human's decision.
async function externalApprovalTool(params: {amount: number, reason: string}): Promise<{decision: string}> {
  // ... implementation to call external system
  return {decision: 'approved'}; // or 'rejected'
}

const approvalTool = new FunctionTool({
  name: 'external_approval_tool',
  description: 'Sends a request for human approval.',
  parameters: z.object({
    amount: z.number(),
    reason: z.string(),
  }),
  execute: externalApprovalTool,
});


// Agent that prepares the request
const prepareRequest = new LlmAgent({
    name: 'PrepareApproval',
    instruction: 'Prepare the approval request details based on user input. Store amount and reason in state.',
    // ... likely sets state['approval_amount'] and state['approval_reason'] ...
});

// Agent that calls the human approval tool
const requestApproval = new LlmAgent({
    name: 'RequestHumanApproval',
    instruction: 'Use the external_approval_tool with amount from state["approval_amount"] and reason from state["approval_reason"].',
    tools: [approvalTool],
    outputKey: 'human_decision'
});

// Agent that proceeds based on human decision
const processDecision = new LlmAgent({
    name: 'ProcessDecision',
    instruction: 'Check {human_decision}. If "approved", proceed. If "rejected", inform user.'
});

const approvalWorkflow = new SequentialAgent({
    name: 'HumanApprovalWorkflow',
    subAgents: [prepareRequest, requestApproval, processDecision]
});