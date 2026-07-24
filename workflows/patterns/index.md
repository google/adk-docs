# Multi-agent workflow patterns

Supported in ADKPython v0.1.0Typescript v0.2.0Go v0.1.0Java v0.1.0Kotlin v0.1.0

This guide provides a number of agent patterns which you can implement with Agent Development Kit (ADK), including code examples. These patterns are useful across a broad set of applications and you should evaluate and test them against your project requirements before committing to a full implementation.

## Coordinator and dispatcher

- **Structure:** A central [`LlmAgent`](/agents/llm-agents/) (Coordinator) manages several specialized `sub_agents`.
- **Goal:** Route incoming requests to the appropriate specialist agent.
- **ADK Primitives Used:**
  - **Hierarchy:** Coordinator has specialists listed in `sub_agents`.
  - **Interaction:** Primarily uses **LLM-Driven Delegation** (requires clear `description`s on sub-agents and appropriate `instruction` on Coordinator) or **Explicit Invocation (`AgentTool`)** (Coordinator includes `AgentTool`-wrapped specialists in its `tools`).

```python
# Conceptual Code: Coordinator using LLM Transfer
from google.adk.agents import LlmAgent


billing_agent = LlmAgent(name="Billing", description="Handles billing inquiries.")
support_agent = LlmAgent(name="Support", description="Handles technical support requests.")


coordinator = LlmAgent(
    name="HelpDeskCoordinator",
    model="gemini-flash-latest",
    instruction="Route user requests: Use Billing agent for payment issues, Support agent for technical problems.",
    description="Main help desk router.",
    # allow_transfer=True is often implicit with sub_agents in AutoFlow
    sub_agents=[billing_agent, support_agent]
)
# User asks "My payment failed" -> Coordinator's LLM should call transfer_to_agent(agent_name='Billing')
# User asks "I can't log in" -> Coordinator's LLM should call transfer_to_agent(agent_name='Support')
```

```typescript
// Conceptual Code: Coordinator using LLM Transfer
import { LlmAgent } from '@google/adk';

const billingAgent = new LlmAgent({name: 'Billing', description: 'Handles billing inquiries.'});
const supportAgent = new LlmAgent({name: 'Support', description: 'Handles technical support requests.'});

const coordinator = new LlmAgent({
    name: 'HelpDeskCoordinator',
    model: 'gemini-flash-latest',
    instruction: 'Route user requests: Use Billing agent for payment issues, Support agent for technical problems.',
    description: 'Main help desk router.',
    // allowTransfer=true is often implicit with subAgents in AutoFlow
    subAgents: [billingAgent, supportAgent]
});
// User asks "My payment failed" -> Coordinator's LLM should call {functionCall: {name: 'transfer_to_agent', args: {agent_name: 'Billing'}}}
// User asks "I can't log in" -> Coordinator's LLM should call {functionCall: {name: 'transfer_to_agent', args: {agent_name: 'Support'}}}
```

```go
import (
    "google.golang.org/adk/v2/agent"
    "google.golang.org/adk/v2/agent/llmagent"
)

// Conceptual Code: Coordinator using LLM Transfer
billingAgent, _ := llmagent.New(llmagent.Config{Name: "Billing", Description: "Handles billing inquiries.", Model: m})
supportAgent, _ := llmagent.New(llmagent.Config{Name: "Support", Description: "Handles technical support requests.", Model: m})

coordinator, _ := llmagent.New(llmagent.Config{
    Name:        "HelpDeskCoordinator",
    Model:       m,
    Instruction: "Route user requests: Use Billing agent for payment issues, Support agent for technical problems.",
    Description: "Main help desk router.",
    SubAgents:   []agent.Agent{billingAgent, supportAgent},
})
// User asks "My payment failed" -> Coordinator's LLM should call transfer_to_agent(agent_name='Billing')
// User asks "I can't log in" -> Coordinator's LLM should call transfer_to_agent(agent_name='Support')
```

```java
// Conceptual Code: Coordinator using LLM Transfer
import com.google.adk.agents.LlmAgent;

LlmAgent billingAgent = LlmAgent.builder()
    .name("Billing")
    .description("Handles billing inquiries and payment issues.")
    .build();

LlmAgent supportAgent = LlmAgent.builder()
    .name("Support")
    .description("Handles technical support requests and login problems.")
    .build();

LlmAgent coordinator = LlmAgent.builder()
    .name("HelpDeskCoordinator")
    .model("gemini-flash-latest")
    .instruction("Route user requests: Use Billing agent for payment issues, Support agent for technical problems.")
    .description("Main help desk router.")
    .subAgents(billingAgent, supportAgent)
    // Agent transfer is implicit with sub agents in the Autoflow, unless specified
    // using .disallowTransferToParent or disallowTransferToPeers
    .build();

// User asks "My payment failed" -> Coordinator's LLM should call
// transferToAgent(agentName='Billing')
// User asks "I can't log in" -> Coordinator's LLM should call
// transferToAgent(agentName='Support')
```

