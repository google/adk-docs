// Conceptual Code: Coordinator using LLM Transfer
import { LlmAgent } from '@google/adk';

const billingAgent = new LlmAgent({name: 'Billing', description: 'Handles billing inquiries.'});
const supportAgent = new LlmAgent({name: 'Support', description: 'Handles technical support requests.'});

const coordinator = new LlmAgent({
    name: 'HelpDeskCoordinator',
    model: 'gemini-flash-latest',
    instruction: 'Route user requests: Use Billing agent for payment issues, Support agent for technical problems.',
    description: 'Main help desk router.',
    // allowTransfer=true is often implicit with subAgents in AutoFlow
    subAgents: [billingAgent, supportAgent]
});
// User asks "My payment failed" -> Coordinator's LLM should call {functionCall: {name: 'transfer_to_agent', args: {agent_name: 'Billing'}}}
// User asks "I can't log in" -> Coordinator's LLM should call {functionCall: {name: 'transfer_to_agent', args: {agent_name: 'Support'}}}