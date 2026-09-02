// Conceptual Example: Using outputKey and reading state
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.SequentialAgent;


LlmAgent agentA = LlmAgent.builder()
    .name("AgentA")
    .instruction("Find the capital of France.")
    .outputKey("capital_city")
    .build();


LlmAgent agentB = LlmAgent.builder()
    .name("AgentB")
    .instruction("Tell me about the city stored in {capital_city}.")
    .outputKey("capital_city")
    .build();


SequentialAgent pipeline = SequentialAgent.builder().name("CityInfo").subAgents(agentA, agentB).build();
// AgentA runs, saves "Paris" to state('capital_city').
// AgentB runs, its instruction processor reads state.get("capital_city") to get "Paris".