```kotlin
val billingAgent =
    LlmAgent(name = "Billing", model = model, description = "Handles billing inquiries.")
val supportAgent =
    LlmAgent(
        name = "Support",
        model = model,
        description = "Handles technical support requests.",
    )

val helpDesk =
    LlmAgent(
        name = "HelpDeskCoordinator",
        model = model,
        instruction =
            Instruction(
                "Route user requests: Use Billing agent for payment issues, Support agent for technical problems.",
            ),
        description = "Main help desk router.",
        subAgents = listOf(billingAgent, supportAgent),
    )
```

## Sequential pipeline

- **Structure:** A [`SequentialAgent`](/agents/workflow-agents/sequential-agents/) contains `sub_agents` executed in a fixed order.
- **Goal:** Implement a multistep process where the output of one-step feeds into the next.
- **ADK Primitives Used:**
  - **Workflow:** `SequentialAgent` defines the order.
  - **Communication:** Primarily uses **Shared Session State**. Earlier agents write results (often via `output_key`), later agents read those results from `context.state`.

```python
# Conceptual Code: Sequential Data Pipeline
from google.adk.agents import SequentialAgent, LlmAgent


validator = LlmAgent(name="ValidateInput", instruction="Validate the input.", output_key="validation_status")
processor = LlmAgent(name="ProcessData", instruction="Process data if {validation_status} is 'valid'.", output_key="result")
reporter = LlmAgent(name="ReportResult", instruction="Report the result from {result}.")


data_pipeline = SequentialAgent(
    name="DataPipeline",
    sub_agents=[validator, processor, reporter]
)
# validator runs -> saves to state['validation_status']
# processor runs -> reads state['validation_status'], saves to state['result']
# reporter runs -> reads state['result']
```

```typescript
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
```

```go
import (
    "google.golang.org/adk/v2/agent"
    "google.golang.org/adk/v2/agent/llmagent"
    "google.golang.org/adk/v2/agent/workflowagents/sequentialagent"
)

// Conceptual Code: Sequential Data Pipeline
validator, _ := llmagent.New(llmagent.Config{Name: "ValidateInput", Instruction: "Validate the input.", OutputKey: "validation_status", Model: m})
processor, _ := llmagent.New(llmagent.Config{Name: "ProcessData", Instruction: "Process data if {validation_status} is 'valid'.", OutputKey: "result", Model: m})
reporter, _ := llmagent.New(llmagent.Config{Name: "ReportResult", Instruction: "Report the result from {result}.", Model: m})

dataPipeline, _ := sequentialagent.New(sequentialagent.Config{
    AgentConfig: agent.Config{Name: "DataPipeline", SubAgents: []agent.Agent{validator, processor, reporter}},
})
// validator runs -> saves to state["validation_status"]
// processor runs -> reads state["validation_status"], saves to state["result"]
// reporter runs -> reads state["result"]
```

```java
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
```

```kotlin
val validator =
    LlmAgent(
        name = "ValidateInput",
        model = model,
        instruction = Instruction("Validate the input."),
    )
val processor =
    LlmAgent(
        name = "ProcessData",
        model = model,
        instruction = Instruction("Process data if validation is successful."),
    )
val reporter =
    LlmAgent(
        name = "ReportResult",
        model = model,
        instruction = Instruction("Report the result."),
    )

val dataPipeline =
    SequentialAgent(
        name = "DataPipeline",
        subAgents = listOf(validator, processor, reporter),
    )
```

## Parallel fan-out and gather

- **Structure:** A [`ParallelAgent`](/agents/workflow-agents/parallel-agents/) runs multiple `sub_agents` concurrently, often followed by a later agent (in a `SequentialAgent`) that aggregates results.
- **Goal:** Execute independent tasks simultaneously to reduce latency, then combine their outputs.
- **ADK Primitives Used:**
  - **Workflow:** `ParallelAgent` for concurrent execution (Fan-Out). Often nested within a `SequentialAgent` to handle the subsequent aggregation step (Gather).
  - **Communication:** Sub-agents write results to distinct keys in **Shared Session State**. The subsequent "Gather" agent reads multiple state keys.

```python
# Conceptual Code: Parallel Information Gathering
from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent


fetch_api1 = LlmAgent(name="API1Fetcher", instruction="Fetch data from API 1.", output_key="api1_data")
fetch_api2 = LlmAgent(name="API2Fetcher", instruction="Fetch data from API 2.", output_key="api2_data")


gather_concurrently = ParallelAgent(
    name="ConcurrentFetch",
    sub_agents=[fetch_api1, fetch_api2]
)


synthesizer = LlmAgent(
    name="Synthesizer",
    instruction="Combine results from {api1_data} and {api2_data}."
)


overall_workflow = SequentialAgent(
    name="FetchAndSynthesize",
    sub_agents=[gather_concurrently, synthesizer] # Run parallel fetch, then synthesize
)
# fetch_api1 and fetch_api2 run concurrently, saving to state.
# synthesizer runs afterwards, reading state['api1_data'] and state['api2_data'].
```

```typescript
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
```

