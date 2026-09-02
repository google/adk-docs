// Conceptual Setup: LLM Transfer
import com.google.adk.agents.LlmAgent;


LlmAgent bookingAgent = LlmAgent.builder()
    .name("Booker")
    .description("Handles flight and hotel bookings.")
    .build();


LlmAgent infoAgent = LlmAgent.builder()
    .name("Info")
    .description("Provides general information and answers questions.")
    .build();


// Define the coordinator agent
LlmAgent coordinator = LlmAgent.builder()
    .name("Coordinator")
    .model("gemini-flash-latest") // Or your desired model
    .instruction("You are an assistant. Delegate booking tasks to Booker and info requests to Info.")
    .description("Main coordinator.")
    // AutoFlow will be used by default (implicitly) because subAgents are present
    // and transfer is not disallowed.
    .subAgents(bookingAgent, infoAgent)
    .build();

// If coordinator receives "Book a flight", its LLM should generate:
// FunctionCall.builder.name("transferToAgent").args(ImmutableMap.of("agent_name", "Booker")).build()
// ADK framework then routes execution to bookingAgent.