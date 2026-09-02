// Conceptual Code: Using a Tool for Human Approval
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.SequentialAgent;
import com.google.adk.tools.FunctionTool;


// --- Assume external_approval_tool exists ---
// This tool would:
// 1. Take details (e.g., request_id, amount, reason).
// 2. Send these details to a human review system (e.g., via API).
// 3. Poll or wait for the human response (approved/rejected).
// 4. Return the human's decision.
// public boolean externalApprovalTool(float amount, String reason) { ... }
FunctionTool approvalTool = FunctionTool.create(externalApprovalTool);


// Agent that prepares the request
LlmAgent prepareRequest = LlmAgent.builder()
    .name("PrepareApproval")
    .instruction("Prepare the approval request details based on user input. Store amount and reason in state.")
    // ... likely sets state['approval_amount'] and state['approval_reason'] ...
    .build();


// Agent that calls the human approval tool
LlmAgent requestApproval = LlmAgent.builder()
    .name("RequestHumanApproval")
    .instruction("Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].")
    .tools(approvalTool)
    .outputKey("human_decision")
    .build();


// Agent that proceeds based on human decision
LlmAgent processDecision = LlmAgent.builder()
    .name("ProcessDecision")
    .instruction("Check {human_decision}. If 'approved', proceed. If 'rejected', inform user.")
    .build();


SequentialAgent approvalWorkflow = SequentialAgent.builder()
    .name("HumanApprovalWorkflow")
    .subAgents(prepareRequest, requestApproval, processDecision)
    .build();