```go
import (
    "google.golang.org/adk/v2/agent"
    "google.golang.org/adk/v2/agent/llmagent"
    "google.golang.org/adk/v2/agent/workflowagents/parallelagent"
    "google.golang.org/adk/v2/agent/workflowagents/sequentialagent"
)

// Conceptual Code: Parallel Information Gathering
fetchAPI1, _ := llmagent.New(llmagent.Config{Name: "API1Fetcher", Instruction: "Fetch data from API 1.", OutputKey: "api1_data", Model: m})
fetchAPI2, _ := llmagent.New(llmagent.Config{Name: "API2Fetcher", Instruction: "Fetch data from API 2.", OutputKey: "api2_data", Model: m})

gatherConcurrently, _ := parallelagent.New(parallelagent.Config{
    AgentConfig: agent.Config{Name: "ConcurrentFetch", SubAgents: []agent.Agent{fetchAPI1, fetchAPI2}},
})

synthesizer, _ := llmagent.New(llmagent.Config{Name: "Synthesizer", Instruction: "Combine results from {api1_data} and {api2_data}.", Model: m})

overallWorkflow, _ := sequentialagent.New(sequentialagent.Config{
    AgentConfig: agent.Config{Name: "FetchAndSynthesize", SubAgents: []agent.Agent{gatherConcurrently, synthesizer}},
})
// fetch_api1 and fetch_api2 run concurrently, saving to state.
// synthesizer runs afterwards, reading state["api1_data"] and state["api2_data"].
```

```java
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
```

```kotlin
val fetchApi1 =
    LlmAgent(
        name = "API1Fetcher",
        model = model,
        instruction = Instruction("Fetch data from API 1."),
    )
val fetchApi2 =
    LlmAgent(
        name = "API2Fetcher",
        model = model,
        instruction = Instruction("Fetch data from API 2."),
    )

val gatherConcurrently =
    ParallelAgent(
        name = "ConcurrentFetch",
        subAgents = listOf(fetchApi1, fetchApi2),
    )

val synthesizer =
    LlmAgent(
        name = "Synthesizer",
        model = model,
        instruction = Instruction("Combine results from state."),
    )

val overallWorkflow =
    SequentialAgent(
        name = "FetchAndSynthesize",
        subAgents = listOf(gatherConcurrently, synthesizer),
    )
```

## Hierarchical task decomposition

- **Structure:** A multi-level tree of agents where higher-level agents break down complex goals and delegate sub-tasks to lower-level agents.
- **Goal:** Solve complex problems by recursively breaking them down into simpler, executable steps.
- **ADK Primitives Used:**
  - **Hierarchy:** Multi-level `parent_agent`/`sub_agents` structure.
  - **Interaction:** Primarily **LLM-Driven Delegation** or **Explicit Invocation (`AgentTool`)** used by parent agents to assign tasks to subagents. Results are returned up the hierarchy (via tool responses or state).

```python
# Conceptual Code: Hierarchical Research Task
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool


# Low-level tool-like agents
web_searcher = LlmAgent(name="WebSearch", description="Performs web searches for facts.")
summarizer = LlmAgent(name="Summarizer", description="Summarizes text.")


# Mid-level agent combining tools
research_assistant = LlmAgent(
    name="ResearchAssistant",
    model="gemini-flash-latest",
    description="Finds and summarizes information on a topic.",
    tools=[agent_tool.AgentTool(agent=web_searcher), agent_tool.AgentTool(agent=summarizer)]
)


# High-level agent delegating research
report_writer = LlmAgent(
    name="ReportWriter",
    model="gemini-flash-latest",
    instruction="Write a report on topic X. Use the ResearchAssistant to gather information.",
    tools=[agent_tool.AgentTool(agent=research_assistant)]
    # Alternatively, could use LLM Transfer if research_assistant is a sub_agent
)
# User interacts with ReportWriter.
# ReportWriter calls ResearchAssistant tool.
# ResearchAssistant calls WebSearch and Summarizer tools.
# Results flow back up.
```

```typescript
// Conceptual Code: Hierarchical Research Task
import { LlmAgent, AgentTool } from '@google/adk';

// Low-level tool-like agents
const webSearcher = new LlmAgent({name: 'WebSearch', description: 'Performs web searches for facts.'});
const summarizer = new LlmAgent({name: 'Summarizer', description: 'Summarizes text.'});

// Mid-level agent combining tools
const researchAssistant = new LlmAgent({
    name: 'ResearchAssistant',
    model: 'gemini-flash-latest',
    description: 'Finds and summarizes information on a topic.',
    tools: [new AgentTool({agent: webSearcher}), new AgentTool({agent: summarizer})]
});

// High-level agent delegating research
const reportWriter = new LlmAgent({
    name: 'ReportWriter',
    model: 'gemini-flash-latest',
    instruction: 'Write a report on topic X. Use the ResearchAssistant to gather information.',
    tools: [new AgentTool({agent: researchAssistant})]
    // Alternatively, could use LLM Transfer if researchAssistant is a subAgent
});
// User interacts with ReportWriter.
// ReportWriter calls ResearchAssistant tool.
// ResearchAssistant calls WebSearch and Summarizer tools.
// Results flow back up.
```

