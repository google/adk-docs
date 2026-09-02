// Conceptual Code: Sequential Data Pipeline
import { SequentialAgent, LlmAgent } from '@google/adk';

const validator = new LlmAgent({name: 'ValidateInput', instruction: 'Validate the input.', outputKey: 'validation_status'});
const processor = new LlmAgent({name: 'ProcessData', instruction: 'Process data if {validation_status} is "valid".', outputKey: 'result'});
const reporter = new LlmAgent({name: 'ReportResult', instruction: 'Report the result from {result}.'});

const dataPipeline = new SequentialAgent({
    name: 'DataPipeline',
    subAgents: [validator, processor, reporter]
});
// validator runs -> saves to state['validation_status']
// processor runs -> reads state['validation_status'], saves to state['result']
// reporter runs -> reads state['result']