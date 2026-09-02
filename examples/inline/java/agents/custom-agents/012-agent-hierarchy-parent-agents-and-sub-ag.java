// Conceptual Example: Defining Hierarchy
import com.google.adk.agents.SequentialAgent;
import com.google.adk.agents.LlmAgent;


// Define individual agents
LlmAgent greeter = LlmAgent.builder().name("Greeter").model("gemini-flash-latest").build();
SequentialAgent taskDoer = SequentialAgent.builder().name("TaskExecutor").subAgents(...).build(); // Sequential Agent


// Create parent agent and assign sub_agents
LlmAgent coordinator = LlmAgent.builder()
    .name("Coordinator")
    .model("gemini-flash-latest")
    .description("I coordinate greetings and tasks")
    .subAgents(greeter, taskDoer) // Assign sub_agents here
    .build();


// Framework automatically sets:
// assert greeter.parentAgent().equals(coordinator);
// assert taskDoer.parentAgent().equals(coordinator);