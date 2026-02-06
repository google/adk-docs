# LLM Agent

Supported in ADK Python v0.1.0 Typescript v0.2.0 Go v0.1.0 Java v0.1.0

The `LlmAgent` (often aliased simply as `Agent`) is a core component in ADK, acting as the "thinking" part of your application. It leverages the power of a Large Language Model (LLM) for reasoning, understanding natural language, making decisions, generating responses, and interacting with tools.

Unlike deterministic [Workflow Agents](https://google.github.io/adk-docs/agents/workflow-agents/index.md) that follow predefined execution paths, `LlmAgent` behavior is non-deterministic. It uses the LLM to interpret instructions and context, deciding dynamically how to proceed, which tools to use (if any), or whether to transfer control to another agent.

Building an effective `LlmAgent` involves defining its identity, clearly guiding its behavior through instructions, and equipping it with the necessary tools and capabilities.

## Defining the Agent's Identity and Purpose

First, you need to establish what the agent *is* and what it's *for*.

- **`name` (Required):** Every agent needs a unique string identifier. This `name` is crucial for internal operations, especially in multi-agent systems where agents need to refer to or delegate tasks to each other. Choose a descriptive name that reflects the agent's function (e.g., `customer_support_router`, `billing_inquiry_agent`). Avoid reserved names like `user`.
- **`description` (Optional, Recommended for Multi-Agent):** Provide a concise summary of the agent's capabilities. This description is primarily used by *other* LLM agents to determine if they should route a task to this agent. Make it specific enough to differentiate it from peers (e.g., "Handles inquiries about current billing statements," not just "Billing agent").
- **`model` (Required):** Specify the underlying LLM that will power this agent's reasoning. This is a string identifier like `"gemini-2.5-flash"`. The choice of model impacts the agent's capabilities, cost, and performance. See the [Models](/adk-docs/agents/models/) page for available options and considerations.

```python
# Example: Defining the basic identity
capital_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="capital_agent",
    description="Answers user questions about the capital city of a given country."
    # instruction and tools will be added next
)
```

```typescript
// Example: Defining the basic identity
const capitalAgent = new LlmAgent({
    model: 'gemini-2.5-flash',
    name: 'capital_agent',
    description: 'Answers user questions about the capital city of a given country.',
    // instruction and tools will be added next
});
```

```go
// Example: Defining the basic identity
agent, err := llmagent.New(llmagent.Config{
    Name:        "capital_agent",
    Model:       model,
    Description: "Answers user questions about the capital city of a given country.",
    // instruction and tools will be added next
})
```

```java
// Example: Defining the basic identity
LlmAgent capitalAgent =
    LlmAgent.builder()
        .model("gemini-2.5-flash")
        .name("capital_agent")
        .description("Answers user questions about the capital city of a given country.")
        // instruction and tools will be added next
        .build();
```

## Guiding the Agent: Instructions (`instruction`)

The `instruction` parameter is arguably the most critical for shaping an `LlmAgent`'s behavior. It's a string (or a function returning a string) that tells the agent:

- Its core task or goal.
- Its personality or persona (e.g., "You are a helpful assistant," "You are a witty pirate").
- Constraints on its behavior (e.g., "Only answer questions about X," "Never reveal Y").
- How and when to use its `tools`. You should explain the purpose of each tool and the circumstances under which it should be called, supplementing any descriptions within the tool itself.
- The desired format for its output (e.g., "Respond in JSON," "Provide a bulleted list").

**Tips for Effective Instructions:**

- **Be Clear and Specific:** Avoid ambiguity. Clearly state the desired actions and outcomes.
- **Use Markdown:** Improve readability for complex instructions using headings, lists, etc.
- **Provide Examples (Few-Shot):** For complex tasks or specific output formats, include examples directly in the instruction.
- **Guide Tool Use:** Don't just list tools; explain *when* and *why* the agent should use them.

**State:**

- The instruction is a string template, you can use the `{var}` syntax to insert dynamic values into the instruction.
- `{var}` is used to insert the value of the state variable named var.
- `{artifact.var}` is used to insert the text content of the artifact named var.
- If the state variable or artifact does not exist, the agent will raise an error. If you want to ignore the error, you can append a `?` to the variable name as in `{var?}`.

```python
# Example: Adding instructions
capital_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="capital_agent",
    description="Answers user questions about the capital city of a given country.",
    instruction="""You are an agent that provides the capital city of a country.
When a user asks for the capital of a country:
1. Identify the country name from the user's query.
2. Use the `get_capital_city` tool to find the capital.
3. Respond clearly to the user, stating the capital city.
Example Query: "What's the capital of {country}?"
Example Response: "The capital of France is Paris."
""",
    # tools will be added next
)
```

```typescript
// Example: Adding instructions
const capitalAgent = new LlmAgent({
    model: 'gemini-2.5-flash',
    name: 'capital_agent',
    description: 'Answers user questions about the capital city of a given country.',
    instruction: `You are an agent that provides the capital city of a country.
        When a user asks for the capital of a country:
        1. Identify the country name from the user's query.
        2. Use the \`getCapitalCity\` tool to find the capital.
        3. Respond clearly to the user, stating the capital city.
        Example Query: "What's the capital of {country}?"
        Example Response: "The capital of France is Paris."
        `,
    // tools will be added next
});
```

```go
    // Example: Adding instructions
    agent, err := llmagent.New(llmagent.Config{
        Name:        "capital_agent",
        Model:       model,
        Description: "Answers user questions about the capital city of a given country.",
        Instruction: `You are an agent that provides the capital city of a country.
When a user asks for the capital of a country:
1. Identify the country name from the user's query.
2. Use the 'get_capital_city' tool to find the capital.
3. Respond clearly to the user, stating the capital city.
Example Query: "What's the capital of {country}?"
Example Response: "The capital of France is Paris."`,
        // tools will be added next
    })
```

```java
// Example: Adding instructions
LlmAgent capitalAgent =
    LlmAgent.builder()
        .model("gemini-2.5-flash")
        .name("capital_agent")
        .description("Answers user questions about the capital city of a given country.")
        .instruction(
            """
            You are an agent that provides the capital city of a country.
            When a user asks for the capital of a country:
            1. Identify the country name from the user's query.
            2. Use the `get_capital_city` tool to find the capital.
            3. Respond clearly to the user, stating the capital city.
            Example Query: "What's the capital of {country}?"
            Example Response: "The capital of France is Paris."
            """)
        // tools will be added next
        .build();
