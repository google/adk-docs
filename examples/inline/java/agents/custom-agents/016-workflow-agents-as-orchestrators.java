// Conceptual Example: Sequential Pipeline
import com.google.adk.agents.SequentialAgent;
import com.google.adk.agents.LlmAgent;

LlmAgent step1 = LlmAgent.builder().name("Step1_Fetch").outputKey("data").build(); // Saves output to state.get("data")
LlmAgent step2 = LlmAgent.builder().name("Step2_Process").instruction("Process data from {data}.").build();

SequentialAgent pipeline = SequentialAgent.builder().name("MyPipeline").subAgents(step1, step2).build();
// When pipeline runs, Step2 can access the state.get("data") set by Step1.