```go
import (
    "google.golang.org/adk/v2/agent/llmagent"
    "google.golang.org/adk/v2/tool"
    "google.golang.org/adk/v2/tool/agenttool"
)

// Conceptual Code: Hierarchical Research Task
// Low-level tool-like agents
webSearcher, _ := llmagent.New(llmagent.Config{Name: "WebSearch", Description: "Performs web searches for facts.", Model: m})
summarizer, _ := llmagent.New(llmagent.Config{Name: "Summarizer", Description: "Summarizes text.", Model: m})

// Mid-level agent combining tools
webSearcherTool := agenttool.New(webSearcher, nil)
summarizerTool := agenttool.New(summarizer, nil)
researchAssistant, _ := llmagent.New(llmagent.Config{
    Name:        "ResearchAssistant",
    Model:       m,
    Description: "Finds and summarizes information on a topic.",
    Tools:       []tool.Tool{webSearcherTool, summarizerTool},
})

// High-level agent delegating research
researchAssistantTool := agenttool.New(researchAssistant, nil)
reportWriter, _ := llmagent.New(llmagent.Config{
    Name:        "ReportWriter",
    Model:       m,
    Instruction: "Write a report on topic X. Use the ResearchAssistant to gather information.",
    Tools:       []tool.Tool{researchAssistantTool},
})
// User interacts with ReportWriter.
// ReportWriter calls ResearchAssistant tool.
// ResearchAssistant calls WebSearch and Summarizer tools.
// Results flow back up.
```

```java
// Conceptual Code: Hierarchical Research Task
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.AgentTool;


// Low-level tool-like agents
LlmAgent webSearcher = LlmAgent.builder()
    .name("WebSearch")
    .description("Performs web searches for facts.")
    .build();


LlmAgent summarizer = LlmAgent.builder()
    .name("Summarizer")
    .description("Summarizes text.")
    .build();


// Mid-level agent combining tools
LlmAgent researchAssistant = LlmAgent.builder()
    .name("ResearchAssistant")
    .model("gemini-flash-latest")
    .description("Finds and summarizes information on a topic.")
    .tools(AgentTool.create(webSearcher), AgentTool.create(summarizer))
    .build();


// High-level agent delegating research
LlmAgent reportWriter = LlmAgent.builder()
    .name("ReportWriter")
    .model("gemini-flash-latest")
    .instruction("Write a report on topic X. Use the ResearchAssistant to gather information.")
    .tools(AgentTool.create(researchAssistant))
    // Alternatively, could use LLM Transfer if research_assistant is a subAgent
    .build();


// User interacts with ReportWriter.
// ReportWriter calls ResearchAssistant tool.
// ResearchAssistant calls WebSearch and Summarizer tools.
// Results flow back up.
```

```kotlin
val webSearcher =
    LlmAgent(
        name = "WebSearch",
        model = model,
        description = "Performs web searches for facts.",
    )
val summarizer = LlmAgent(name = "Summarizer", model = model, description = "Summarizes text.")

val researchAssistant =
    LlmAgent(
        name = "ResearchAssistant",
        model = model,
        description = "Finds and summarizes information on a topic.",
        subAgents = listOf(webSearcher, summarizer),
    )

val reportWriter =
    LlmAgent(
        name = "ReportWriter",
        model = model,
        instruction =
            Instruction(
                "Write a report on topic X. Use the ResearchAssistant to gather information.",
            ),
        subAgents = listOf(researchAssistant),
    )
```

## Generate and review pattern

- **Structure:** Typically involves two agents within a [`SequentialAgent`](/agents/workflow-agents/sequential-agents/): a generator agent and a critic reviewer agent.
- **Goal:** Improve the quality or validity of generated output by having a dedicated agent review it.
- **ADK Primitives Used:**
  - **Workflow:** `SequentialAgent` ensures generation happens before review.
  - **Communication:** **Shared Session State** (Generator uses `output_key` to save output; Reviewer reads that state key). The Reviewer might save its feedback to another state key for subsequent steps.

```python
# Conceptual Code: Generator-Critic
from google.adk.agents import SequentialAgent, LlmAgent


generator = LlmAgent(
    name="DraftWriter",
    instruction="Write a short paragraph about subject X.",
    output_key="draft_text"
)


reviewer = LlmAgent(
    name="FactChecker",
    instruction="Review the text in {draft_text} for factual accuracy. Output 'valid' or 'invalid' with reasons.",
    output_key="review_status"
)


# Optional: Further steps based on review_status


review_pipeline = SequentialAgent(
    name="WriteAndReview",
    sub_agents=[generator, reviewer]
)
# generator runs -> saves draft to state['draft_text']
# reviewer runs -> reads state['draft_text'], saves status to state['review_status']
```

```typescript
// Conceptual Code: Generator-Critic
import { SequentialAgent, LlmAgent } from '@google/adk';

const generator = new LlmAgent({
    name: 'DraftWriter',
    instruction: 'Write a short paragraph about subject X.',
    outputKey: 'draft_text'
});

const reviewer = new LlmAgent({
    name: 'FactChecker',
    instruction: 'Review the text in {draft_text} for factual accuracy. Output "valid" or "invalid" with reasons.',
    outputKey: 'review_status'
});

// Optional: Further steps based on review_status

const reviewPipeline = new SequentialAgent({
    name: 'WriteAndReview',
    subAgents: [generator, reviewer]
});
// generator runs -> saves draft to state['draft_text']
// reviewer runs -> reads state['draft_text'], saves status to state['review_status']
```

