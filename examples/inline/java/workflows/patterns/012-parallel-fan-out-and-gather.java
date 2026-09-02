// Conceptual Code: Parallel Information Gathering
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.ParallelAgent;
import com.google.adk.agents.SequentialAgent;

LlmAgent fetchApi1 = LlmAgent.builder()
    .name("API1Fetcher")
    .instruction("Fetch data from API 1.")
    .outputKey("api1_data")
    .build();

LlmAgent fetchApi2 = LlmAgent.builder()
    .name("API2Fetcher")
    .instruction("Fetch data from API 2.")
    .outputKey("api2_data")
    .build();

ParallelAgent gatherConcurrently = ParallelAgent.builder()
    .name("ConcurrentFetcher")
    .subAgents(fetchApi2, fetchApi1)
    .build();

LlmAgent synthesizer = LlmAgent.builder()
    .name("Synthesizer")
    .instruction("Combine results from {api1_data} and {api2_data}.")
    .build();

SequentialAgent overallWorfklow = SequentialAgent.builder()
    .name("FetchAndSynthesize") // Run parallel fetch, then synthesize
    .subAgents(gatherConcurrently, synthesizer)
    .build();

// fetch_api1 and fetch_api2 run concurrently, saving to state.
// synthesizer runs afterwards, reading state['api1_data'] and state['api2_data'].