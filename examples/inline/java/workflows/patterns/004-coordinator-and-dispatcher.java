// Conceptual Code: Coordinator using LLM Transfer
import com.google.adk.agents.LlmAgent;

LlmAgent billingAgent = LlmAgent.builder()
    .name("Billing")
    .description("Handles billing inquiries and payment issues.")
    .build();

LlmAgent supportAgent = LlmAgent.builder()
    .name("Support")
    .description("Handles technical support requests and login problems.")
    .build();

LlmAgent coordinator = LlmAgent.builder()
    .name("HelpDeskCoordinator")
    .model("gemini-flash-latest")
    .instruction("Route user requests: Use Billing agent for payment issues, Support agent for technical problems.")
    .description("Main help desk router.")
    .subAgents(billingAgent, supportAgent)
    // Agent transfer is implicit with sub agents in the Autoflow, unless specified
    // using .disallowTransferToParent or disallowTransferToPeers
    .build();

// User asks "My payment failed" -> Coordinator's LLM should call
// transferToAgent(agentName='Billing')
// User asks "I can't log in" -> Coordinator's LLM should call
// transferToAgent(agentName='Support')