```go
import (
    "google.golang.org/adk/v2/agent"
    "google.golang.org/adk/v2/agent/llmagent"
    "google.golang.org/adk/v2/agent/workflowagents/sequentialagent"
)

// Conceptual Code: Generator-Critic
generator, _ := llmagent.New(llmagent.Config{
    Name:        "DraftWriter",
    Instruction: "Write a short paragraph about subject X.",
    OutputKey:   "draft_text",
    Model:       m,
})

reviewer, _ := llmagent.New(llmagent.Config{
    Name:        "FactChecker",
    Instruction: "Review the text in {draft_text} for factual accuracy. Output 'valid' or 'invalid' with reasons.",
    OutputKey:   "review_status",
    Model:       m,
})

reviewPipeline, _ := sequentialagent.New(sequentialagent.Config{
    AgentConfig: agent.Config{Name: "WriteAndReview", SubAgents: []agent.Agent{generator, reviewer}},
})
// generator runs -> saves draft to state["draft_text"]
// reviewer runs -> reads state["draft_text"], saves status to state["review_status"]
```

```java
// Conceptual Code: Generator-Critic
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.SequentialAgent;


LlmAgent generator = LlmAgent.builder()
    .name("DraftWriter")
    .instruction("Write a short paragraph about subject X.")
    .outputKey("draft_text")
    .build();


LlmAgent reviewer = LlmAgent.builder()
    .name("FactChecker")
    .instruction("Review the text in {draft_text} for factual accuracy. Output 'valid' or 'invalid' with reasons.")
    .outputKey("review_status")
    .build();


// Optional: Further steps based on review_status


SequentialAgent reviewPipeline = SequentialAgent.builder()
    .name("WriteAndReview")
    .subAgents(generator, reviewer)
    .build();


// generator runs -> saves draft to state['draft_text']
// reviewer runs -> reads state['draft_text'], saves status to state['review_status']
```

```kotlin
val generator =
    LlmAgent(
        name = "DraftWriter",
        model = model,
        instruction = Instruction("Write a short paragraph about subject X."),
    )

val reviewer =
    LlmAgent(
        name = "FactChecker",
        model = model,
        instruction =
            Instruction(
                "Review the generated text for factual accuracy. Output 'valid' or 'invalid' with reasons.",
            ),
    )

val reviewPipeline =
    SequentialAgent(
        name = "WriteAndReview",
        subAgents = listOf(generator, reviewer),
    )
```

## Iterative refinement

- **Structure:** Uses a [`LoopAgent`](/agents/workflow-agents/loop-agents/) containing one or more agents that work on a task over multiple iterations.
- **Goal:** Progressively improve a result (e.g., code, text, plan) stored in the session state until a quality threshold is met or a maximum number of iterations is reached.
- **ADK Primitives Used:**
  - **Workflow:** `LoopAgent` manages the repetition.
  - **Communication:** **Shared Session State** is essential for agents to read the previous iteration's output and save the refined version.
  - **Termination:** The loop typically ends based on `max_iterations` or a dedicated checking agent setting `escalate=True` in the `Event Actions` when the result is satisfactory.

```python
# Conceptual Code: Iterative Code Refinement
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator


# Agent to generate/refine code based on state['current_code'] and state['requirements']
code_refiner = LlmAgent(
    name="CodeRefiner",
    instruction="Read state['current_code'] (if exists) and state['requirements']. Generate/refine Python code to meet requirements. Save to state['current_code'].",
    output_key="current_code" # Overwrites previous code in state
)


# Agent to check if the code meets quality standards
quality_checker = LlmAgent(
    name="QualityChecker",
    instruction="Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.",
    output_key="quality_status"
)


# Custom agent to check the status and escalate if 'pass'
class CheckStatusAndEscalate(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("quality_status", "fail")
        should_stop = (status == "pass")
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))


refinement_loop = LoopAgent(
    name="CodeRefinementLoop",
    max_iterations=5,
    sub_agents=[code_refiner, quality_checker, CheckStatusAndEscalate(name="StopChecker")]
)
# Loop runs: Refiner -> Checker -> StopChecker
# State['current_code'] is updated each iteration.
# Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5 iterations.
```