```

*(Note: For instructions that apply to* all *agents in a system, consider using `global_instruction` on the root agent, detailed further in the [Multi-Agents](https://google.github.io/adk-docs/agents/multi-agents/index.md) section.)*

## Equipping the Agent: Tools (`tools`)

Tools give your `LlmAgent` capabilities beyond the LLM's built-in knowledge or reasoning. They allow the agent to interact with the outside world, perform calculations, fetch real-time data, or execute specific actions.

- **`tools` (Optional):** Provide a list of tools the agent can use. Each item in the list can be:
  - A native function or method (wrapped as a `FunctionTool`). Python ADK automatically wraps the native function into a `FunctionTool` whereas, you must explicitly wrap your Java methods using `FunctionTool.create(...)`
  - An instance of a class inheriting from `BaseTool`.
  - An instance of another agent (`AgentTool`, enabling agent-to-agent delegation - see [Multi-Agents](https://google.github.io/adk-docs/agents/multi-agents/index.md)).

The LLM uses the function/tool names, descriptions (from docstrings or the `description` field), and parameter schemas to decide which tool to call based on the conversation and its instructions.

```python
# Define a tool function
def get_capital_city(country: str) -> str:
  """Retrieves the capital city for a given country."""
  # Replace with actual logic (e.g., API call, database lookup)
  capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
  return capitals.get(country.lower(), f"Sorry, I don't know the capital of {country}.")

# Add the tool to the agent
capital_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="capital_agent",
    description="Answers user questions about the capital city of a given country.",
    instruction="""You are an agent that provides the capital city of a country... (previous instruction text)""",
    tools=[get_capital_city] # Provide the function directly
)
```

```typescript
import {z} from 'zod';
import { LlmAgent, FunctionTool } from '@google/adk';

// Define the schema for the tool's input parameters
const getCapitalCityParamsSchema = z.object({
    country: z.string().describe('The country to get capital for.'),
});

// Define the tool function itself
async function getCapitalCity(params: z.infer<typeof getCapitalCityParamsSchema>): Promise<{ capitalCity: string }> {
const capitals: Record<string, string> = {
    'france': 'Paris',
    'japan': 'Tokyo',
    'canada': 'Ottawa',
};
const result = capitals[params.country.toLowerCase()] ??
    `Sorry, I don't know the capital of ${params.country}.`;
return {capitalCity: result}; // Tools must return an object
}

// Create an instance of the FunctionTool
const getCapitalCityTool = new FunctionTool({
    name: 'getCapitalCity',
    description: 'Retrieves the capital city for a given country.',
    parameters: getCapitalCityParamsSchema,
    execute: getCapitalCity,
});

// Add the tool to the agent
const capitalAgent = new LlmAgent({
    model: 'gemini-2.5-flash',
    name: 'capitalAgent',
    description: 'Answers user questions about the capital city of a given country.',
    instruction: 'You are an agent that provides the capital city of a country...', // Note: the full instruction is omitted for brevity
    tools: [getCapitalCityTool], // Provide the FunctionTool instance in an array
});
```

```go
// Define a tool function
type getCapitalCityArgs struct {
    Country string `json:"country" jsonschema:"The country to get the capital of."`
}
getCapitalCity := func(ctx tool.Context, args getCapitalCityArgs) (map[string]any, error) {
    // Replace with actual logic (e.g., API call, database lookup)
    capitals := map[string]string{"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
    capital, ok := capitals[strings.ToLower(args.Country)]
    if !ok {
        return nil, fmt.Errorf("Sorry, I don't know the capital of %s.", args.Country)
    }
    return map[string]any{"result": capital}, nil
}

// Add the tool to the agent
capitalTool, err := functiontool.New(
    functiontool.Config{
        Name:        "get_capital_city",
        Description: "Retrieves the capital city for a given country.",
    },
    getCapitalCity,
)
if err != nil {
    log.Fatal(err)
}
agent, err := llmagent.New(llmagent.Config{
    Name:        "capital_agent",
    Model:       model,
    Description: "Answers user questions about the capital city of a given country.",
    Instruction: "You are an agent that provides the capital city of a country... (previous instruction text)",
    Tools:       []tool.Tool{capitalTool},
})
```

```java
// Define a tool function
// Retrieves the capital city of a given country.
public static Map<String, Object> getCapitalCity(
        @Schema(name = "country", description = "The country to get capital for")
        String country) {
  // Replace with actual logic (e.g., API call, database lookup)
  Map<String, String> countryCapitals = new HashMap<>();
  countryCapitals.put("canada", "Ottawa");
  countryCapitals.put("france", "Paris");
  countryCapitals.put("japan", "Tokyo");

  String result =
          countryCapitals.getOrDefault(
                  country.toLowerCase(), "Sorry, I couldn't find the capital for " + country + ".");
  return Map.of("result", result); // Tools must return a Map
}

// Add the tool to the agent
FunctionTool capitalTool = FunctionTool.create(experiment.getClass(), "getCapitalCity");
LlmAgent capitalAgent =
    LlmAgent.builder()
        .model("gemini-2.5-flash")
        .name("capital_agent")
        .description("Answers user questions about the capital city of a given country.")
        .instruction("You are an agent that provides the capital city of a country... (previous instruction text)")
        .tools(capitalTool) // Provide the function wrapped as a FunctionTool
        .build();
```

Learn more about Tools in [Custom Tools](/adk-docs/tools-custom/).

## Advanced Configuration & Control

Beyond the core parameters, `LlmAgent` offers several options for finer control:

### Fine-Tuning LLM Generation (`generate_content_config`)

You can adjust how the underlying LLM generates responses using `generate_content_config`.

- **`generate_content_config` (Optional):** Pass an instance of [`google.genai.types.GenerateContentConfig`](https://googleapis.github.io/python-genai/genai.html#genai.types.GenerateContentConfig) to control parameters like `temperature` (randomness), `max_output_tokens` (response length), `top_p`, `top_k`, and safety settings.

```python
from google.genai import types

agent = LlmAgent(
    # ... other params
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2, # More deterministic output
        max_output_tokens=250,
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            )
        ]
    )
)
```

```typescript
import { GenerateContentConfig } from '@google/genai';

const generateContentConfig: GenerateContentConfig = {
    temperature: 0.2, // More deterministic output
    maxOutputTokens: 250,
};

const agent = new LlmAgent({
    // ... other params
    generateContentConfig,
});
```

```go
import "google.golang.org/genai"

temperature := float32(0.2)
agent, err := llmagent.New(llmagent.Config{
    Name:  "gen_config_agent",
    Model: model,
    GenerateContentConfig: &genai.GenerateContentConfig{
        Temperature:     &temperature,
        MaxOutputTokens: 250,
    },
})
```

```java
import com.google.genai.types.GenerateContentConfig;

LlmAgent agent =
    LlmAgent.builder()
        // ... other params
        .generateContentConfig(GenerateContentConfig.builder()
            .temperature(0.2F) // More deterministic output
            .maxOutputTokens(250)
            .build())
        .build();
```

### Structuring Data (`input_schema`, `output_schema`, `output_key`)

For scenarios requiring structured data exchange with an `LLM Agent`, the ADK provides mechanisms to define expected input and desired output formats using schema definitions.

- **`input_schema` (Optional):** Define a schema representing the expected input structure. If set, the user message content passed to this agent *must* be a JSON string conforming to this schema. Your instructions should guide the user or preceding agent accordingly.

- **`output_schema` (Optional):** Define a schema representing the desired output structure. If set, the agent's final response *must* be a JSON string conforming to this schema.

- **`output_key` (Optional):** Provide a string key. If set, the text content of the agent's *final* response will be automatically saved to the session's state dictionary under this key. This is useful for passing results between agents or steps in a workflow.

  - In Python, this might look like: `session.state[output_key] = agent_response_text`
  - In Java: `session.state().put(outputKey, agentResponseText)`
  - In Golang, within a callback handler: `ctx.State().Set(output_key, agentResponseText)`

The input and output schema is typically a `Pydantic` BaseModel.

```python
from pydantic import BaseModel, Field

