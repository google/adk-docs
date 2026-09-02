// Conceptual Code: Parallel Information Gathering
import { SequentialAgent, ParallelAgent, LlmAgent } from '@google/adk';

const fetchApi1 = new LlmAgent({name: 'API1Fetcher', instruction: 'Fetch data from API 1.', outputKey: 'api1_data'});
const fetchApi2 = new LlmAgent({name: 'API2Fetcher', instruction: 'Fetch data from API 2.', outputKey: 'api2_data'});

const gatherConcurrently = new ParallelAgent({
    name: 'ConcurrentFetch',
    subAgents: [fetchApi1, fetchApi2]
});

const synthesizer = new LlmAgent({
    name: 'Synthesizer',
    instruction: 'Combine results from {api1_data} and {api2_data}.'
});

const overallWorkflow = new SequentialAgent({
    name: 'FetchAndSynthesize',
    subAgents: [gatherConcurrently, synthesizer] // Run parallel fetch, then synthesize
});
// fetchApi1 and fetchApi2 run concurrently, saving to state.
// synthesizer runs afterwards, reading state['api1_data'] and state['api2_data'].