```typescript
// Conceptual Code: Iterative Code Refinement
import { LoopAgent, LlmAgent, BaseAgent, InvocationContext } from '@google/adk';
import type { Event, createEvent, createEventActions } from '@google/genai';

// Agent to generate/refine code based on state['current_code'] and state['requirements']
const codeRefiner = new LlmAgent({
    name: 'CodeRefiner',
    instruction: 'Read state["current_code"] (if exists) and state["requirements"]. Generate/refine Typescript code to meet requirements. Save to state["current_code"].',
    outputKey: 'current_code' // Overwrites previous code in state
});

// Agent to check if the code meets quality standards
const qualityChecker = new LlmAgent({
    name: 'QualityChecker',
    instruction: 'Evaluate the code in state["current_code"] against state["requirements"]. Output "pass" or "fail".',
    outputKey: 'quality_status'
});

// Custom agent to check the status and escalate if 'pass'
class CheckStatusAndEscalate extends BaseAgent {
    async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event> {
        const status = ctx.session.state.quality_status;
        const shouldStop = status === 'pass';
        if (shouldStop) {
            yield createEvent({
                author: 'StopChecker',
                actions: createEventActions(),
            });
        }
    }

    async *runLiveImpl(ctx: InvocationContext): AsyncGenerator<Event> {
        // This agent doesn't have a live implementation
        yield createEvent({ author: 'StopChecker' });
    }
}

// Loop runs: Refiner -> Checker -> StopChecker
// State['current_code'] is updated each iteration.
// Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5 iterations.
const refinementLoop = new LoopAgent({
    name: 'CodeRefinementLoop',
    maxIterations: 5,
    subAgents: [codeRefiner, qualityChecker, new CheckStatusAndEscalate({name: 'StopChecker'})]
});
```

```go
import (
    "iter"
    "google.golang.org/adk/v2/agent"
    "google.golang.org/adk/v2/agent/llmagent"
    "google.golang.org/adk/v2/agent/workflowagents/loopagent"
    "google.golang.org/adk/v2/session"
)

// Conceptual Code: Iterative Code Refinement
codeRefiner, _ := llmagent.New(llmagent.Config{
    Name:        "CodeRefiner",
    Instruction: "Read state['current_code'] (if exists) and state['requirements']. Generate/refine Python code to meet requirements. Save to state['current_code'].",
    OutputKey:   "current_code",
    Model:       m,
})

qualityChecker, _ := llmagent.New(llmagent.Config{
    Name:        "QualityChecker",
    Instruction: "Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.",
    OutputKey:   "quality_status",
    Model:       m,
})

checkStatusAndEscalate, _ := agent.New(agent.Config{
    Name: "StopChecker",
    Run: func(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
        return func(yield func(*session.Event, error) bool) {
            status, _ := ctx.Session().State().Get("quality_status")
            shouldStop := status == "pass"
            yield(&session.Event{Author: "StopChecker", Actions: session.EventActions{Escalate: shouldStop}}, nil)
        }
    },
})

refinementLoop, _ := loopagent.New(loopagent.Config{
    MaxIterations: 5,
    AgentConfig:   agent.Config{Name: "CodeRefinementLoop", SubAgents: []agent.Agent{codeRefiner, qualityChecker, checkStatusAndEscalate}},
})
// Loop runs: Refiner -> Checker -> StopChecker
// State["current_code"] is updated each iteration.
// Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5 iterations.
```

```java
// Conceptual Code: Iterative Code Refinement
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.LoopAgent;
import com.google.adk.events.Event;
import com.google.adk.events.EventActions;
import com.google.adk.agents.InvocationContext;
import io.reactivex.rxjava3.core.Flowable;
import java.util.List;


// Agent to generate/refine code based on state['current_code'] and state['requirements']
LlmAgent codeRefiner = LlmAgent.builder()
    .name("CodeRefiner")
    .instruction("Read state['current_code'] (if exists) and state['requirements']. Generate/refine Java code to meet requirements. Save to state['current_code'].")
    .outputKey("current_code") // Overwrites previous code in state
    .build();


// Agent to check if the code meets quality standards
LlmAgent qualityChecker = LlmAgent.builder()
    .name("QualityChecker")
    .instruction("Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.")
    .outputKey("quality_status")
    .build();


BaseAgent checkStatusAndEscalate = new BaseAgent(
    "StopChecker","Checks quality_status and escalates if 'pass'.", List.of(), null, null) {


  @Override
  protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
    String status = (String) invocationContext.session().state().getOrDefault("quality_status", "fail");
    boolean shouldStop = "pass".equals(status);


    EventActions actions = EventActions.builder().escalate(shouldStop).build();
    Event event = Event.builder()
        .author(this.name())
        .actions(actions)
        .build();
    return Flowable.just(event);
  }
};


LoopAgent refinementLoop = LoopAgent.builder()
    .name("CodeRefinementLoop")
    .maxIterations(5)
    .subAgents(codeRefiner, qualityChecker, checkStatusAndEscalate)
    .build();


// Loop runs: Refiner -> Checker -> StopChecker
// State['current_code'] is updated each iteration.
// Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5
// iterations.
```

```kotlin
val codeRefiner =
    LlmAgent(
        name = "CodeRefiner",
        model = model,
        instruction =
            Instruction(
                "Read current code (if exists) and requirements from state. Generate/refine Kotlin code to meet requirements.",
            ),
    )

val qualityChecker =
    LlmAgent(
        name = "QualityChecker",
        model = model,
        instruction =
            Instruction(
                "Evaluate the code in state against requirements. Output 'pass' or 'fail'.",
            ),
    )

val stopChecker = CheckConditionAgent(name = "StopChecker") // Checks quality_status

val refinementLoop =
    LoopAgent(
        name = "CodeRefinementLoop",
        maxIterations = 5,
        subAgents = listOf(codeRefiner, qualityChecker, stopChecker),
    )
```

