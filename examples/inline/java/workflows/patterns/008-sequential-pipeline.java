// Conceptual Code: Sequential Data Pipeline
import com.google.adk.agents.SequentialAgent;


LlmAgent validator = LlmAgent.builder()
    .name("ValidateInput")
    .instruction("Validate the input")
    .outputKey("validation_status") // Saves its main text output to session.state["validation_status"]
    .build();


LlmAgent processor = LlmAgent.builder()
    .name("ProcessData")
    .instruction("Process data if {validation_status} is 'valid'")
    .outputKey("result") // Saves its main text output to session.state["result"]
    .build();


LlmAgent reporter = LlmAgent.builder()
    .name("ReportResult")
    .instruction("Report the result from {result}")
    .build();


SequentialAgent dataPipeline = SequentialAgent.builder()
    .name("DataPipeline")
    .subAgents(validator, processor, reporter)
    .build();


// validator runs -> saves to state['validation_status']
// processor runs -> reads state['validation_status'], saves to state['result']
// reporter runs -> reads state['result']