class CapitalOutput(BaseModel):
    capital: str = Field(description="The capital of the country.")

structured_capital_agent = LlmAgent(
    # ... name, model, description
    instruction="""You are a Capital Information Agent. Given a country, respond ONLY with a JSON object containing the capital. Format: {"capital": "capital_name"}""",
    output_schema=CapitalOutput, # Enforce JSON output
    output_key="found_capital"  # Store result in state['found_capital']
    # Cannot use tools=[get_capital_city] effectively here
)
```

```typescript
import {z} from 'zod';
import { Schema, Type } from '@google/genai';

// Define the schema for the output
const CapitalOutputSchema: Schema = {
    type: Type.OBJECT,
    properties: {
        capital: {
            type: Type.STRING,
            description: 'The capital of the country.',
        },
    },
    required: ['capital'],
};

// Create the LlmAgent instance
const structuredCapitalAgent = new LlmAgent({
    // ... name, model, description
    instruction: `You are a Capital Information Agent. Given a country, respond ONLY with a JSON object containing the capital. Format: {"capital": "capital_name"}`,
    outputSchema: CapitalOutputSchema, // Enforce JSON output
    outputKey: 'found_capital', // Store result in state['found_capital']
    // Cannot use tools effectively here
});
```

The input and output schema is a `google.genai.types.Schema` object.

```go
capitalOutput := &genai.Schema{
    Type:        genai.TypeObject,
    Description: "Schema for capital city information.",
    Properties: map[string]*genai.Schema{
        "capital": {
            Type:        genai.TypeString,
            Description: "The capital city of the country.",
        },
    },
}

agent, err := llmagent.New(llmagent.Config{
    Name:         "structured_capital_agent",
    Model:        model,
    Description:  "Provides capital information in a structured format.",
    Instruction:  `You are a Capital Information Agent. Given a country, respond ONLY with a JSON object containing the capital. Format: {"capital": "capital_name"}`,
    OutputSchema: capitalOutput,
    OutputKey:    "found_capital",
    // Cannot use the capitalTool tool effectively here
})
```

The input and output schema is a `google.genai.types.Schema` object.

```java
private static final Schema CAPITAL_OUTPUT =
    Schema.builder()
        .type("OBJECT")
        .description("Schema for capital city information.")
        .properties(
            Map.of(
                "capital",
                Schema.builder()
                    .type("STRING")
                    .description("The capital city of the country.")
                    .build()))
        .build();

LlmAgent structuredCapitalAgent =
    LlmAgent.builder()
        // ... name, model, description
        .instruction(
                "You are a Capital Information Agent. Given a country, respond ONLY with a JSON object containing the capital. Format: {\"capital\": \"capital_name\"}")
        .outputSchema(capitalOutput) // Enforce JSON output
        .outputKey("found_capital") // Store result in state.get("found_capital")
        // Cannot use tools(getCapitalCity) effectively here
        .build();
```

### Managing Context (`include_contents`)

Control whether the agent receives the prior conversation history.

- **`include_contents` (Optional, Default: `'default'`):** Determines if the `contents` (history) are sent to the LLM.
  - `'default'`: The agent receives the relevant conversation history.
  - `'none'`: The agent receives no prior `contents`. It operates based solely on its current instruction and any input provided in the *current* turn (useful for stateless tasks or enforcing specific contexts).

```python
stateless_agent = LlmAgent(
    # ... other params
    include_contents='none'
)
```

```typescript
const statelessAgent = new LlmAgent({
    // ... other params
    includeContents: 'none',
});
```

```go
import "google.golang.org/adk/agent/llmagent"

agent, err := llmagent.New(llmagent.Config{
    Name:            "stateless_agent",
    Model:           model,
    IncludeContents: llmagent.IncludeContentsNone,
})
```

```java
import com.google.adk.agents.LlmAgent.IncludeContents;

LlmAgent statelessAgent =
    LlmAgent.builder()
        // ... other params
        .includeContents(IncludeContents.NONE)
        .build();
```

### Planner

Supported in ADKPython v0.1.0

**`planner` (Optional):** Assign a `BasePlanner` instance to enable multi-step reasoning and planning before execution. There are two main planners:

- **`BuiltInPlanner`:** Leverages the model's built-in planning capabilities (e.g., Gemini's thinking feature). See [Gemini Thinking](https://ai.google.dev/gemini-api/docs/thinking) for details and examples.

  Here, the `thinking_budget` parameter guides the model on the number of thinking tokens to use when generating a response. The `include_thoughts` parameter controls whether the model should include its raw thoughts and internal reasoning process in the response.

  ```python
  from google.adk import Agent
  from google.adk.planners import BuiltInPlanner
  from google.genai import types

  my_agent = Agent(
      model="gemini-2.5-flash",
      planner=BuiltInPlanner(
          thinking_config=types.ThinkingConfig(
              include_thoughts=True,
              thinking_budget=1024,
          )
      ),
      # ... your tools here
  )
  ```

- **`PlanReActPlanner`:** This planner instructs the model to follow a specific structure in its output: first create a plan, then execute actions (like calling tools), and provide reasoning for its steps. *It's particularly useful for models that don't have a built-in "thinking" feature*.

  ```python
  from google.adk import Agent
  from google.adk.planners import PlanReActPlanner

  my_agent = Agent(
      model="gemini-2.5-flash",
      planner=PlanReActPlanner(),
      # ... your tools here
  )
  ```

  The agent's response will follow a structured format:

  ```text
  [user]: ai news
  [google_search_agent]: /*PLANNING*/
  1. Perform a Google search for "latest AI news" to get current updates and headlines related to artificial intelligence.
  2. Synthesize the information from the search results to provide a summary of recent AI news.

  /*ACTION*/
  /*REASONING*/
  The search results provide a comprehensive overview of recent AI news, covering various aspects like company developments, research breakthroughs, and applications. I have enough information to answer the user's request.

  /*FINAL_ANSWER*/
  Here's a summary of recent AI news:
  ....
  ```

Example for using built-in-planner:

```python
from dotenv import load_dotenv


import asyncio
import os

from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.planners import BasePlanner, BuiltInPlanner, PlanReActPlanner
from google.adk.models import LlmRequest

from google.genai.types import ThinkingConfig
from google.genai.types import GenerateContentConfig

import datetime
from zoneinfo import ZoneInfo

APP_NAME = "weather_app"
USER_ID = "1234"
SESSION_ID = "session1234"

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}

# Step 1: Create a ThinkingConfig
thinking_config = ThinkingConfig(
    include_thoughts=True,   # Ask the model to include its thoughts in the response
    thinking_budget=256      # Limit the 'thinking' to 256 tokens (adjust as needed)
)
print("ThinkingConfig:", thinking_config)

