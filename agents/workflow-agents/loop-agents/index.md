# Loop agents

Supported in ADKPython v0.1.0Typescript v0.2.0Go v0.1.0Java v0.2.0

The `LoopAgent` is a workflow agent that executes its sub-agents in a loop (i.e. iteratively). It ***repeatedly runs* a sequence of agents** for a specified number of iterations or until a termination condition is met.

Use the `LoopAgent` when your workflow involves repetition or iterative refinement, such as revising code.

### Example

- You want to build an agent that can generate images of food, but sometimes when you want to generate a specific number of items (e.g. 5 bananas), it generates a different number of those items in the image, such as an image of 7 bananas. You have two tools: `Generate Image`, `Count Food Items`. Because you want to keep generating images until it either correctly generates the specified number of items, or after a certain number of iterations, you should build your agent using a `LoopAgent`.

As with other [workflow agents](https://google.github.io/adk-docs/agents/workflow-agents/index.md), the `LoopAgent` is not powered by an LLM, and is thus deterministic in how it executes. That being said, workflow agents are only concerned with their execution, such as in a loop, and not their internal logic; the tools or sub-agents of a workflow agent may or may not utilize LLMs.

### How it Works

When the `LoopAgent`'s `Run Async` method is called, it performs the following actions:

1. **Sub-Agent Execution:** It iterates through the Sub Agents list *in order*. For *each* sub-agent, it calls the agent's `Run Async` method.

1. **Termination Check:**

   *Crucially*, the `LoopAgent` itself does *not* inherently decide when to stop looping. You *must* implement a termination mechanism to prevent infinite loops. Common strategies include:

   - **Max Iterations**: Set a maximum number of iterations in the `LoopAgent`. **The loop will terminate after that many iterations**.
   - **Escalation from sub-agent**: Design one or more sub-agents to evaluate a condition (e.g., "Is the document quality good enough?", "Has a consensus been reached?"). If the condition is met, the sub-agent can signal termination (e.g., by raising a custom event, setting a flag in a shared context, or returning a specific value).

### Full Example: Iterative Document Improvement

Imagine a scenario where you want to iteratively improve a document:

- **Writer Agent:** An `LlmAgent` that generates or refines a draft on a topic.

- **Critic Agent:** An `LlmAgent` that critiques the draft, identifying areas for improvement.

  ```py
  LoopAgent(sub_agents=[WriterAgent, CriticAgent], max_iterations=5)
  ```

In this setup, the `LoopAgent` would manage the iterative process. The `CriticAgent` could be **designed to return a "STOP" signal when the document reaches a satisfactory quality level**, preventing further iterations. Alternatively, the `max iterations` parameter could be used to limit the process to a fixed number of cycles, or external logic could be implemented to make stop decisions. The **loop would run at most five times**, ensuring the iterative refinement doesn't continue indefinitely.

Full Code

````py
from google.adk.agents import LoopAgent, LlmAgent, SequentialAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext

# --- Constants ---
GEMINI_MODEL = "gemini-2.5-flash"

# --- State Keys ---
STATE_CURRENT_DOC = "current_document"
STATE_CRITICISM = "criticism"
# Define the exact phrase the Critic should use to signal completion
COMPLETION_PHRASE = "No major issues found."

# --- Tool Definition ---
def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end."""
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    # Return empty dict as tools should typically return JSON-serializable output
    return {}

# --- Before Agent Callback ---
def update_initial_topic_state(callback_context: CallbackContext):
    """Ensure 'initial_topic' is set in state before pipeline starts."""
    callback_context.state['initial_topic'] = callback_context.state.get('initial_topic', 'a robot developing unexpected emotions')

# --- Agent Definitions ---

# STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
initial_writer_agent = LlmAgent(
    name="InitialWriterAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    instruction=f"""
    You are a Creative Writing Assistant tasked with starting a story.
    Write a *very basic* first draft of a short story (just 1-2 simple sentences).
    Keep it plain and minimal - do NOT add descriptive language yet.
    Topic: {{initial_topic}}

    Output *only* the story/document text. Do not add introductions or explanations.
    """,
    description="Writes the initial document draft based on the topic, aiming for some initial substance.",
    output_key=STATE_CURRENT_DOC
)

# STEP 2a: Critic Agent (Inside the Refinement Loop)
critic_agent_in_loop = LlmAgent(
    name="CriticAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    instruction=f"""
    You are a Constructive Critic AI reviewing a short story draft.

    **Document to Review:**
    ```
    {{current_document}}
    ```

    **Completion Criteria (ALL must be met):**
    1. At least 4 sentences long
    2. Has a clear beginning, middle, and end
    3. Includes at least one descriptive detail (sensory or emotional)

    **Task:**
    Check the document against the criteria above.

    IF any criteria is NOT met, provide specific feedback on what to add or improve.
    Output *only* the critique text.

    IF ALL criteria are met, respond *exactly* with: "{COMPLETION_PHRASE}"
    """,
    description="Reviews the current draft, providing critique if clear improvements are needed, otherwise signals completion.",
    output_key=STATE_CRITICISM
)

# STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
refiner_agent_in_loop = LlmAgent(
    name="RefinerAgent",
    model=GEMINI_MODEL,
    # Relies solely on state via placeholders
    include_contents='none',
    instruction=f"""
    You are a Creative Writing Assistant refining a document based on feedback OR exiting the process.
    **Current Document:**
    ```
    {{current_document}}
    ```
    **Critique/Suggestions:**
    {{criticism}}

    **Task:**
    Analyze the 'Critique/Suggestions'.
    IF the critique is *exactly* "{COMPLETION_PHRASE}":
    You MUST call the 'exit_loop' function. Do not output any text.
    ELSE (the critique contains actionable feedback):
    Carefully apply the suggestions to improve the 'Current Document'. Output *only* the refined document text.

    Do not add explanations. Either output the refined document OR call the exit_loop function.
    """,
    description="Refines the document based on critique, or calls exit_loop if critique indicates completion.",
    tools=[exit_loop], # Provide the exit_loop tool
    output_key=STATE_CURRENT_DOC # Overwrites state['current_document'] with the refined version
)

# STEP 2: Refinement Loop Agent
refinement_loop = LoopAgent(
    name="RefinementLoop",
    # Agent order is crucial: Critique first, then Refine/Exit
    sub_agents=[
        critic_agent_in_loop,
        refiner_agent_in_loop,
    ],
    max_iterations=5 # Limit loops
)

# STEP 3: Overall Sequential Pipeline
# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = SequentialAgent(
    name="IterativeWritingPipeline",
    sub_agents=[
        initial_writer_agent, # Run first to create initial doc
        refinement_loop       # Then run the critique/refine loop
    ],
    before_agent_callback=update_initial_topic_state, # set initial topic in state
    description="Writes an initial document and then iteratively refines it with critique using an exit tool."
)
````

```typescript
// Part of agent.ts --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup

import { LoopAgent, LlmAgent, SequentialAgent, FunctionTool } from '@google/adk';
import { z } from 'zod';

// --- Constants ---
const GEMINI_MODEL = "gemini-2.5-flash";
const STATE_INITIAL_TOPIC = "initial_topic";

// --- State Keys ---
const STATE_CURRENT_DOC = "current_document";
const STATE_CRITICISM = "criticism";
// Define the exact phrase the Critic should use to signal completion
const COMPLETION_PHRASE = "No major issues found.";

// --- Tool Definition ---
const exitLoopTool = new FunctionTool({
    name: 'exit_loop',
    description: 'Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end.',
    parameters: z.object({}),
    execute: (input, toolContext) => {
        if (toolContext) {
            console.log(`  [Tool Call] exit_loop triggered by ${toolContext.agentName} with input: ${input}`);
            toolContext.actions.escalate = true;
        }
        return {};
    },
});

// --- Agent Definitions ---

// STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
const initialWriterAgent = new LlmAgent({
    name: "InitialWriterAgent",
    model: GEMINI_MODEL,
    includeContents: 'none',
    // MODIFIED Instruction: Ask for a slightly more developed start
    instruction: `You are a Creative Writing Assistant tasked with starting a story.
    Write the *first draft* of a short story (aim for 2-4 sentences).
    Base the content *only* on the topic provided below. Try to introduce a specific element (like a character, a setting detail, or a starting action) to make it engaging.
    Topic: {{${STATE_INITIAL_TOPIC}}}

    Output *only* the story/document text. Do not add introductions or explanations.
    `,
    description: "Writes the initial document draft based on the topic, aiming for some initial substance.",
    outputKey: STATE_CURRENT_DOC
});

// STEP 2a: Critic Agent (Inside the Refinement Loop)
const criticAgentInLoop = new LlmAgent({
    name: "CriticAgent",
    model: GEMINI_MODEL,
    includeContents: 'none',
    // MODIFIED Instruction: More nuanced completion criteria, look for clear improvement paths.
    instruction: `You are a Constructive Critic AI reviewing a short document draft (typically 2-6 sentences). Your goal is balanced feedback.

    **Document to Review:**

    {{current_document}}


    **Task:**
    Review the document for clarity, engagement, and basic coherence according to the initial topic (if known).

    IF you identify 1-2 *clear and actionable* ways the document could be improved to better capture the topic or enhance reader engagement (e.g., "Needs a stronger opening sentence", "Clarify the character's goal"):
    Provide these specific suggestions concisely. Output *only* the critique text.

    ELSE IF the document is coherent, addresses the topic adequately for its length, and has no glaring errors or obvious omissions:
    Respond *exactly* with the phrase "${COMPLETION_PHRASE}" and nothing else. It doesn't need to be perfect, just functionally complete for this stage. Avoid suggesting purely subjective stylistic preferences if the core is sound.

    Do not add explanations. Output only the critique OR the exact completion.
`,
    description: "Reviews the current draft, providing critique if clear improvements are needed, otherwise signals completion.",
    outputKey: STATE_CRITICISM
});


// STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
const refinerAgentInLoop = new LlmAgent({
    name: "RefinerAgent",
    model: GEMINI_MODEL,
    // Relies solely on state via placeholders
    includeContents: 'none',
    instruction: `You are a Creative Writing Assistant refining a document based on feedback OR exiting the process.
    **Current Document:**

    {{current_document}}

    **Critique/Suggestions:**
    {{criticism}}

    **Task:**
    Analyze the 'Critique/Suggestions'.
    IF the critique is *exactly* "${COMPLETION_PHRASE}":
    You MUST call the 'exit_loop' function. Do not output any text.
    ELSE (the critique contains actionable feedback):
    Carefully apply the suggestions to improve the 'Current Document'. Output *only* the refined document text.

    Do not add explanations. Either output the refined document OR call the exit_loop function.
`,
    tools: [exitLoopTool],
    description: "Refines the document based on critique, or calls exit_loop if critique indicates completion.",
    outputKey: STATE_CURRENT_DOC
});


// STEP 2: Refinement Loop Agent
const refinementLoop = new LoopAgent({
    name: "RefinementLoop",
    // Agent order is crucial: Critique first, then Refine/Exit
    subAgents: [
        criticAgentInLoop,
        refinerAgentInLoop,
    ],
    maxIterations: 5 // Limit loops
});

// STEP 3: Overall Sequential Pipeline
// For ADK tools compatibility, the root agent must be named `root_agent`
export const rootAgent = new SequentialAgent({
    name: "IterativeWritingPipeline",
    subAgents: [
        initialWriterAgent, // Run first to create initial doc
        refinementLoop       // Then run the critique/refine loop
    ],
    description: "Writes an initial document and then iteratively refines it with critique using an exit tool."
});
```

```go
// ExitLoopArgs defines the (empty) arguments for the ExitLoop tool.
type ExitLoopArgs struct{}

// ExitLoopResults defines the output of the ExitLoop tool.
type ExitLoopResults struct{}

// ExitLoop is a tool that signals the loop to terminate by setting Escalate to true.
func ExitLoop(ctx tool.Context, input ExitLoopArgs) (ExitLoopResults, error) {
    fmt.Printf("[Tool Call] exitLoop triggered by %s \n", ctx.AgentName())
    ctx.Actions().Escalate = true
    return ExitLoopResults{}, nil
}

func main() {
    ctx := context.Background()

    if err := runAgent(ctx, "Write a document about a cat"); err != nil {
        log.Fatalf("Agent execution failed: %v", err)
    }
}

func runAgent(ctx context.Context, prompt string) error {
    model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        return fmt.Errorf("failed to create model: %v", err)
    }

    // STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
    initialWriterAgent, err := llmagent.New(llmagent.Config{
        Name:        "InitialWriterAgent",
        Model:       model,
        Description: "Writes the initial document draft based on the topic.",
        Instruction: `You are a Creative Writing Assistant tasked with starting a story.
Write the *first draft* of a short story (aim for 2-4 sentences).
Base the content *only* on the topic provided in the user's prompt.
Output *only* the story/document text. Do not add introductions or explanations.`,
        OutputKey: stateDoc,
    })
    if err != nil {
        return fmt.Errorf("failed to create initial writer agent: %v", err)
    }

    // STEP 2a: Critic Agent (Inside the Refinement Loop)
    criticAgentInLoop, err := llmagent.New(llmagent.Config{
        Name:        "CriticAgent",
        Model:       model,
        Description: "Reviews the current draft, providing critique or signaling completion.",
        Instruction: fmt.Sprintf(`You are a Constructive Critic AI reviewing a short document draft.
**Document to Review:**
"""
{%s}
"""
**Task:**
Review the document.
IF you identify 1-2 *clear and actionable* ways it could be improved:
Provide these specific suggestions concisely. Output *only* the critique text.
ELSE IF the document is coherent and addresses the topic adequately:
Respond *exactly* with the phrase "%s" and nothing else.`, stateDoc, donePhrase),
        OutputKey: stateCrit,
    })
    if err != nil {
        return fmt.Errorf("failed to create critic agent: %v", err)
    }

    exitLoopTool, err := functiontool.New(
        functiontool.Config{
            Name:        "exitLoop",
            Description: "Call this function ONLY when the critique indicates no further changes are needed.",
        },
        ExitLoop,
    )
    if err != nil {
        return fmt.Errorf("failed to create exit loop tool: %v", err)
    }

    // STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
    refinerAgentInLoop, err := llmagent.New(llmagent.Config{
        Name:  "RefinerAgent",
        Model: model,
        Instruction: fmt.Sprintf(`You are a Creative Writing Assistant refining a document based on feedback OR exiting the process.
**Current Document:**

"""
{%s}
"""

**Critique/Suggestions:**
{%s}
**Task:**
Analyze the 'Critique/Suggestions'.
IF the critique is *exactly* "%s":
You MUST call the 'exitLoop' function. Do not output any text.
ELSE (the critique contains actionable feedback):
Carefully apply the suggestions to improve the 'Current Document'. Output *only* the refined document text.`, stateDoc, stateCrit, donePhrase),
        Description: "Refines the document based on critique, or calls exitLoop if critique indicates completion.",
        Tools:       []tool.Tool{exitLoopTool},
        OutputKey:   stateDoc,
    })
    if err != nil {
        return fmt.Errorf("failed to create refiner agent: %v", err)
    }

    // STEP 2: Refinement Loop Agent
    refinementLoop, err := loopagent.New(loopagent.Config{
        AgentConfig: agent.Config{
            Name:      "RefinementLoop",
            SubAgents: []agent.Agent{criticAgentInLoop, refinerAgentInLoop},
        },
        MaxIterations: 5,
    })
    if err != nil {
        return fmt.Errorf("failed to create loop agent: %v", err)
    }

    // STEP 3: Overall Sequential Pipeline
    iterativeWriterAgent, err := sequentialagent.New(sequentialagent.Config{
        AgentConfig: agent.Config{
            Name:      appName,
            SubAgents: []agent.Agent{initialWriterAgent, refinementLoop},
        },
    })
    if err != nil {
        return fmt.Errorf("failed to create sequential agent pipeline: %v", err)
    }
```

````java
import static com.google.adk.agents.LlmAgent.IncludeContents.NONE;

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.LoopAgent;
import com.google.adk.agents.SequentialAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Map;

public class LoopAgentExample {

  // --- Constants ---
  private static final String APP_NAME = "IterativeWritingPipeline";
  private static final String USER_ID = "test_user_456";
  private static final String MODEL_NAME = "gemini-2.0-flash";

  // --- State Keys ---
  private static final String STATE_CURRENT_DOC = "current_document";
  private static final String STATE_CRITICISM = "criticism";

  public static void main(String[] args) {
    LoopAgentExample loopAgentExample = new LoopAgentExample();
    loopAgentExample.runAgent("Write a document about a cat");
  }

  // --- Tool Definition ---
  @Schema(
      description =
          "Call this function ONLY when the critique indicates no further changes are needed,"
              + " signaling the iterative process should end.")
  public static Map<String, Object> exitLoop(@Schema(name = "toolContext") ToolContext toolContext) {
    System.out.printf("[Tool Call] exitLoop triggered by %s \n", toolContext.agentName());
    toolContext.actions().setEscalate(true);
    //  Return empty dict as tools should typically return JSON-serializable output
    return Map.of();
  }

  // --- Agent Definitions ---
  public void runAgent(String prompt) {
    // STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
    LlmAgent initialWriterAgent =
        LlmAgent.builder()
            .model(MODEL_NAME)
            .name("InitialWriterAgent")
            .description(
                "Writes the initial document draft based on the topic, aiming for some initial"
                    + " substance.")
            .instruction(
                """
                    You are a Creative Writing Assistant tasked with starting a story.
                    Write the *first draft* of a short story (aim for 2-4 sentences).
                    Base the content *only* on the topic provided below. Try to introduce a specific element (like a character, a setting detail, or a starting action) to make it engaging.

                    Output *only* the story/document text. Do not add introductions or explanations.
                """)
            .outputKey(STATE_CURRENT_DOC)
            .includeContents(NONE)
            .build();

    // STEP 2a: Critic Agent (Inside the Refinement Loop)
    LlmAgent criticAgentInLoop =
        LlmAgent.builder()
            .model(MODEL_NAME)
            .name("CriticAgent")
            .description(
                "Reviews the current draft, providing critique if clear improvements are needed,"
                    + " otherwise signals completion.")
            .instruction(
                """
                    You are a Constructive Critic AI reviewing a short document draft (typically 2-6 sentences). Your goal is balanced feedback.

                    **Document to Review:**
                    ```
                    {{current_document}}
                    ```

                    **Task:**
                    Review the document for clarity, engagement, and basic coherence according to the initial topic (if known).

                    IF you identify 1-2 *clear and actionable* ways the document could be improved to better capture the topic or enhance reader engagement (e.g., "Needs a stronger opening sentence", "Clarify the character's goal"):
                    Provide these specific suggestions concisely. Output *only* the critique text.

                    ELSE IF the document is coherent, addresses the topic adequately for its length, and has no glaring errors or obvious omissions:
                    Respond *exactly* with the phrase "No major issues found." and nothing else. It doesn't need to be perfect, just functionally complete for this stage. Avoid suggesting purely subjective stylistic preferences if the core is sound.

                    Do not add explanations. Output only the critique OR the exact completion phrase.
                    """)
            .outputKey(STATE_CRITICISM)
            .includeContents(NONE)
            .build();

    // STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
    LlmAgent refinerAgentInLoop =
        LlmAgent.builder()
            .model(MODEL_NAME)
            .name("RefinerAgent")
            .description(
                "Refines the document based on critique, or calls exitLoop if critique indicates"
                    + " completion.")
            .instruction(
                """
                    You are a Creative Writing Assistant refining a document based on feedback OR exiting the process.
                    **Current Document:**
                    ```
                    {{current_document}}
                    ```
                    **Critique/Suggestions:**
                    {{criticism}}

                    **Task:**
                    Analyze the 'Critique/Suggestions'.
                    IF the critique is *exactly* "No major issues found.":
                    You MUST call the 'exitLoop' function. Do not output any text.
                    ELSE (the critique contains actionable feedback):
                    Carefully apply the suggestions to improve the 'Current Document'. Output *only* the refined document text.

                    Do not add explanations. Either output the refined document OR call the exitLoop function.
                """)
            .outputKey(STATE_CURRENT_DOC)
            .includeContents(NONE)
            .tools(FunctionTool.create(LoopAgentExample.class, "exitLoop"))
            .build();

    // STEP 2: Refinement Loop Agent
    LoopAgent refinementLoop =
        LoopAgent.builder()
            .name("RefinementLoop")
            .description("Repeatedly refines the document with critique and then exits.")
            .subAgents(criticAgentInLoop, refinerAgentInLoop)
            .maxIterations(5)
            .build();

    // STEP 3: Overall Sequential Pipeline
    SequentialAgent iterativeWriterAgent =
        SequentialAgent.builder()
            .name(APP_NAME)
            .description(
                "Writes an initial document and then iteratively refines it with critique using an"
                    + " exit tool.")
            .subAgents(initialWriterAgent, refinementLoop)
            .build();

    // Create an InMemoryRunner
    InMemoryRunner runner = new InMemoryRunner(iterativeWriterAgent, APP_NAME);
    // InMemoryRunner automatically creates a session service. Create a session using the service
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();
    Content userMessage = Content.fromParts(Part.fromText(prompt));

    // Run the agent
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    // Stream event response
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
````
