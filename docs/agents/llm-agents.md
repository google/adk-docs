# LLM Agent

The `LlmAgent` (often aliased simply as `Agent`) is a core component in ADK,
acting as the "thinking" part of your application. It leverages the power of a
Large Language Model (LLM) for reasoning, understanding natural language, making
decisions, generating responses, and interacting with tools.

Unlike deterministic [Workflow Agents](workflow-agents/index.md) that follow
predefined execution paths, `LlmAgent` behavior is non-deterministic. It uses
the LLM to interpret instructions and context, deciding dynamically how to
proceed, which tools to use (if any), or whether to transfer control to another
agent.

Building an effective `LlmAgent` involves defining its identity, clearly guiding
its behavior through instructions, and equipping it with the necessary tools and
capabilities.

## Defining the Agent's Identity and Purpose

First, you need to establish what the agent *is* and what it's *for*.

* **`name` (Required):** Every agent needs a unique string identifier. This
  `name` is crucial for internal operations, especially in multi-agent systems
  where agents need to refer to or delegate tasks to each other. Choose a
  descriptive name that reflects the agent's function (e.g.,
  `customer_support_router`, `billing_inquiry_agent`). Avoid reserved names like
  `user`.

* **`description` (Optional, Recommended for Multi-Agent):** Provide a concise
  summary of the agent's capabilities. This description is primarily used by
  *other* LLM agents to determine if they should route a task to this agent.
  Make it specific enough to differentiate it from peers (e.g., "Handles
  inquiries about current billing statements," not just "Billing agent").

* **`model` (Required):** Specify the underlying LLM that will power this
  agent's reasoning. This is a string identifier like `"gemini-2.0-flash"`. The
  choice of model impacts the agent's capabilities, cost, and performance. See
  the [Models](models.md) page for available options and considerations.

=== "Python"

    ```python
    # Example: Defining the basic identity
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="Answers user questions about the capital city of a given country."
        # instruction and tools will be added next
    )
    ```

=== "Java"

    ```java
    // Example: Defining the basic identity
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("Answers user questions about the capital city of a given country.")
            // instruction and tools will be added next
            .build();
    ```


## Guiding the Agent: Instructions (`instruction`)

The `instruction` parameter is arguably the most critical for shaping an
`LlmAgent`'s behavior. It's a string (or a function returning a string) that
tells the agent:

* Its core task or goal.
* Its personality or persona (e.g., "You are a helpful assistant," "You are a witty pirate").
* Constraints on its behavior (e.g., "Only answer questions about X," "Never reveal Y").
* How and when to use its `tools`. You should explain the purpose of each tool and the circumstances under which it should be called, supplementing any descriptions within the tool itself.
* The desired format for its output (e.g., "Respond in JSON," "Provide a bulleted list").

**Tips for Effective Instructions:**

* **Be Clear and Specific:** Avoid ambiguity. Clearly state the desired actions and outcomes.
* **Use Markdown:** Improve readability for complex instructions using headings, lists, etc.
* **Provide Examples (Few-Shot):** For complex tasks or specific output formats, include examples directly in the instruction.
* **Guide Tool Use:** Don't just list tools; explain *when* and *why* the agent should use them.

**State:**

* The instruction is a string template, you can use the `{var}` syntax to insert dynamic values into the instruction.
* `{var}` is used to insert the value of the state variable named var.
* `{artifact.var}` is used to insert the text content of the artifact named var.
* If the state variable or artifact does not exist, the agent will raise an error. If you want to ignore the error, you can append a `?` to the variable name as in `{var?}`.

=== "Python"

    ```python
    # Example: Adding instructions
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
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

=== "Java"

    ```java
    // Example: Adding instructions
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
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

*(Note: For instructions that apply to *all* agents in a system, consider using
`global_instruction` on the root agent, detailed further in the
[Multi-Agents](multi-agents.md) section.)*

## Equipping the Agent: Tools (`tools`)

Tools give your `LlmAgent` capabilities beyond the LLM's built-in knowledge or
reasoning. They allow the agent to interact with the outside world, perform
calculations, fetch real-time data, or execute specific actions.

* **`tools` (Optional):** Provide a list of tools the agent can use. Each item in the list can be:
    * A native function or method (wrapped as a `FunctionTool`). Python ADK automatically wraps the native function into a `FuntionTool` whereas, you must explicitly wrap your Java methods using `FunctionTool.create(...)`
    * An instance of a class inheriting from `BaseTool`.
    * An instance of another agent (`AgentTool`, enabling agent-to-agent delegation - see [Multi-Agents](multi-agents.md)).

The LLM uses the function/tool names, descriptions (from docstrings or the
`description` field), and parameter schemas to decide which tool to call based
on the conversation and its instructions.

=== "Python"

    ```python
    # Define a tool function
    def get_capital_city(country: str) -> str:
      """Retrieves the capital city for a given country."""
      # Replace with actual logic (e.g., API call, database lookup)
      capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
      return capitals.get(country.lower(), f"Sorry, I don't know the capital of {country}.")

    # Add the tool to the agent
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="Answers user questions about the capital city of a given country.",
        instruction="""You are an agent that provides the capital city of a country... (previous instruction text)""",
        tools=[get_capital_city] # Provide the function directly
    )
    ```

=== "Java"

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
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("Answers user questions about the capital city of a given country.")
            .instruction("You are an agent that provides the capital city of a country... (previous instruction text)")
            .tools(capitalTool) // Provide the function wrapped as a FunctionTool
            .build();
    ```

Learn more about Tools in the [Tools](../tools/index.md) section.

## Advanced Configuration & Control

Beyond the core parameters, `LlmAgent` offers several options for finer control:

### Configuring LLM Generation (`generate_content_config`) {#fine-tuning-llm-generation-generate_content_config}

You can adjust how the underlying LLM generates responses using `generate_content_config`.

* **`generate_content_config` (Optional):** Pass an instance of [`google.genai.types.GenerateContentConfig`](https://googleapis.github.io/python-genai/genai.html#genai.types.GenerateContentConfig) to control parameters like `temperature` (randomness), `max_output_tokens` (response length), `top_p`, `top_k`, and safety settings.

=== "Python"

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

=== "Java"

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

* **`input_schema` (Optional):** Define a schema representing the expected input structure. If set, the user message content passed to this agent *must* be a JSON string conforming to this schema. Your instructions should guide the user or preceding agent accordingly.

* **`output_schema` (Optional):** Define a schema representing the desired output structure. If set, the agent's final response *must* be a JSON string conforming to this schema.

* **`output_key` (Optional):** Provide a string key. If set, the text content of the agent's *final* response will be automatically saved to the session's state dictionary under this key. This is useful for passing results between agents or steps in a workflow.
    * In Python, this might look like: `session.state[output_key] = agent_response_text`
    * In Java: `session.state().put(outputKey, agentResponseText)`

=== "Python"

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

=== "Java"

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

* **`include_contents` (Optional, Default: `'default'`):** Determines if the `contents` (history) are sent to the LLM.
    * `'default'`: The agent receives the relevant conversation history.
    * `'none'`: The agent receives no prior `contents`. It operates based solely on its current instruction and any input provided in the *current* turn (useful for stateless tasks or enforcing specific contexts).

=== "Python"

    ```python
    stateless_agent = LlmAgent(
        # ... other params
        include_contents='none'
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent.IncludeContents;

    LlmAgent statelessAgent =
        LlmAgent.builder()
            // ... other params
            .includeContents(IncludeContents.NONE)
            .build();
    ```

### Context Compaction

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python. Java support is planned/ coming soon."}

For long-running conversations, the history of events can grow very large, leading to increased latency and cost. The ADK provides a context compaction feature to mitigate this. It summarizes the conversation history at regular intervals, reducing the context size sent to the LLM.

You can enable this feature by providing an `EventsCompactionConfig` when creating your `App`.

* **`events_compaction_config` (Optional):** An instance of `EventsCompactionConfig` to configure context compaction.
    * **`compaction_interval`:** The number of new user-initiated invocations that will trigger a compaction.
    * **`summarizer`:** An instance of a `BaseEventsSummarizer`. The `LlmEventSummarizer` is a good default choice.
    * **`overlap_size`:** The number of invocations to overlap between compaction windows to maintain context.

=== "Python"

    ```python
    from google.adk.apps import App, EventsCompactionConfig
    from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
    from google.adk.agents import LlmAgent

    # Define your agent
    my_agent = LlmAgent(
        # ... your agent configuration
    )

    # Configure context compaction
    compaction_config = EventsCompactionConfig(
        compaction_interval=2,
        summarizer=LlmEventSummarizer(model="gemini-1.5-flash"),
        overlap_size=1
    )

    # Create an App with the agent and compaction config
    my_app = App(
        agent=my_agent,
        events_compaction_config=compaction_config
    )
    ```

### Planner

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python. Java support is planned/ coming soon."}

**`planner` (Optional):** Assign a `BasePlanner` instance to enable multi-step reasoning and planning before execution. There are two main planners:

* **`BuiltInPlanner`:** Leverages the model's built-in planning capabilities (e.g., Gemini's thinking feature). See [Gemini Thinking](https://ai.google.dev/gemini-api/docs/thinking) for details and examples.

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
    
* **`PlanReActPlanner`:** This planner instructs the model to follow a specific structure in its output: first create a plan, then execute actions (like calling tools), and provide reasoning for its steps. *It's particularly useful for models that don't have a built-in "thinking" feature*.

    ```python
    from google.adk import Agent
    from google.adk.planners import PlanReActPlanner

    my_agent = Agent(
        model="gemini-2.0-flash",
        planner=PlanReActPlanner(),
        # ... your tools here
    )
    ```

    The agent's response will follow a structured format:

    ```
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

### Code Execution

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python. Java support is planned/ coming soon."}

* **`code_executor` (Optional):** Provide a `BaseCodeExecutor` instance to allow the agent to execute code blocks found in the LLM's response. ([See Tools/Built-in tools](../tools/built-in-tools.md)).

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

## Putting It Together: Example

??? "Code"
    Here's the complete basic `capital_agent`:

    === "Python"

        ```python
        --8<-- "examples/python/snippets/agents/llm-agent/capital_agent.py"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/LlmAgentExample.java:full_code"
        ```

_(This example demonstrates the core concepts. More complex agents might incorporate schemas, context control, planning, etc.)_

## Related Concepts (Deferred Topics)

While this page covers the core configuration of `LlmAgent`, several related concepts provide more advanced control and are detailed elsewhere:

* **Callbacks:** Intercepting execution points (before/after model calls, before/after tool calls) using `before_model_callback`, `after_model_callback`, etc. See [Callbacks](../callbacks/types-of-callbacks.md).
* **Multi-Agent Control:** Advanced strategies for agent interaction, including planning (`planner`), controlling agent transfer (`disallow_transfer_to_parent`, `disallow_transfer_to_peers`), and system-wide instructions (`global_instruction`). See [Multi-Agents](multi-agents.md).