# Step 2: Instantiate BuiltInPlanner
planner = BuiltInPlanner(
    thinking_config=thinking_config
)
print("BuiltInPlanner created.")

# Step 3: Wrap the planner in an LlmAgent
agent = LlmAgent(
    model="gemini-2.5-pro-preview-03-25",  # Set your model name
    name="weather_and_time_agent",
    instruction="You are an agent that returns time and weather",
    planner=planner,
    tools=[get_weather, get_current_time]
)

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        print(f"\nDEBUG EVENT: {event}\n")
        if event.is_final_response() and event.content:
            final_answer = event.content.parts[0].text.strip()
            print("\n🟢 FINAL ANSWER\n", final_answer, "\n")

call_agent("If it's raining in New York right now, what is the current temperature?")
```

### Code Execution

Supported in ADKPython v0.1.0Java v0.1.0

- **`code_executor` (Optional):** Provide a `BaseCodeExecutor` instance to allow the agent to execute code blocks found in the LLM's response. For more information, see [Code Execution with Gemini API](/adk-docs/tools/gemini-api/code-execution/).

````python
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.code_executors import BuiltInCodeExecutor
from google.genai import types

AGENT_NAME = "calculator_agent"
APP_NAME = "calculator"
USER_ID = "user1234"
SESSION_ID = "session_code_exec_async"
GEMINI_MODEL = "gemini-2.0-flash"

# Agent Definition
code_agent = LlmAgent(
    name=AGENT_NAME,
    model=GEMINI_MODEL,
    code_executor=BuiltInCodeExecutor(),
    instruction="""You are a calculator agent.
    When given a mathematical expression, write and execute Python code to calculate the result.
    Return only the final numerical result as plain text, without markdown or code blocks.
    """,
    description="Executes Python code to perform calculations.",
)

# Session and Runner
session_service = InMemorySessionService()
session = asyncio.run(session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
))
runner = Runner(agent=code_agent, app_name=APP_NAME,
                session_service=session_service)

# Agent Interaction (Async)
async def call_agent_async(query):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(f"\n--- Running Query: {query} ---")
    final_response_text = "No final text response captured."
    try:
        # Use run_async
        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=content
        ):
            print(f"Event ID: {event.id}, Author: {event.author}")

            # --- Check for specific parts FIRST ---
            has_specific_part = False
            if event.content and event.content.parts:
                for part in event.content.parts:  # Iterate through all parts
                    if part.executable_code:
                        # Access the actual code string via .code
                        print(
                            f"  Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```"
                        )
                        has_specific_part = True
                    elif part.code_execution_result:
                        # Access outcome and output correctly
                        print(
                            f"  Debug: Code Execution Result: {part.code_execution_result.outcome} - Output:\n{part.code_execution_result.output}"
                        )
                        has_specific_part = True
                    # Also print any text parts found in any event for debugging
                    elif part.text and not part.text.isspace():
                        print(f"  Text: '{part.text.strip()}'")
                        # Do not set has_specific_part=True here, as we want the final response logic below

            # --- Check for final response AFTER specific parts ---
            # Only consider it final if it doesn't have the specific code parts we just handled
            if not has_specific_part and event.is_final_response():
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    final_response_text = event.content.parts[0].text.strip()
                    print(f"==> Final Agent Response: {final_response_text}")
                else:
                    print(
                        "==> Final Agent Response: [No text content in final event]")

    except Exception as e:
        print(f"ERROR during agent run: {e}")
    print("-" * 30)


# Main async function to run the examples
async def main():
    await call_agent_async("Calculate the value of (5 + 7) * 3")
    await call_agent_async("What is 10 factorial?")


# Execute the main async function
try:
    asyncio.run(main())
except RuntimeError as e:
    # Handle specific error when running asyncio.run in an already running loop (like Jupyter/Colab)
    if "cannot be called from a running event loop" in str(e):
        print("\nRunning in an existing event loop (like Colab/Jupyter).")
        print("Please run `await main()` in a notebook cell instead.")
        # If in an interactive environment like a notebook, you might need to run:
        # await main()
    else:
        raise e  # Re-raise other runtime errors
````

````java
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.BuiltInCodeExecutionTool;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Part;

public class CodeExecutionAgentApp {

  private static final String AGENT_NAME = "calculator_agent";
  private static final String APP_NAME = "calculator";
  private static final String USER_ID = "user1234";
  private static final String SESSION_ID = "session_code_exec_sync";
  private static final String GEMINI_MODEL = "gemini-2.0-flash";

  /**
   * Calls the agent with a query and prints the interaction events and final response.
   *
   * @param runner The runner instance for the agent.
   * @param query The query to send to the agent.
   */
  public static void callAgent(Runner runner, String query) {
    Content content =
        Content.builder().role("user").parts(ImmutableList.of(Part.fromText(query))).build();

    InMemorySessionService sessionService = (InMemorySessionService) runner.sessionService();
    Session session =
        sessionService
            .createSession(APP_NAME, USER_ID, /* state= */ null, SESSION_ID)
            .blockingGet();

    System.out.println("\n--- Running Query: " + query + " ---");
    final String[] finalResponseText = {"No final text response captured."};

    try {
      runner
          .runAsync(session.userId(), session.id(), content)
          .forEach(
              event -> {
                System.out.println("Event ID: " + event.id() + ", Author: " + event.author());

                boolean hasSpecificPart = false;
                if (event.content().isPresent() && event.content().get().parts().isPresent()) {
                  for (Part part : event.content().get().parts().get()) {
                    if (part.executableCode().isPresent()) {
                      System.out.println(
                          "  Debug: Agent generated code:\n```python\n"
                              + part.executableCode().get().code()
                              + "\n```");
                      hasSpecificPart = true;
                    } else if (part.codeExecutionResult().isPresent()) {
                      System.out.println(
                          "  Debug: Code Execution Result: "
                              + part.codeExecutionResult().get().outcome()
                              + " - Output:\n"
                              + part.codeExecutionResult().get().output());
                      hasSpecificPart = true;
                    } else if (part.text().isPresent() && !part.text().get().trim().isEmpty()) {
                      System.out.println("  Text: '" + part.text().get().trim() + "'");
                    }
                  }
                }

                if (!hasSpecificPart && event.finalResponse()) {
                  if (event.content().isPresent()
                      && event.content().get().parts().isPresent()
                      && !event.content().get().parts().get().isEmpty()
                      && event.content().get().parts().get().get(0).text().isPresent()) {
                    finalResponseText[0] =
                        event.content().get().parts().get().get(0).text().get().trim();
                    System.out.println("==> Final Agent Response: " + finalResponseText[0]);
                  } else {
                    System.out.println(
                        "==> Final Agent Response: [No text content in final event]");
                  }
                }
              });
    } catch (Exception e) {
      System.err.println("ERROR during agent run: " + e.getMessage());
      e.printStackTrace();
    }
    System.out.println("------------------------------");
  }