## Human-in-the-loop

- **Structure:** Integrates human intervention points within an agent workflow.
- **Goal:** Allow for human oversight, approval, correction, or tasks that AI cannot perform.
- **ADK Primitives Used (Conceptual):**
  - **Interaction:** Can be implemented using a custom **Tool** that pauses execution and sends a request to an external system (e.g., a UI, ticketing system) waiting for human input. The tool then returns the human's response to the agent.
  - **Workflow:** Could use **LLM-Driven Delegation** (`transfer_to_agent`) targeting a conceptual "Human Agent" that triggers the external workflow, or use the custom tool within an `LlmAgent`.
  - **State/Callbacks:** State can hold task details for the human; callbacks can manage the interaction flow.
  - **Note:** ADK doesn't have a built-in "Human Agent" type, so this requires custom integration.

```python
# Conceptual Code: Using a Tool for Human Approval
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool


# --- Assume external_approval_tool exists ---
# This tool would:
# 1. Take details (e.g., request_id, amount, reason).
# 2. Send these details to a human review system (e.g., via API).
# 3. Poll or wait for the human response (approved/rejected).
# 4. Return the human's decision.
# async def external_approval_tool(amount: float, reason: str) -> str: ...
approval_tool = FunctionTool(func=external_approval_tool)


# Agent that prepares the request
prepare_request = LlmAgent(
    name="PrepareApproval",
    instruction="Prepare the approval request details based on user input. Store amount and reason in state.",
    # ... likely sets state['approval_amount'] and state['approval_reason'] ...
)


# Agent that calls the human approval tool
request_approval = LlmAgent(
    name="RequestHumanApproval",
    instruction="Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].",
    tools=[approval_tool],
    output_key="human_decision"
)


# Agent that proceeds based on human decision
process_decision = LlmAgent(
    name="ProcessDecision",
    instruction="Check {human_decision}. If 'approved', proceed. If 'rejected', inform user."
)


approval_workflow = SequentialAgent(
    name="HumanApprovalWorkflow",
    sub_agents=[prepare_request, request_approval, process_decision]
)
```

```typescript
// Conceptual Code: Using a Tool for Human Approval
import { LlmAgent, SequentialAgent, FunctionTool } from '@google/adk';
import { z } from 'zod';

// --- Assume externalApprovalTool exists ---
// This tool would:
// 1. Take details (e.g., request_id, amount, reason).
// 2. Send these details to a human review system (e.g., via API).
// 3. Poll or wait for the human response (approved/rejected).
// 4. Return the human's decision.
async function externalApprovalTool(params: {amount: number, reason: string}): Promise<{decision: string}> {
  // ... implementation to call external system
  return {decision: 'approved'}; // or 'rejected'
}

const approvalTool = new FunctionTool({
  name: 'external_approval_tool',
  description: 'Sends a request for human approval.',
  parameters: z.object({
    amount: z.number(),
    reason: z.string(),
  }),
  execute: externalApprovalTool,
});


// Agent that prepares the request
const prepareRequest = new LlmAgent({
    name: 'PrepareApproval',
    instruction: 'Prepare the approval request details based on user input. Store amount and reason in state.',
    // ... likely sets state['approval_amount'] and state['approval_reason'] ...
});

// Agent that calls the human approval tool
const requestApproval = new LlmAgent({
    name: 'RequestHumanApproval',
    instruction: 'Use the external_approval_tool with amount from state["approval_amount"] and reason from state["approval_reason"].',
    tools: [approvalTool],
    outputKey: 'human_decision'
});

// Agent that proceeds based on human decision
const processDecision = new LlmAgent({
    name: 'ProcessDecision',
    instruction: 'Check {human_decision}. If "approved", proceed. If "rejected", inform user.'
});

const approvalWorkflow = new SequentialAgent({
    name: 'HumanApprovalWorkflow',
    subAgents: [prepareRequest, requestApproval, processDecision]
});
```

```go
import (
    "google.golang.org/adk/v2/agent"
    "google.golang.org/adk/v2/agent/llmagent"
    "google.golang.org/adk/v2/agent/workflowagents/sequentialagent"
    "google.golang.org/adk/v2/tool"
)

// Conceptual Code: Using a Tool for Human Approval
// --- Assume externalApprovalTool exists ---
// func externalApprovalTool(amount float64, reason string) (string, error) { ... }
type externalApprovalToolArgs struct {
    Amount float64 `json:"amount" jsonschema:"The amount for which approval is requested."`
    Reason string  `json:"reason" jsonschema:"The reason for the approval request."`
}
var externalApprovalTool func(agent.Context, externalApprovalToolArgs) (string, error)
approvalTool, _ := functiontool.New(
    functiontool.Config{
        Name:        "external_approval_tool",
        Description: "Sends a request for human approval.",
    },
    externalApprovalTool,
)

prepareRequest, _ := llmagent.New(llmagent.Config{
    Name:        "PrepareApproval",
    Instruction: "Prepare the approval request details based on user input. Store amount and reason in state.",
    Model:       m,
})

requestApproval, _ := llmagent.New(llmagent.Config{
    Name:        "RequestHumanApproval",
    Instruction: "Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].",
    Tools:       []tool.Tool{approvalTool},
    OutputKey:   "human_decision",
    Model:       m,
})

processDecision, _ := llmagent.New(llmagent.Config{
    Name:        "ProcessDecision",
    Instruction: "Check {human_decision}. If 'approved', proceed. If 'rejected', inform user.",
    Model:       m,
})

approvalWorkflow, _ := sequentialagent.New(sequentialagent.Config{
    AgentConfig: agent.Config{Name: "HumanApprovalWorkflow", SubAgents: []agent.Agent{prepareRequest, requestApproval, processDecision}},
})
```

