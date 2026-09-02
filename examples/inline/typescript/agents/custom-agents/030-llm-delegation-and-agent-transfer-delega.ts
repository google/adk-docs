// Conceptual Setup: LLM Transfer
import { LlmAgent } from '@google/adk';

const bookingAgent = new LlmAgent({name: 'Booker', description: 'Handles flight and hotel bookings.'});
const infoAgent = new LlmAgent({name: 'Info', description: 'Provides general information and answers questions.'});

const coordinator = new LlmAgent({
    name: 'Coordinator',
    model: 'gemini-flash-latest',
    instruction: 'You are an assistant. Delegate booking tasks to Booker and info requests to Info.',
    description: 'Main coordinator.',
    // AutoFlow is typically used implicitly here
    subAgents: [bookingAgent, infoAgent]
});
// If coordinator receives "Book a flight", its LLM should generate:
// {functionCall: {name: 'transfer_to_agent', args: {agent_name: 'Booker'}}}
// ADK framework then routes execution to bookingAgent.