  public static void main(String[] args) {
    BuiltInCodeExecutionTool codeExecutionTool = new BuiltInCodeExecutionTool();

    BaseAgent codeAgent =
        LlmAgent.builder()
            .name(AGENT_NAME)
            .model(GEMINI_MODEL)
            .tools(ImmutableList.of(codeExecutionTool))
            .instruction(
                """
                                You are a calculator agent.
                                When given a mathematical expression, write and execute Python code to calculate the result.
                                Return only the final numerical result as plain text, without markdown or code blocks.
                                """)
            .description("Executes Python code to perform calculations.")
            .build();

    InMemorySessionService sessionService = new InMemorySessionService();
    Runner runner = new Runner(codeAgent, APP_NAME, null, sessionService);

    callAgent(runner, "Calculate the value of (5 + 7) * 3");
    callAgent(runner, "What is 10 factorial?");
  }
}
````

## Putting It Together: Example

Code

Here's the complete basic `capital_agent`:

```python
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# --- Full example code demonstrating LlmAgent with Tools vs. Output Schema ---
import json # Needed for pretty printing dicts
import asyncio 

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field

# --- 1. Define Constants ---
APP_NAME = "agent_comparison_app"
USER_ID = "test_user_456"
SESSION_ID_TOOL_AGENT = "session_tool_agent_xyz"
SESSION_ID_SCHEMA_AGENT = "session_schema_agent_xyz"
MODEL_NAME = "gemini-2.0-flash"

# --- 2. Define Schemas ---

# Input schema used by both agents
class CountryInput(BaseModel):
    country: str = Field(description="The country to get information about.")

# Output schema ONLY for the second agent
class CapitalInfoOutput(BaseModel):
    capital: str = Field(description="The capital city of the country.")
    # Note: Population is illustrative; the LLM will infer or estimate this
    # as it cannot use tools when output_schema is set.
    population_estimate: str = Field(description="An estimated population of the capital city.")

# --- 3. Define the Tool (Only for the first agent) ---
def get_capital_city(country: str) -> str:
    """Retrieves the capital city of a given country."""
    print(f"\n-- Tool Call: get_capital_city(country='{country}') --")
    country_capitals = {
        "united states": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "japan": "Tokyo",
    }
    result = country_capitals.get(country.lower(), f"Sorry, I couldn't find the capital for {country}.")
    print(f"-- Tool Result: '{result}' --")
    return result

# --- 4. Configure Agents ---

# Agent 1: Uses a tool and output_key
capital_agent_with_tool = LlmAgent(
    model=MODEL_NAME,
    name="capital_agent_tool",
    description="Retrieves the capital city using a specific tool.",
    instruction="""You are a helpful agent that provides the capital city of a country using a tool.
The user will provide the country name in a JSON format like {"country": "country_name"}.
1. Extract the country name.
2. Use the `get_capital_city` tool to find the capital.
3. Respond clearly to the user, stating the capital city found by the tool.
""",
    tools=[get_capital_city],
    input_schema=CountryInput,
    output_key="capital_tool_result", # Store final text response
)

# Agent 2: Uses output_schema (NO tools possible)
structured_info_agent_schema = LlmAgent(
    model=MODEL_NAME,
    name="structured_info_agent_schema",
    description="Provides capital and estimated population in a specific JSON format.",
    instruction=f"""You are an agent that provides country information.
The user will provide the country name in a JSON format like {{"country": "country_name"}}.
Respond ONLY with a JSON object matching this exact schema:
{json.dumps(CapitalInfoOutput.model_json_schema(), indent=2)}
Use your knowledge to determine the capital and estimate the population. Do not use any tools.
""",
    # *** NO tools parameter here - using output_schema prevents tool use ***
    input_schema=CountryInput,
    output_schema=CapitalInfoOutput, # Enforce JSON output structure
    output_key="structured_info_result", # Store final JSON response
)

# --- 5. Set up Session Management and Runners ---
session_service = InMemorySessionService()

# Create a runner for EACH agent
capital_runner = Runner(
    agent=capital_agent_with_tool,
    app_name=APP_NAME,
    session_service=session_service
)
structured_runner = Runner(
    agent=structured_info_agent_schema,
    app_name=APP_NAME,
    session_service=session_service
)

# --- 6. Define Agent Interaction Logic ---
async def call_agent_and_print(
    runner_instance: Runner,
    agent_instance: LlmAgent,
    session_id: str,
    query_json: str
):
    """Sends a query to the specified agent/runner and prints results."""
    print(f"\n>>> Calling Agent: '{agent_instance.name}' | Query: {query_json}")

    user_content = types.Content(role='user', parts=[types.Part(text=query_json)])

    final_response_content = "No final response received."
    async for event in runner_instance.run_async(user_id=USER_ID, session_id=session_id, new_message=user_content):
        # print(f"Event: {event.type}, Author: {event.author}") # Uncomment for detailed logging
        if event.is_final_response() and event.content and event.content.parts:
            # For output_schema, the content is the JSON string itself
            final_response_content = event.content.parts[0].text

    print(f"<<< Agent '{agent_instance.name}' Response: {final_response_content}")

    current_session = await session_service.get_session(app_name=APP_NAME,
                                                  user_id=USER_ID,
                                                  session_id=session_id)
    stored_output = current_session.state.get(agent_instance.output_key)

    # Pretty print if the stored output looks like JSON (likely from output_schema)
    print(f"--- Session State ['{agent_instance.output_key}']: ", end="")
    try:
        # Attempt to parse and pretty print if it's JSON
        parsed_output = json.loads(stored_output)
        print(json.dumps(parsed_output, indent=2))
    except (json.JSONDecodeError, TypeError):
         # Otherwise, print as string
        print(stored_output)
    print("-" * 30)


# --- 7. Run Interactions ---
async def main():
    # Create separate sessions for clarity, though not strictly necessary if context is managed
    print("--- Creating Sessions ---")
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_TOOL_AGENT)
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_SCHEMA_AGENT)

    print("--- Testing Agent with Tool ---")
    await call_agent_and_print(capital_runner, capital_agent_with_tool, SESSION_ID_TOOL_AGENT, '{"country": "France"}')
    await call_agent_and_print(capital_runner, capital_agent_with_tool, SESSION_ID_TOOL_AGENT, '{"country": "Canada"}')

    print("\n\n--- Testing Agent with Output Schema (No Tool Use) ---")
    await call_agent_and_print(structured_runner, structured_info_agent_schema, SESSION_ID_SCHEMA_AGENT, '{"country": "France"}')
    await call_agent_and_print(structured_runner, structured_info_agent_schema, SESSION_ID_SCHEMA_AGENT, '{"country": "Japan"}')

# --- Run the Agent ---
# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
if __name__ == "__main__":
    asyncio.run(main())
```