```java
// Conceptual Code: Using a Tool for Human Approval
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.SequentialAgent;
import com.google.adk.tools.FunctionTool;


// --- Assume external_approval_tool exists ---
// This tool would:
// 1. Take details (e.g., request_id, amount, reason).
// 2. Send these details to a human review system (e.g., via API).
// 3. Poll or wait for the human response (approved/rejected).
// 4. Return the human's decision.
// public boolean externalApprovalTool(float amount, String reason) { ... }
FunctionTool approvalTool = FunctionTool.create(externalApprovalTool);


// Agent that prepares the request
LlmAgent prepareRequest = LlmAgent.builder()
    .name("PrepareApproval")
    .instruction("Prepare the approval request details based on user input. Store amount and reason in state.")
    // ... likely sets state['approval_amount'] and state['approval_reason'] ...
    .build();


// Agent that calls the human approval tool
LlmAgent requestApproval = LlmAgent.builder()
    .name("RequestHumanApproval")
    .instruction("Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].")
    .tools(approvalTool)
    .outputKey("human_decision")
    .build();


// Agent that proceeds based on human decision
LlmAgent processDecision = LlmAgent.builder()
    .name("ProcessDecision")
    .instruction("Check {human_decision}. If 'approved', proceed. If 'rejected', inform user.")
    .build();


SequentialAgent approvalWorkflow = SequentialAgent.builder()
    .name("HumanApprovalWorkflow")
    .subAgents(prepareRequest, requestApproval, processDecision)
    .build();
```

```kotlin
class ExternalApprovalTool : BaseTool(
    "external_approval_tool",
    "Sends a request for human approval.",
) {
    override fun declaration(): FunctionDeclaration =
        FunctionDeclaration(
            "external_approval_tool",
            "Sends a request for human approval.",
        )

    override suspend fun run(
        context: ToolContext,
        args: Map<String, Any>,
    ): Any {
        // Simulate calling external system (e.g., UI, ticketing system)
        // In a real app, this might poll for a result or wait for a webhook.
        return mapOf("decision" to "approved")
    }
}
```

### Human in the loop with Policy

A more advanced and structured way to implement Human-in-the-Loop is by using a `PolicyEngine`. This approach allows you to define policies that can trigger a confirmation step from a user before a tool is executed. The `SecurityPlugin` intercepts a tool call, consults the `PolicyEngine`, and if the policy dictates, it will automatically request user confirmation. This pattern is more robust for enforcing governance and security rules.

Here's how it works:

1. **`SecurityPlugin`**: You add this plugin to your `Runner`. It acts as an interceptor for all tool calls.
1. **`BasePolicyEngine`**: You create a custom class that implements this interface. Its `evaluate()` method contains your logic to decide if a tool call needs confirmation.
1. **`PolicyOutcome.CONFIRM`**: When your `evaluate()` method returns this outcome, the `SecurityPlugin` pauses the tool execution and generates a special `FunctionCall` using `getAskUserConfirmationFunctionCalls`.
1. **Application Handling**: Your application code receives this special function call and presents the confirmation request to the user.
1. **User Confirmation**: Once the user confirms, your application sends a `FunctionResponse` back to the agent, which allows the `SecurityPlugin` to proceed with the original tool execution.

TypeScript Recommended Pattern

The Policy-based pattern is the recommended approach for implementing Human-in-the-Loop workflows in TypeScript. Support in other ADK languages is planned for future releases.

A conceptual example of using a `CustomPolicyEngine` to require user confirmation before executing any tool is shown below.

```typescript
const rootAgent = new LlmAgent({
  name: 'weather_time_agent',
  model: 'gemini-flash-latest',
  description:
      'Agent to answer questions about the time and weather in a city.',
  instruction:
      'You are a helpful agent who can answer user questions about the time and weather in a city.',
  tools: [getWeatherTool],
});

class CustomPolicyEngine implements BasePolicyEngine {
  async evaluate(_context: ToolCallPolicyContext): Promise<PolicyCheckResult> {
    // Default permissive implementation
    return Promise.resolve({
      outcome: PolicyOutcome.CONFIRM,
      reason: 'Needs confirmation for tool call',
    });
  }
}

const runner = new InMemoryRunner({
    agent: rootAgent,
    appName,
    plugins: [new SecurityPlugin({policyEngine: new CustomPolicyEngine()})]
});
```

You can find the full code sample [here](https://github.com/google/adk-docs/blob/main/examples/typescript/snippets/agents/workflow-agents/hitl_confirmation_agent.ts).
