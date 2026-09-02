// Conceptual Example: Sequential Pipeline
import { SequentialAgent, LlmAgent } from '@google/adk';

const step1 = new LlmAgent({name: 'Step1_Fetch', outputKey: 'data'}); // Saves output to state['data']
const step2 = new LlmAgent({name: 'Step2_Process', instruction: 'Process data from {data}.'});

const pipeline = new SequentialAgent({name: 'MyPipeline', subAgents: [step1, step2]});
// When pipeline runs, Step2 can access the state['data'] set by Step1.