```javascript
// Copyright 2025 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { LlmAgent, FunctionTool, InMemoryRunner, isFinalResponse } from '@google/adk';
import { createUserContent, Schema, Type } from '@google/genai';
import type { Part } from '@google/genai';
 import { z } from 'zod';

// --- 1. Define Constants ---
const APP_NAME = "capital_app_ts";
const USER_ID = "test_user_789";
const SESSION_ID_TOOL_AGENT = "session_tool_agent_ts";
const SESSION_ID_SCHEMA_AGENT = "session_schema_agent_ts";
const MODEL_NAME = "gemini-2.5-flash"; // Using flash for speed

// --- 2. Define Schemas ---

// A. Schema for the Tool's parameters (using Zod)
const CountryInput = z.object({
    country: z.string().describe('The country to get the capital for.'),
});

// B. Output schema ONLY for the second agent (using ADK's Schema type)
const CapitalInfoOutputSchema: Schema = {
    type: Type.OBJECT,
    description: "Schema for capital city information.",
    properties: {
        capital: {
            type: Type.STRING,
            description: "The capital city of the country."
        },
        population_estimate: {
            type: Type.STRING,
            description: "An estimated population of the capital city."
        },
    },
    required: ["capital", "population_estimate"],
};


// --- 3. Define the Tool (Only for the first agent) ---
async function getCapitalCity(params: z.infer<typeof CountryInput>): Promise<{ result: string }> {
    console.log(`\n-- Tool Call: getCapitalCity(country='${params.country}') --`);
    const capitals: Record<string, string> = {
        'united states': 'Washington, D.C.',
        'canada': 'Ottawa',
        'france': 'Paris',
        'japan': 'Tokyo',
    };
    const result = capitals[params.country.toLowerCase()] ??
        `Sorry, I couldn't find the capital for ${params.country}.`;
    console.log(`-- Tool Result: '${result}' --`);
    return { result: result }; // Tools must return an object
}

// --- 4. Configure Agents ---

// Agent 1: Uses a tool and outputKey
const getCapitalCityTool = new FunctionTool({
    name: 'get_capital_city',
    description: 'Retrieves the capital city for a given country',
    parameters: CountryInput,
    execute: getCapitalCity,
});

const capitalAgentWithTool = new LlmAgent({
    model: MODEL_NAME,
    name: 'capital_agent_tool',
    description: 'Retrieves the capital city using a specific tool.',
    instruction: `You are a helpful agent that provides the capital city of a country using a tool.
The user will provide the country name in a JSON format like {"country": "country_name"}.
1. Extract the country name.
2. Use the \`get_capital_city\` tool to find the capital.
3. Respond with a JSON object with the key 'capital' and the value as the capital city.
`,
    tools: [getCapitalCityTool],
    outputKey: "capital_tool_result", // Store final text response
});

// Agent 2: Uses outputSchema (NO tools possible)
const structuredInfoAgentSchema = new LlmAgent({
    model: MODEL_NAME,
    name: 'structured_info_agent_schema',
    description: 'Provides capital and estimated population in a specific JSON format.',
    instruction: `You are an agent that provides country information.
The user will provide the country name in a JSON format like {"country": "country_name"}.
Respond ONLY with a JSON object matching this exact schema:
${JSON.stringify(CapitalInfoOutputSchema, null, 2)}
Use your knowledge to determine the capital and estimate the population. Do not use any tools.
`,
    // *** NO tools parameter here - using outputSchema prevents tool use ***
    outputSchema: CapitalInfoOutputSchema,
    outputKey: "structured_info_result",
});


// --- 5. Define Agent Interaction Logic ---
async function callAgentAndPrint(
    runner: InMemoryRunner,
    agent: LlmAgent,
    sessionId: string,
    queryJson: string
) {
    console.log(`\n>>> Calling Agent: '${agent.name}' | Query: ${queryJson}`);
    const message = createUserContent(queryJson);

    let finalResponseContent = "No final response received.";
    for await (const event of runner.runAsync({ userId: USER_ID, sessionId: sessionId, newMessage: message })) {
        if (isFinalResponse(event) && event.content?.parts?.length) {
            finalResponseContent = event.content.parts.map((part: Part) => part.text ?? '').join('');
        }
    }
    console.log(`<<< Agent '${agent.name}' Response: ${finalResponseContent}`);

    // Check the session state
    const currentSession = await runner.sessionService.getSession({ appName: APP_NAME, userId: USER_ID, sessionId: sessionId });
    if (!currentSession) {
        console.log(`--- Session not found: ${sessionId} ---`);
        return;
    }
    const storedOutput = currentSession.state[agent.outputKey!];

    console.log(`--- Session State ['${agent.outputKey}']: `);
    try {
        // Attempt to parse and pretty print if it's JSON
        const parsedOutput = JSON.parse(storedOutput as string);
        console.log(JSON.stringify(parsedOutput, null, 2));
    } catch (e) {
        // Otherwise, print as a string
        console.log(storedOutput);
    }
    console.log("-".repeat(30));
}

// --- 6. Run Interactions ---
async function main() {
    // Set up runners for each agent
    const capitalRunner = new InMemoryRunner({ appName: APP_NAME, agent: capitalAgentWithTool });
    const structuredRunner = new InMemoryRunner({ appName: APP_NAME, agent: structuredInfoAgentSchema });

    // Create sessions
    console.log("--- Creating Sessions ---");
    await capitalRunner.sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: SESSION_ID_TOOL_AGENT });
    await structuredRunner.sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: SESSION_ID_SCHEMA_AGENT });

    console.log("\n--- Testing Agent with Tool ---");
    await callAgentAndPrint(capitalRunner, capitalAgentWithTool, SESSION_ID_TOOL_AGENT, '{"country": "France"}');
    await callAgentAndPrint(capitalRunner, capitalAgentWithTool, SESSION_ID_TOOL_AGENT, '{"country": "Canada"}');

    console.log("\n\n--- Testing Agent with Output Schema (No Tool Use) ---");
    await callAgentAndPrint(structuredRunner, structuredInfoAgentSchema, SESSION_ID_SCHEMA_AGENT, '{"country": "France"}');
    await callAgentAndPrint(structuredRunner, structuredInfoAgentSchema, SESSION_ID_SCHEMA_AGENT, '{"country": "Japan"}');
}

main();
```

```go
package main

import (
    "context"
    "encoding/json"
    "errors"
    "fmt"
    "log"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"

    "google.golang.org/genai"
)

// --- Main Runnable Example ---

const (
    modelName = "gemini-2.0-flash"
    appName   = "agent_comparison_app"
    userID    = "test_user_456"
)

type getCapitalCityArgs struct {
    Country string `json:"country" jsonschema:"The country to get the capital of."`
}

// getCapitalCity retrieves the capital city of a given country.
func getCapitalCity(ctx tool.Context, args getCapitalCityArgs) (map[string]any, error) {
    fmt.Printf("\n-- Tool Call: getCapitalCity(country='%s') --\n", args.Country)
    capitals := map[string]string{
        "united states": "Washington, D.C.",
        "canada":        "Ottawa",
        "france":        "Paris",
        "japan":         "Tokyo",
    }
    capital, ok := capitals[strings.ToLower(args.Country)]
    if !ok {
        result := fmt.Sprintf("Sorry, I couldn't find the capital for %s.", args.Country)
        fmt.Printf("-- Tool Result: '%s' --\n", result)
        return nil, errors.New(result)
    }
    fmt.Printf("-- Tool Result: '%s' --\n", capital)
    return map[string]any{"result": capital}, nil
}

