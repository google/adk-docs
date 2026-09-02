// Conceptual Example: Using outputKey and reading state
import { LlmAgent, SequentialAgent } from '@google/adk';

const agentA = new LlmAgent({name: 'AgentA', instruction: 'Find the capital of France.', outputKey: 'capital_city'});
const agentB = new LlmAgent({name: 'AgentB', instruction: 'Tell me about the city stored in {capital_city}.'});

const pipeline = new SequentialAgent({name: 'CityInfo', subAgents: [agentA, agentB]});
// AgentA runs, saves "Paris" to state['capital_city'].
// AgentB runs, its instruction processor reads state['capital_city'] to get "Paris".