// callAgent is a helper function to execute an agent with a given prompt and handle its output.
func callAgent(ctx context.Context, a agent.Agent, outputKey string, prompt string) {
    fmt.Printf("\n>>> Calling Agent: '%s' | Query: %s\n", a.Name(), prompt)
    // Create an in-memory session service to manage agent state.
    sessionService := session.InMemoryService()

    // Create a new session for the agent interaction.
    sessionCreateResponse, err := sessionService.Create(ctx, &session.CreateRequest{
        AppName: appName,
        UserID:  userID,
    })
    if err != nil {
        log.Fatalf("Failed to create the session service: %v", err)
    }

    session := sessionCreateResponse.Session

    // Configure the runner with the application name, agent, and session service.
    config := runner.Config{
        AppName:        appName,
        Agent:          a,
        SessionService: sessionService,
    }

    // Create a new runner instance.
    r, err := runner.New(config)
    if err != nil {
        log.Fatalf("Failed to create the runner: %v", err)
    }

    // Prepare the user's message to send to the agent.
    sessionID := session.ID()
    userMsg := &genai.Content{
        Parts: []*genai.Part{
            genai.NewPartFromText(prompt),
        },
        Role: string(genai.RoleUser),
    }

    // Run the agent and process the streaming events.
    for event, err := range r.Run(ctx, userID, sessionID, userMsg, agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
    }) {
        if err != nil {
            fmt.Printf("\nAGENT_ERROR: %v\n", err)
        } else if event.Partial {
            // Print partial responses as they are received.
            for _, p := range event.Content.Parts {
                fmt.Print(p.Text)
            }
        }
    }

    // After the run, check if there's an expected output key in the session state.
    if outputKey != "" {
        storedOutput, error := session.State().Get(outputKey)
        if error == nil {
            // Pretty-print the stored output if it's a JSON string.
            fmt.Printf("\n--- Session State ['%s']: ", outputKey)
            storedString, isString := storedOutput.(string)
            if isString {
                var prettyJSON map[string]interface{}
                if err := json.Unmarshal([]byte(storedString), &prettyJSON); err == nil {
                    indentedJSON, err := json.MarshalIndent(prettyJSON, "", "  ")
                    if err == nil {
                        fmt.Println(string(indentedJSON))
                    } else {
                        fmt.Println(storedString)
                    }
                } else {
                    fmt.Println(storedString)
                }
            } else {
                fmt.Println(storedOutput)
            }
            fmt.Println(strings.Repeat("-", 30))
        }
    }
}

func main() {
    ctx := context.Background()

    model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("Failed to create model: %v", err)
    }

    capitalTool, err := functiontool.New(
        functiontool.Config{
            Name:        "get_capital_city",
            Description: "Retrieves the capital city for a given country.",
        },
        getCapitalCity,
    )
    if err != nil {
        log.Fatalf("Failed to create function tool: %v", err)
    }

    countryInputSchema := &genai.Schema{
        Type:        genai.TypeObject,
        Description: "Input for specifying a country.",
        Properties: map[string]*genai.Schema{
            "country": {
                Type:        genai.TypeString,
                Description: "The country to get information about.",
            },
        },
        Required: []string{"country"},
    }

    capitalAgentWithTool, err := llmagent.New(llmagent.Config{
        Name:        "capital_agent_tool",
        Model:       model,
        Description: "Retrieves the capital city using a specific tool.",
        Instruction: `You are a helpful agent that provides the capital city of a country using a tool.
The user will provide the country name in a JSON format like {"country": "country_name"}.
1. Extract the country name.
2. Use the 'get_capital_city' tool to find the capital.
3. Respond clearly to the user, stating the capital city found by the tool.`,
        Tools:       []tool.Tool{capitalTool},
        InputSchema: countryInputSchema,
        OutputKey:   "capital_tool_result",
    })
    if err != nil {
        log.Fatalf("Failed to create capital agent with tool: %v", err)
    }

    capitalInfoOutputSchema := &genai.Schema{
        Type:        genai.TypeObject,
        Description: "Schema for capital city information.",
        Properties: map[string]*genai.Schema{
            "capital": {
                Type:        genai.TypeString,
                Description: "The capital city of the country.",
            },
            "population_estimate": {
                Type:        genai.TypeString,
                Description: "An estimated population of the capital city.",
            },
        },
        Required: []string{"capital", "population_estimate"},
    }
    schemaJSON, _ := json.Marshal(capitalInfoOutputSchema)
    structuredInfoAgentSchema, err := llmagent.New(llmagent.Config{
        Name:        "structured_info_agent_schema",
        Model:       model,
        Description: "Provides capital and estimated population in a specific JSON format.",
        Instruction: fmt.Sprintf(`You are an agent that provides country information.
The user will provide the country name in a JSON format like {"country": "country_name"}.
Respond ONLY with a JSON object matching this exact schema:
%s
Use your knowledge to determine the capital and estimate the population. Do not use any tools.`, string(schemaJSON)),
        InputSchema:  countryInputSchema,
        OutputSchema: capitalInfoOutputSchema,
        OutputKey:    "structured_info_result",
    })
    if err != nil {
        log.Fatalf("Failed to create structured info agent: %v", err)
    }

    fmt.Println("--- Testing Agent with Tool ---")
    callAgent(ctx, capitalAgentWithTool, "capital_tool_result", `{"country": "France"}`)
    callAgent(ctx, capitalAgentWithTool, "capital_tool_result", `{"country": "Canada"}`)

    fmt.Println("\n\n--- Testing Agent with Output Schema (No Tool Use) ---")
    callAgent(ctx, structuredInfoAgentSchema, "structured_info_result", `{"country": "France"}`)
    callAgent(ctx, structuredInfoAgentSchema, "structured_info_result", `{"country": "Japan"}`)
}
```

```java
// --- Full example code demonstrating LlmAgent with Tools vs. Output Schema ---

import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations;
import com.google.adk.tools.FunctionTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import com.google.genai.types.Schema;
import io.reactivex.rxjava3.core.Flowable;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class LlmAgentExample {

  // --- 1. Define Constants ---
  private static final String MODEL_NAME = "gemini-2.0-flash";
  private static final String APP_NAME = "capital_agent_tool";
  private static final String USER_ID = "test_user_456";
  private static final String SESSION_ID_TOOL_AGENT = "session_tool_agent_xyz";
  private static final String SESSION_ID_SCHEMA_AGENT = "session_schema_agent_xyz";

  // --- 2. Define Schemas ---

  // Input schema used by both agents
  private static final Schema COUNTRY_INPUT_SCHEMA =
      Schema.builder()
          .type("OBJECT")
          .description("Input for specifying a country.")
          .properties(
              Map.of(
                  "country",
                  Schema.builder()
                      .type("STRING")
                      .description("The country to get information about.")
                      .build()))
          .required(List.of("country"))
          .build();

  // Output schema ONLY for the second agent
  private static final Schema CAPITAL_INFO_OUTPUT_SCHEMA =
      Schema.builder()
          .type("OBJECT")
          .description("Schema for capital city information.")
          .properties(
              Map.of(
                  "capital",
                  Schema.builder()
                      .type("STRING")
                      .description("The capital city of the country.")
                      .build(),
                  "population_estimate",
                  Schema.builder()
                      .type("STRING")
                      .description("An estimated population of the capital city.")
                      .build()))
          .required(List.of("capital", "population_estimate"))
          .build();

  // --- 3. Define the Tool (Only for the first agent) ---
  // Retrieves the capital city of a given country.
  public static Map<String, Object> getCapitalCity(
      @Annotations.Schema(name = "country", description = "The country to get capital for")
      String country) {
    System.out.printf("%n-- Tool Call: getCapitalCity(country='%s') --%n", country);
    Map<String, String> countryCapitals = new HashMap<>();
    countryCapitals.put("united states", "Washington, D.C.");
    countryCapitals.put("canada", "Ottawa");
    countryCapitals.put("france", "Paris");
    countryCapitals.put("japan", "Tokyo");

    String result =
        countryCapitals.getOrDefault(
            country.toLowerCase(), "Sorry, I couldn't find the capital for " + country + ".");
    System.out.printf("-- Tool Result: '%s' --%n", result);
    return Map.of("result", result); // Tools must return a Map
  }

  public static void main(String[] args){
    LlmAgentExample agentExample = new LlmAgentExample();
    FunctionTool capitalTool = FunctionTool.create(agentExample.getClass(), "getCapitalCity");

    // --- 4. Configure Agents ---

    // Agent 1: Uses a tool and output_key
    LlmAgent capitalAgentWithTool =
        LlmAgent.builder()
            .model(MODEL_NAME)
            .name("capital_agent_tool")
            .description("Retrieves the capital city using a specific tool.")
            .instruction(
              """
              You are a helpful agent that provides the capital city of a country using a tool.
              1. Extract the country name.
              2. Use the `get_capital_city` tool to find the capital.
              3. Respond clearly to the user, stating the capital city found by the tool.
              """)
            .tools(capitalTool)
            .inputSchema(COUNTRY_INPUT_SCHEMA)
            .outputKey("capital_tool_result") // Store final text response
            .build();

    // Agent 2: Uses an output schema
    LlmAgent structuredInfoAgentSchema =
        LlmAgent.builder()
            .model(MODEL_NAME)
            .name("structured_info_agent_schema")
            .description("Provides capital and estimated population in a specific JSON format.")
            .instruction(
                String.format("""
                You are an agent that provides country information.
                Respond ONLY with a JSON object matching this exact schema: %s
                Use your knowledge to determine the capital and estimate the population. Do not use any tools.
                """, CAPITAL_INFO_OUTPUT_SCHEMA.toJson()))
            // *** NO tools parameter here - using output_schema prevents tool use ***
            .inputSchema(COUNTRY_INPUT_SCHEMA)
            .outputSchema(CAPITAL_INFO_OUTPUT_SCHEMA) // Enforce JSON output structure
            .outputKey("structured_info_result") // Store final JSON response
            .build();

    // --- 5. Set up Session Management and Runners ---
    InMemorySessionService sessionService = new InMemorySessionService();

    sessionService.createSession(APP_NAME, USER_ID, null, SESSION_ID_TOOL_AGENT).blockingGet();
    sessionService.createSession(APP_NAME, USER_ID, null, SESSION_ID_SCHEMA_AGENT).blockingGet();

    Runner capitalRunner = new Runner(capitalAgentWithTool, APP_NAME, null, sessionService);
    Runner structuredRunner = new Runner(structuredInfoAgentSchema, APP_NAME, null, sessionService);

    // --- 6. Run Interactions ---
    System.out.println("--- Testing Agent with Tool ---");
    agentExample.callAgentAndPrint(
        capitalRunner, capitalAgentWithTool, SESSION_ID_TOOL_AGENT, "{\"country\": \"France\"}");
    agentExample.callAgentAndPrint(
        capitalRunner, capitalAgentWithTool, SESSION_ID_TOOL_AGENT, "{\"country\": \"Canada\"}");

    System.out.println("\n\n--- Testing Agent with Output Schema (No Tool Use) ---");
    agentExample.callAgentAndPrint(
        structuredRunner,
        structuredInfoAgentSchema,
        SESSION_ID_SCHEMA_AGENT,
        "{\"country\": \"France\"}");
    agentExample.callAgentAndPrint(
        structuredRunner,
        structuredInfoAgentSchema,
        SESSION_ID_SCHEMA_AGENT,
        "{\"country\": \"Japan\"}");
  }

  // --- 7. Define Agent Interaction Logic ---
  public void callAgentAndPrint(Runner runner, LlmAgent agent, String sessionId, String queryJson) {
    System.out.printf(
        "%n>>> Calling Agent: '%s' | Session: '%s' | Query: %s%n",
        agent.name(), sessionId, queryJson);

    Content userContent = Content.fromParts(Part.fromText(queryJson));
    final String[] finalResponseContent = {"No final response received."};
    Flowable<Event> eventStream = runner.runAsync(USER_ID, sessionId, userContent);

    // Stream event response
    eventStream.blockingForEach(event -> {
          if (event.finalResponse() && event.content().isPresent()) {
            event
                .content()
                .get()
                .parts()
                .flatMap(parts -> parts.isEmpty() ? Optional.empty() : Optional.of(parts.get(0)))
                .flatMap(Part::text)
                .ifPresent(text -> finalResponseContent[0] = text);
          }
        });

    System.out.printf("<<< Agent '%s' Response: %s%n", agent.name(), finalResponseContent[0]);

    // Retrieve the session again to get the updated state
    Session updatedSession =
        runner
            .sessionService()
            .getSession(APP_NAME, USER_ID, sessionId, Optional.empty())
            .blockingGet();

    if (updatedSession != null && agent.outputKey().isPresent()) {
      // Print to verify if the stored output looks like JSON (likely from output_schema)
      System.out.printf("--- Session State ['%s']: ", agent.outputKey().get());
      }
  }
}
```

*(This example demonstrates the core concepts. More complex agents might incorporate schemas, context control, planning, etc.)*

## Related Concepts (Deferred Topics)

While this page covers the core configuration of `LlmAgent`, several related concepts provide more advanced control and are detailed elsewhere:

- **Callbacks:** Intercepting execution points (before/after model calls, before/after tool calls) using `before_model_callback`, `after_model_callback`, etc. See [Callbacks](https://google.github.io/adk-docs/callbacks/types-of-callbacks/index.md).
- **Multi-Agent Control:** Advanced strategies for agent interaction, including planning (`planner`), controlling agent transfer (`disallow_transfer_to_parent`, `disallow_transfer_to_peers`), and system-wide instructions (`global_instruction`). See [Multi-Agents](https://google.github.io/adk-docs/agents/multi-agents/index.md).
