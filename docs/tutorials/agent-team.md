# Build Your First Intelligent Agent Team: A Progressive Weather Bot with ADK

<a href="https://colab.research.google.com/github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" style="display: inline-flex; align-items: center; gap: 5px; text-decoration: none; color: #4285F4;">
  <img width="32px" src="https://www.gstatic.com/pantheon/images/bigquery/welcome_page/colab-logo.svg" alt="Google Colaboratory logo">
  <span>Open in Colab</span>
</a>

This tutorial extends from the [Multi-tool agent](/tutorials/multi-tool-agent/) project. Now, you're ready to dive deeper and construct a more sophisticated, **multi-agent system**.

We'll embark on building a **Weather Bot agent team**, progressively layering advanced features onto a simple foundation. Starting with a single agent that can look up weather, we will incrementally add capabilities like:

*   Leveraging different AI models (Gemini, GPT, Claude).
*   Designing specialized sub-agents for distinct tasks (like greetings and farewells).
*   Enabling intelligent delegation between agents.
*   Giving agents memory using persistent session state.
*   Implementing crucial safety guardrails using callbacks.

**Why a Weather Bot Team?**

This use case, while seemingly simple, provides a practical and relatable canvas to explore core ADK concepts essential for building complex, real-world agentic applications. You'll learn how to structure interactions, manage state, ensure safety, and orchestrate multiple AI "brains" working together.

**What is ADK Again?**

As a reminder, ADK is a Python framework designed to streamline the development of applications powered by Large Language Models (LLMs). It offers robust building blocks for creating agents that can reason, plan, utilize tools, interact dynamically with users, and collaborate effectively within a team.

**In this advanced tutorial, you will master:**

*   ✅ **Tool Definition & Usage:** Crafting Python functions (`tools`) that grant agents specific abilities (like fetching data) and instructing agents on how to use them effectively.
*   ✅ **Multi-LLM Flexibility:** Configuring agents to utilize various leading LLMs (Gemini, GPT-4o, Claude Sonnet) via LiteLLM integration, allowing you to choose the best model for each task.
*   ✅ **Agent Delegation & Collaboration:** Designing specialized sub-agents and enabling automatic routing (`auto flow`) of user requests to the most appropriate agent within a team.
*   ✅ **Session State for Memory:** Utilizing `Session State` and `ToolContext` to enable agents to remember information across conversational turns, leading to more contextual interactions.
*   ✅ **Safety Guardrails with Callbacks:** Implementing `before_model_callback` and `before_tool_callback` to inspect, modify, or block requests/tool usage based on predefined rules, enhancing application safety and control.

**End State Expectation:**

By completing this tutorial, you will have built a functional multi-agent Weather Bot system. This system will not only provide weather information but also handle conversational niceties, remember the last city checked, and operate within defined safety boundaries, all orchestrated using ADK.

**Prerequisites:**

*   ✅ **Solid understanding of Python programming.**
*   ✅ **Familiarity with Large Language Models (LLMs), APIs, and the concept of agents.**
*   ❗ **Crucially: Completion of the ADK Quickstart tutorial(s) or equivalent foundational knowledge of ADK basics (Agent, Runner, SessionService, basic Tool usage).** This tutorial builds directly upon those concepts.
*   ✅ **API Keys** for the LLMs you intend to use (e.g., Google AI Studio for Gemini, OpenAI Platform, Anthropic Console).


---

**Note on Execution Environment:**

This tutorial is structured for interactive notebook environments like Google Colab, Colab Enterprise, or Jupyter notebooks. Please keep the following in mind:

*   **Running Async Code:** Notebook environments handle asynchronous code differently. You'll see examples using `await` (suitable when an event loop is already running, common in notebooks) or `asyncio.run()` (often needed when running as a standalone `.py` script or in specific notebook setups). The code blocks provide guidance for both scenarios.
*   **Manual Runner/Session Setup:** The steps involve explicitly creating `Runner` and `SessionService` instances. This approach is shown because it gives you fine-grained control over the agent's execution lifecycle, session management, and state persistence.

**Alternative: Using ADK's Built-in Tools (Web UI / CLI / API Server)**

If you prefer a setup that handles the runner and session management automatically using ADK's standard tools, you can find the equivalent code structured for that purpose [here](https://github.com/google/adk-docs/tree/main/examples/python/tutorial/agent_team/adk_tutorial). That version is designed to be run directly with commands like `adk web` (for a web UI), `adk run` (for CLI interaction), or `adk api_server` (to expose an API). Please follow the `README.md` instructions provided in that alternative resource.

---

**Ready to build your agent team? Let's dive in!**

> **Note:** This tutorial works with adk version 1.0.0 and above

```python
--8<-- "examples/inline/python/tutorials/agent-team/001-build-your-first-intelligent-agent-team.py"
```


```python
--8<-- "examples/inline/python/tutorials/agent-team/002-install-adk-and-litellm-for-multi-model.py"
```


```python
--8<-- "examples/inline/python/tutorials/agent-team/003-ignore-all-warnings.py"
```


```python
--8<-- "examples/inline/python/tutorials/agent-team/004-markdown-security-note-it-s-best-practic.py"
```

---

## Step 1: Your First Agent \- Basic Weather Lookup

Let's begin by building the fundamental component of our Weather Bot: a single agent capable of performing a specific task – looking up weather information. This involves creating two core pieces:

1. **A Tool:** A Python function that equips the agent with the *ability* to fetch weather data.
2. **An Agent:** The AI "brain" that understands the user's request, knows it has a weather tool, and decides when and how to use it.

---

**1\. Define the Tool (`get_weather`)**

In ADK, **Tools** are the building blocks that give agents concrete capabilities beyond just text generation. They are typically regular Python functions that perform specific actions, like calling an API, querying a database, or performing calculations.

Our first tool will provide a *mock* weather report. This allows us to focus on the agent structure without needing external API keys yet. Later, you could easily swap this mock function with one that calls a real weather service.

**Key Concept: Docstrings are Crucial\!** The agent's LLM relies heavily on the function's **docstring** to understand:

* *What* the tool does.
* *When* to use it.
* *What arguments* it requires (`city: str`).
* *What information* it returns.

**Best Practice:** Write clear, descriptive, and accurate docstrings for your tools. This is essential for the LLM to use the tool correctly.


```python
--8<-- "examples/inline/python/tutorials/agent-team/005-step-1-your-first-agent-basic-weather-lo.py"
```

---

**2\. Define the Agent (`weather_agent`)**

Now, let's create the **Agent** itself. An `Agent` in ADK orchestrates the interaction between the user, the LLM, and the available tools.

We configure it with several key parameters:

* `name`: A unique identifier for this agent (e.g., "weather\_agent\_v1").
* `model`: Specifies which LLM to use (e.g., `MODEL_GEMINI_FLASH`). We'll start with a specific Gemini model.
* `description`: A concise summary of the agent's overall purpose. This becomes crucial later when other agents need to decide whether to delegate tasks to *this* agent.
* `instruction`: Detailed guidance for the LLM on how to behave, its persona, its goals, and specifically *how and when* to utilize its assigned `tools`.
* `tools`: A list containing the actual Python tool functions the agent is allowed to use (e.g., `[get_weather]`).

**Best Practice:** Provide clear and specific `instruction` prompts. The more detailed the instructions, the better the LLM can understand its role and how to use its tools effectively. Be explicit about error handling if needed.

**Best Practice:** Choose descriptive `name` and `description` values. These are used internally by ADK and are vital for features like automatic delegation (covered later).


```python
--8<-- "examples/inline/python/tutorials/agent-team/006-example-tool-usage-optional-test.py"
```

---

**3\. Setup Runner and Session Service**

To manage conversations and execute the agent, we need two more components:

* `SessionService`: Responsible for managing conversation history and state for different users and sessions. The `InMemorySessionService` is a simple implementation that stores everything in memory, suitable for testing and simple applications. It keeps track of the messages exchanged. We'll explore state persistence more in Step 4\.
* `Runner`: The engine that orchestrates the interaction flow. It takes user input, routes it to the appropriate agent, manages calls to the LLM and tools based on the agent's logic, handles session updates via the `SessionService`, and yields events representing the progress of the interaction.


```python
--8<-- "examples/inline/python/tutorials/agent-team/007-use-one-of-the-model-constants-defined-e.py"
```

---

**4\. Interact with the Agent**

We need a way to send messages to our agent and receive its responses. Since LLM calls and tool executions can take time, ADK's `Runner` operates asynchronously.

We'll define an `async` helper function (`call_agent_async`) that:

1. Takes a user query string.
2. Packages it into the ADK `Content` format.
3. Calls `runner.run_async`, providing the user/session context and the new message.
4. Iterates through the **Events** yielded by the runner. Events represent steps in the agent's execution (e.g., tool call requested, tool result received, intermediate LLM thought, final response).
5. Identifies and prints the **final response** event using `event.is_final_response()`.

**Why `async`?** Interactions with LLMs and potentially tools (like external APIs) are I/O-bound operations. Using `asyncio` allows the program to handle these operations efficiently without blocking execution.


```python
--8<-- "examples/inline/python/tutorials/agent-team/008-key-concept-runner-orchestrates-the-agen.py"
```

---

**5\. Run the Conversation**

Finally, let's test our setup by sending a few queries to the agent. We wrap our `async` calls in a main `async` function and run it using `await`.

Watch the output:

* See the user queries.
* Notice the `--- Tool: get_weather called... ---` logs when the agent uses the tool.
* Observe the agent's final responses, including how it handles the case where weather data isn't available (for Paris).


```python
--8<-- "examples/inline/python/tutorials/agent-team/009-we-iterate-through-events-to-find-the-fi.py"
```

---

Congratulations\! You've successfully built and interacted with your first ADK agent. It understands the user's request, uses a tool to find information, and responds appropriately based on the tool's result.

In the next step, we'll explore how to easily switch the underlying Language Model powering this agent.

## Step 2: Going Multi-Model with LiteLLM [Optional]

In Step 1, we built a functional Weather Agent powered by a specific Gemini model. While effective, real-world applications often benefit from the flexibility to use *different* Large Language Models (LLMs). Why?

*   **Performance:** Some models excel at specific tasks (e.g., coding, reasoning, creative writing).
*   **Cost:** Different models have varying price points.
*   **Capabilities:** Models offer diverse features, context window sizes, and fine-tuning options.
*   **Availability/Redundancy:** Having alternatives ensures your application remains functional even if one provider experiences issues.

ADK makes switching between models seamless through its integration with the [**LiteLLM**](https://github.com/BerriAI/litellm) library. LiteLLM acts as a consistent interface to over 100 different LLMs.

**In this step, we will:**

1.  Learn how to configure an ADK `Agent` to use models from providers like OpenAI (GPT) and Anthropic (Claude) using the `LiteLlm` wrapper.
2.  Define, configure (with their own sessions and runners), and immediately test instances of our Weather Agent, each backed by a different LLM.
3.  Interact with these different agents to observe potential variations in their responses, even when using the same underlying tool.

---

**1\. Import `LiteLlm`**

We imported this during the initial setup (Step 0), but it's the key component for multi-model support:


```python
--8<-- "examples/inline/python/tutorials/agent-team/010-step-2-going-multi-model-with-litellm-op.py"
```

**2\. Define and Test Multi-Model Agents**

Instead of passing only a model name string (which defaults to Google's Gemini models), we wrap the desired model identifier string within the `LiteLlm` class.

*   **Key Concept: `LiteLlm` Wrapper:** The `LiteLlm(model="provider/model_name")` syntax tells ADK to route requests for this agent through the LiteLLM library to the specified model provider.

Make sure you have configured the necessary API keys for OpenAI and Anthropic in Step 0. We'll use the `call_agent_async` function (defined earlier, which now accepts `runner`, `user_id`, and `session_id`) to interact with each agent immediately after its setup.

Each block below will:

*   Define the agent using a specific LiteLLM model (`MODEL_GPT_4O` or `MODEL_CLAUDE_SONNET`).
*   Create a *new, separate* `InMemorySessionService` and session specifically for that agent's test run. This keeps the conversation histories isolated for this demonstration.
*   Create a `Runner` configured for the specific agent and its session service.
*   Immediately call `call_agent_async` to send a query and test the agent.

**Best Practice:** Use constants for model names (like `MODEL_GPT_4O`, `MODEL_CLAUDE_SONNET` defined in Step 0) to avoid typos and make code easier to manage.

**Error Handling:** We wrap the agent definitions in `try...except` blocks. This prevents the entire code cell from failing if an API key for a specific provider is missing or invalid, allowing the tutorial to proceed with the models that *are* configured.

First, let's create and test the agent using OpenAI's GPT-4o.


```python
--8<-- "examples/inline/python/tutorials/agent-team/011-title-1-import-litellm.py"
```

Next, we'll do the same for Anthropic's Claude Sonnet.


```python
--8<-- "examples/inline/python/tutorials/agent-team/012-agent-using-gpt-4o.py"
```

Observe the output carefully from both code blocks. You should see:

1.  Each agent (`weather_agent_gpt`, `weather_agent_claude`) is created successfully (if API keys are valid).
2.  A dedicated session and runner are set up for each.
3.  Each agent correctly identifies the need to use the `get_weather` tool when processing the query (you'll see the `--- Tool: get_weather called... ---` log).
4.  The *underlying tool logic* remains identical, always returning our mock data.
5.  However, the **final textual response** generated by each agent might differ slightly in phrasing, tone, or formatting. This is because the instruction prompt is interpreted and executed by different LLMs (GPT-4o vs. Claude Sonnet).

This step demonstrates the power and flexibility ADK + LiteLLM provide. You can easily experiment with and deploy agents using various LLMs while keeping your core application logic (tools, fundamental agent structure) consistent.

In the next step, we'll move beyond a single agent and build a small team where agents can delegate tasks to each other!

---

## Step 3: Building an Agent Team \- Delegation for Greetings & Farewells

In Steps 1 and 2, we built and experimented with a single agent focused solely on weather lookups. While effective for its specific task, real-world applications often involve handling a wider variety of user interactions. We *could* keep adding more tools and complex instructions to our single weather agent, but this can quickly become unmanageable and less efficient.

A more robust approach is to build an **Agent Team**. This involves:

1. Creating multiple, **specialized agents**, each designed for a specific capability (e.g., one for weather, one for greetings, one for calculations).
2. Designating a **root agent** (or orchestrator) that receives the initial user request.
3. Enabling the root agent to **delegate** the request to the most appropriate specialized sub-agent based on the user's intent.

**Why build an Agent Team?**

* **Modularity:** Easier to develop, test, and maintain individual agents.
* **Specialization:** Each agent can be fine-tuned (instructions, model choice) for its specific task.
* **Scalability:** Simpler to add new capabilities by adding new agents.
* **Efficiency:** Allows using potentially simpler/cheaper models for simpler tasks (like greetings).

**In this step, we will:**

1. Define simple tools for handling greetings (`say_hello`) and farewells (`say_goodbye`).
2. Create two new specialized sub-agents: `greeting_agent` and `farewell_agent`.
3. Update our main weather agent (`weather_agent_v2`) to act as the **root agent**.
4. Configure the root agent with its sub-agents, enabling **automatic delegation**.
5. Test the delegation flow by sending different types of requests to the root agent.

---

**1\. Define Tools for Sub-Agents**

First, let's create the simple Python functions that will serve as tools for our new specialist agents. Remember, clear docstrings are vital for the agents that will use them.


```python
--8<-- "examples/inline/python/tutorials/agent-team/013-step-3-building-an-agent-team-delegation.py"
```

---

**2\. Define the Sub-Agents (Greeting & Farewell)**

Now, create the `Agent` instances for our specialists. Notice their highly focused `instruction` and, critically, their clear `description`. The `description` is the primary information the *root agent* uses to decide *when* to delegate to these sub-agents.

**Best Practice:** Sub-agent `description` fields should accurately and concisely summarize their specific capability. This is crucial for effective automatic delegation.

**Best Practice:** Sub-agent `instruction` fields should be tailored to their limited scope, telling them exactly what to do and *what not* to do (e.g., "Your *only* task is...").


```python
--8<-- "examples/inline/python/tutorials/agent-team/014-optional-self-test.py"
```

---

**3\. Define the Root Agent (Weather Agent v2) with Sub-Agents**

Now, we upgrade our `weather_agent`. The key changes are:

* Adding the `sub_agents` parameter: We pass a list containing the `greeting_agent` and `farewell_agent` instances we just created.
* Updating the `instruction`: We explicitly tell the root agent *about* its sub-agents and *when* it should delegate tasks to them.

**Key Concept: Automatic Delegation (Auto Flow)** By providing the `sub_agents` list, ADK enables automatic delegation. When the root agent receives a user query, its LLM considers not only its own instructions and tools but also the `description` of each sub-agent. If the LLM determines that a query aligns better with a sub-agent's described capability (e.g., "Handles simple greetings"), it will automatically generate a special internal action to *transfer control* to that sub-agent for that turn. The sub-agent then processes the query using its own model, instructions, and tools.

**Best Practice:** Ensure the root agent's instructions clearly guide its delegation decisions. Mention the sub-agents by name and describe the conditions under which delegation should occur.


```python
--8<-- "examples/inline/python/tutorials/agent-team/015-farewell-agent.py"
```

---

**4\. Interact with the Agent Team**

Now that we've defined our root agent (`weather_agent_team` - *Note: Ensure this variable name matches the one defined in the previous code block, likely `# @title Define the Root Agent with Sub-Agents`, which might have named it `root_agent`*) with its specialized sub-agents, let's test the delegation mechanism.

The following code block will:

1.  Define an `async` function `run_team_conversation`.
2.  Inside this function, create a *new, dedicated* `InMemorySessionService` and a specific session (`session_001_agent_team`) just for this test run. This isolates the conversation history for testing the team dynamics.
3.  Create a `Runner` (`runner_agent_team`) configured to use our `weather_agent_team` (the root agent) and the dedicated session service.
4.  Use our updated `call_agent_async` function to send different types of queries (greeting, weather request, farewell) to the `runner_agent_team`. We explicitly pass the runner, user ID, and session ID for this specific test.
5.  Immediately execute the `run_team_conversation` function.

We expect the following flow:

1.  The "Hello there!" query goes to `runner_agent_team`.
2.  The root agent (`weather_agent_team`) receives it and, based on its instructions and the `greeting_agent`'s description, delegates the task.
3.  `greeting_agent` handles the query, calls its `say_hello` tool, and generates the response.
4.  The "What is the weather in New York?" query is *not* delegated and is handled directly by the root agent using its `get_weather` tool.
5.  The "Thanks, bye!" query is delegated to the `farewell_agent`, which uses its `say_goodbye` tool.




```python
--8<-- "examples/inline/python/tutorials/agent-team/016-also-ensure-the-original-getweather-tool.py"
```

---

Look closely at the output logs, especially the `--- Tool: ... called ---` messages. You should observe:

*   For "Hello there!", the `say_hello` tool was called (indicating `greeting_agent` handled it).
*   For "What is the weather in New York?", the `get_weather` tool was called (indicating the root agent handled it).
*   For "Thanks, bye!", the `say_goodbye` tool was called (indicating `farewell_agent` handled it).

This confirms successful **automatic delegation**! The root agent, guided by its instructions and the `description`s of its `sub_agents`, correctly routed user requests to the appropriate specialist agent within the team.

You've now structured your application with multiple collaborating agents. This modular design is fundamental for building more complex and capable agent systems. In the next step, we'll give our agents the ability to remember information across turns using session state.

## Step 4: Adding Memory and Personalization with Session State

So far, our agent team can handle different tasks through delegation, but each interaction starts fresh – the agents have no memory of past conversations or user preferences within a session. To create more sophisticated and context-aware experiences, agents need **memory**. ADK provides this through **Session State**.

**What is Session State?**

* It's a Python dictionary (`session.state`) tied to a specific user session (identified by `APP_NAME`, `USER_ID`, `SESSION_ID`).
* It persists information *across multiple conversational turns* within that session.
* Agents and Tools can read from and write to this state, allowing them to remember details, adapt behavior, and personalize responses.

**How Agents Interact with State:**

1. **`ToolContext` (Primary Method):** Tools can accept a `ToolContext` object (automatically provided by ADK for any parameter annotated `ToolContext`, whatever its position). This object gives direct access to the session state via `tool_context.state`, allowing tools to read preferences or save results *during* execution.
2. **`output_key` (Auto-Save Agent Response):** An `Agent` can be configured with an `output_key="your_key"`. ADK will then automatically save the agent's final textual response for a turn into `session.state["your_key"]`.

**In this step, we will enhance our Weather Bot team by:**

1. Using a **new** `InMemorySessionService` to demonstrate state in isolation.
2. Initializing session state with a user preference for `temperature_unit`.
3. Creating a state-aware version of the weather tool (`get_weather_stateful`) that reads this preference via `ToolContext` and adjusts its output format (Celsius/Fahrenheit).
4. Updating the root agent to use this stateful tool and configuring it with an `output_key` to automatically save its final weather report to the session state.
5. Running a conversation to observe how the initial state affects the tool, how manual state changes alter subsequent behavior, and how `output_key` persists the agent's response.

---

**1\. Initialize New Session Service and State**

To clearly demonstrate state management without interference from prior steps, we'll instantiate a new `InMemorySessionService`. We'll also create a session with an initial state defining the user's preferred temperature unit.


```python
--8<-- "examples/inline/python/tutorials/agent-team/017-step-4-adding-memory-and-personalization.py"
```

---

**2\. Create State-Aware Weather Tool (`get_weather_stateful`)**

Now, we create a new version of the weather tool. Its key feature is accepting `tool_context: ToolContext` which allows it to access `tool_context.state`. It will read the `user_preference_temperature_unit` and format the temperature accordingly.


* **Key Concept: `ToolContext`** This object is the bridge allowing your tool logic to interact with the session's context, including reading and writing state variables. ADK finds the parameter by its `ToolContext` annotation and injects it automatically, so it can sit at any position in your tool function's signature. The annotated parameter is also hidden from the schema the LLM sees.


* **Best Practice:** When reading from state, use `dictionary.get('key', default_value)` to handle cases where the key might not exist yet, ensuring your tool doesn't crash.


```python
--8<-- "examples/inline/python/tutorials/agent-team/018-verify-the-initial-state-was-set-correct.py"
```

---

**3\. Redefine Sub-Agents and Update Root Agent**

To ensure this step is self-contained and builds correctly, we first redefine the `greeting_agent` and `farewell_agent` exactly as they were in Step 3\. Then, we define our new root agent (`weather_agent_v4_stateful`):

* It uses the new `get_weather_stateful` tool.
* It includes the greeting and farewell sub-agents for delegation.
* **Crucially**, it sets `output_key="last_weather_report"` which automatically saves its final weather response to the session state.


```python
--8<-- "examples/inline/python/tutorials/agent-team/019-verify-the-initial-state-was-set-correct.py"
```

---

**4\. Interact and Test State Flow**

Now, let's execute a conversation designed to test the state interactions using the `runner_root_stateful` (associated with our stateful agent and the `session_service_stateful`). We'll use the `call_agent_async` function defined earlier, ensuring we pass the correct runner, user ID (`USER_ID_STATEFUL`), and session ID (`SESSION_ID_STATEFUL`).

The conversation flow will be:

1.  **Check weather (London):** The `get_weather_stateful` tool should read the initial "Celsius" preference from the session state initialized in Section 1. The root agent's final response (the weather report in Celsius) should get saved to `state['last_weather_report']` via the `output_key` configuration.
2.  **Manually update state:** We will *directly modify* the state stored within the `InMemorySessionService` instance (`session_service_stateful`).
    *   **Why direct modification?** The `session_service.get_session()` method returns a *copy* of the session. Modifying that copy wouldn't affect the state used in subsequent agent runs. For this testing scenario with `InMemorySessionService`, we access the internal `sessions` dictionary to change the *actual* stored state value for `user_preference_temperature_unit` to "Fahrenheit". *Note: In real applications, state changes are typically triggered by tools or agent logic returning `EventActions(state_delta=...)`, not direct manual updates.*
3.  **Check weather again (New York):** The `get_weather_stateful` tool should now read the updated "Fahrenheit" preference from the state and convert the temperature accordingly. The root agent's *new* response (weather in Fahrenheit) will overwrite the previous value in `state['last_weather_report']` due to the `output_key`.
4.  **Greet the agent:** Verify that delegation to the `greeting_agent` still works correctly alongside the stateful operations.
5.  **Inspect final state:** After the conversation, we retrieve the session one last time (getting a copy) and print its state to confirm the `user_preference_temperature_unit` is indeed "Fahrenheit", observe the final value saved by `output_key` (which will be the previous weather report in this run), and see the `last_city_checked_stateful` value written by the tool.



```python
--8<-- "examples/inline/python/tutorials/agent-team/020-check-prerequisites-before-creating-the.py"
```

---

By reviewing the conversation flow and the final session state printout, you can confirm:

*   **State Read:** The weather tool (`get_weather_stateful`) correctly read `user_preference_temperature_unit` from state, initially using "Celsius" for London.
*   **State Update:** The direct modification successfully changed the stored preference to "Fahrenheit".
*   **State Read (Updated):** The tool subsequently read "Fahrenheit" when asked for New York's weather and performed the conversion.
*   **Tool State Write:** The tool successfully wrote the `last_city_checked_stateful` ("New York" after the second weather check) into the state via `tool_context.state`.
*   **Delegation:** The delegation to the `greeting_agent` for "Hi!" functioned correctly even after state modifications.
*   **`output_key`:** The `output_key="last_weather_report"` successfully saved the root agent's *final* response for *each turn* where the root agent was the one ultimately responding. In this sequence, the final greeting ("Hello, there!") was generated by the delegated sub-agent rather than the root agent, so `output_key` was not triggered on that final turn, leaving the previous weather report intact in the session state.
*   **Final State:** The final check confirms the preference persisted as "Fahrenheit".

You've now successfully integrated session state to personalize agent behavior using `ToolContext`, manually manipulated state for testing `InMemorySessionService`, and observed how `output_key` provides a simple mechanism for saving the agent's last response to state. This foundational understanding of state management is key as we proceed to implement safety guardrails using callbacks in the next steps.

---

## Step 5: Adding Safety \- Input Guardrail with `before_model_callback`

Our agent team is becoming more capable, remembering preferences and using tools effectively. However, in real-world scenarios, we often need safety mechanisms to control the agent's behavior *before* potentially problematic requests even reach the core Large Language Model (LLM).

ADK provides **Callbacks** – functions that allow you to hook into specific points in the agent's execution lifecycle. The `before_model_callback` is particularly useful for input safety.

**What is `before_model_callback`?**

* It's a Python function you define that ADK executes *just before* an agent sends its compiled request (including conversation history, instructions, and the latest user message) to the underlying LLM.
* **Purpose:** Inspect the request, modify it if necessary, or block it entirely based on predefined rules.

**Common Use Cases:**

* **Input Validation/Filtering:** Check if user input meets criteria or contains disallowed content (like PII or keywords).
* **Guardrails:** Prevent harmful, off-topic, or policy-violating requests from being processed by the LLM.
* **Dynamic Prompt Modification:** Add timely information (e.g., from session state) to the LLM request context just before sending.

**How it Works:**

1. Define a function accepting `callback_context: CallbackContext` and `llm_request: LlmRequest`.

    * `callback_context`: Provides access to agent info, session state (`callback_context.state`), etc.
    * `llm_request`: Contains the full payload intended for the LLM (`contents`, `config`).

2. Inside the function:

    * **Inspect:** Examine `llm_request.contents` (especially the last user message).
    * **Modify (Use Caution):** You *can* change parts of `llm_request`.
    * **Block (Guardrail):** Return an `LlmResponse` object. ADK will send this response back immediately, *skipping* the LLM call for that turn.
    * **Allow:** Return `None`. ADK proceeds to call the LLM with the (potentially modified) request.

**In this step, we will:**

1. Define a `before_model_callback` function (`block_keyword_guardrail`) that checks the user's input for a specific keyword ("BLOCK").
2. Update our stateful root agent (`weather_agent_v4_stateful` from Step 4\) to use this callback.
3. Create a new runner associated with this updated agent but using the *same stateful session service* to maintain state continuity.
4. Test the guardrail by sending both normal and keyword-containing requests.

---

**1\. Define the Guardrail Callback Function**

This function will inspect the last user message within the `llm_request` content. If it finds "BLOCK" (case-insensitive), it constructs and returns an `LlmResponse` to block the flow; otherwise, it returns `None`.


```python
--8<-- "examples/inline/python/tutorials/agent-team/021-step-5-adding-safety-input-guardrail-wit.py"
```

---

**2\. Update Root Agent to Use the Callback**

We redefine the root agent, adding the `before_model_callback` parameter and pointing it to our new guardrail function. We'll give it a new version name for clarity.

*Important:* We need to redefine the sub-agents (`greeting_agent`, `farewell_agent`) and the stateful tool (`get_weather_stateful`) within this context if they are not already available from previous steps, ensuring the root agent definition has access to all its components.


```python
--8<-- "examples/inline/python/tutorials/agent-team/022-ensure-necessary-imports-are-available.py"
```

---

**3\. Interact to Test the Guardrail**

Let's test the guardrail's behavior. We'll use the *same session* (`SESSION_ID_STATEFUL`) as in Step 4 to show that state persists across these changes.

1. Send a normal weather request (should pass the guardrail and execute).
2. Send a request containing "BLOCK" (should be intercepted by the callback).
3. Send a greeting (should pass the root agent's guardrail, be delegated, and execute normally).


```python
--8<-- "examples/inline/python/tutorials/agent-team/023-check-all-components-before-proceeding.py"
```

---

Observe the execution flow:

1. **London Weather:** The callback runs for `weather_agent_v5_model_guardrail`, inspects the message, prints "Keyword not found. Allowing LLM call.", and returns `None`. The agent proceeds, calls the `get_weather_stateful` tool (which uses the "Fahrenheit" preference from Step 4's state change), and returns the weather. This response updates `last_weather_report` via `output_key`.
2. **BLOCK Request:** The callback runs again for `weather_agent_v5_model_guardrail`, inspects the message, finds "BLOCK", prints "Blocking LLM call\!", sets the state flag, and returns the predefined `LlmResponse`. The agent's underlying LLM is *never called* for this turn. The user sees the callback's blocking message.
3. **Hello Again:** The callback runs for `weather_agent_v5_model_guardrail`, allows the request. The root agent then delegates to `greeting_agent`. *Note: The `before_model_callback` defined on the root agent does NOT automatically apply to sub-agents.* The `greeting_agent` proceeds normally, calls its `say_hello` tool, and returns the greeting.

You have successfully implemented an input safety layer\! The `before_model_callback` provides a powerful mechanism to enforce rules and control agent behavior *before* expensive or potentially risky LLM calls are made. Next, we'll apply a similar concept to add guardrails around tool usage itself.

## Step 6: Adding Safety \- Tool Argument Guardrail (`before_tool_callback`)

In Step 5, we added a guardrail to inspect and potentially block user input *before* it reached the LLM. Now, we'll add another layer of control *after* the LLM has decided to use a tool but *before* that tool actually executes. This is useful for validating the *arguments* the LLM wants to pass to the tool.

ADK provides the `before_tool_callback` for this precise purpose.

**What is `before_tool_callback`?**

* It's a Python function executed just *before* a specific tool function runs, after the LLM has requested its use and decided on the arguments.
* **Purpose:** Validate tool arguments, prevent tool execution based on specific inputs, modify arguments dynamically, or enforce resource usage policies.

**Common Use Cases:**

* **Argument Validation:** Check if arguments provided by the LLM are valid, within allowed ranges, or conform to expected formats.
* **Resource Protection:** Prevent tools from being called with inputs that might be costly, access restricted data, or cause unwanted side effects (e.g., blocking API calls for certain parameters).
* **Dynamic Argument Modification:** Adjust arguments based on session state or other contextual information before the tool runs.

**How it Works:**

1. Define a function accepting `tool: BaseTool`, `args: Dict[str, Any]`, and `tool_context: ToolContext`.

    * `tool`: The tool object about to be called (inspect `tool.name`).
    * `args`: The dictionary of arguments the LLM generated for the tool.
    * `tool_context`: Provides access to session state (`tool_context.state`), agent info, etc.

2. Inside the function:

    * **Inspect:** Examine the `tool.name` and the `args` dictionary.
    * **Modify:** Change values within the `args` dictionary *directly*. If you return `None`, the tool runs with these modified args.
    * **Block/Override (Guardrail):** Return a **dictionary**. ADK treats this dictionary as the *result* of the tool call, completely *skipping* the execution of the original tool function. The dictionary should ideally match the expected return format of the tool it's blocking.
    * **Allow:** Return `None`. ADK proceeds to execute the actual tool function with the (potentially modified) arguments.

**In this step, we will:**

1. Define a `before_tool_callback` function (`block_paris_tool_guardrail`) that specifically checks if the `get_weather_stateful` tool is called with the city "Paris".
2. If "Paris" is detected, the callback will block the tool and return a custom error dictionary.
3. Update our root agent (`weather_agent_v6_tool_guardrail`) to include *both* the `before_model_callback` and this new `before_tool_callback`.
4. Create a new runner for this agent, using the same stateful session service.
5. Test the flow by requesting weather for allowed cities and the blocked city ("Paris").

---

**1\. Define the Tool Guardrail Callback Function**

This function targets the `get_weather_stateful` tool. It checks the `city` argument. If it's "Paris", it returns an error dictionary that looks like the tool's own error response. Otherwise, it allows the tool to run by returning `None`.


```python
--8<-- "examples/inline/python/tutorials/agent-team/024-step-6-adding-safety-tool-argument-guard.py"
```

---

**2\. Update Root Agent to Use Both Callbacks**

We redefine the root agent again (`weather_agent_v6_tool_guardrail`), this time adding the `before_tool_callback` parameter alongside the `before_model_callback` from Step 5\.

*Self-Contained Execution Note:* Similar to Step 5, ensure all prerequisites (sub-agents, tools, `before_model_callback`) are defined or available in the execution context before defining this agent.


```python
--8<-- "examples/inline/python/tutorials/agent-team/025-ensure-necessary-imports-are-available.py"
```

---

**3\. Interact to Test the Tool Guardrail**

Let's test the interaction flow, again using the same stateful session (`SESSION_ID_STATEFUL`) from the previous steps.

1. Request weather for "New York": Passes both callbacks, tool executes (using Fahrenheit preference from state).
2. Request weather for "Paris": Passes `before_model_callback`. LLM decides to call `get_weather_stateful(city='Paris')`. `before_tool_callback` intercepts, blocks the tool, and returns the error dictionary. Agent relays this error.
3. Request weather for "London": Passes both callbacks, tool executes normally.


```python
--8<-- "examples/inline/python/tutorials/agent-team/026-define-the-root-agent-with-both-callback.py"
```

---

Analyze the output:

1. **New York:** The `before_model_callback` allows the request. The LLM requests `get_weather_stateful`. The `before_tool_callback` runs, inspects the args (`{'city': 'New York'}`), sees it's not "Paris", prints "Allowing tool..." and returns `None`. The actual `get_weather_stateful` function executes, reads "Fahrenheit" from state, and returns the weather report. The agent relays this, and it gets saved via `output_key`.
2. **Paris:** The `before_model_callback` allows the request. The LLM requests `get_weather_stateful(city='Paris')`. The `before_tool_callback` runs, inspects the args, detects "Paris", prints "Blocking tool execution\!", sets the state flag, and returns the error dictionary `{'status': 'error', 'error_message': 'Policy restriction...'}`. The actual `get_weather_stateful` function is **never executed**. The agent receives the error dictionary *as if it were the tool's output* and formulates a response based on that error message.
3. **London:** Behaves like New York, passing both callbacks and executing the tool successfully. The new London weather report overwrites the `last_weather_report` in the state.

You've now added a crucial safety layer controlling not just *what* reaches the LLM, but also *how* the agent's tools can be used based on the specific arguments generated by the LLM. Callbacks like `before_model_callback` and `before_tool_callback` are essential for building robust, safe, and policy-compliant agent applications.



---


## Conclusion: Your Agent Team is Ready!

Congratulations! You've successfully journeyed from building a single, basic weather agent to constructing a sophisticated, multi-agent team using the Agent Development Kit (ADK).

**Let's recap what you've accomplished:**

*   You started with a **fundamental agent** equipped with a single tool (`get_weather`).
*   You explored ADK's **multi-model flexibility** using LiteLLM, running the same core logic with different LLMs like Gemini, GPT-4o, and Claude.
*   You embraced **modularity** by creating specialized sub-agents (`greeting_agent`, `farewell_agent`) and enabling **automatic delegation** from a root agent.
*   You gave your agents **memory** using **Session State**, allowing them to remember user preferences (`temperature_unit`) and past interactions (`output_key`).
*   You implemented crucial **safety guardrails** using both `before_model_callback` (blocking specific input keywords) and `before_tool_callback` (blocking tool execution based on arguments like the city "Paris").

Through building this progressive Weather Bot team, you've gained hands-on experience with core ADK concepts essential for developing complex, intelligent applications.

**Key Takeaways:**

*   **Agents & Tools:** The fundamental building blocks for defining capabilities and reasoning. Clear instructions and docstrings are paramount.
*   **Runners & Session Services:** The engine and memory management system that orchestrate agent execution and maintain conversational context.
*   **Delegation:** Designing multi-agent teams allows for specialization, modularity, and better management of complex tasks. Agent `description` is key for auto-flow.
*   **Session State (`ToolContext`, `output_key`):** Essential for creating context-aware, personalized, and multi-turn conversational agents.
*   **Callbacks (`before_model`, `before_tool`):** Powerful hooks for implementing safety, validation, policy enforcement, and dynamic modifications *before* critical operations (LLM calls or tool execution).
*   **Flexibility (`LiteLlm`):** ADK empowers you to choose the best LLM for the job, balancing performance, cost, and features.

**Where to Go Next?**

Your Weather Bot team is a great starting point. Here are some ideas to further explore ADK and enhance your application:

1.  **Real Weather API:** Replace the `mock_weather_db` in your `get_weather` tool with a call to a real weather API (like OpenWeatherMap, WeatherAPI).
2.  **More Complex State:** Store more user preferences (e.g., preferred location, notification settings) or conversation summaries in the session state.
3.  **Refine Delegation:** Experiment with different root agent instructions or sub-agent descriptions to fine-tune the delegation logic. Could you add a "forecast" agent?
4.  **Advanced Callbacks:**
    *   Use `after_model_callback` to potentially reformat or sanitize the LLM's response *after* it's generated.
    *   Use `after_tool_callback` to process or log the results returned by a tool.
    *   Implement `before_agent_callback` or `after_agent_callback` for agent-level entry/exit logic.
5.  **Error Handling:** Improve how the agent handles tool errors or unexpected API responses. Maybe add retry logic within a tool.
6.  **Persistent Session Storage:** Consider changing `InMemorySessionService` to one of ADK's persistent implementations, such as `DatabaseSessionService` which is SQLAlchemy-backed and installed with `pip install google-adk[db]`, or `VertexAiSessionService`. For more information, see the [Session](/sessions/session/) page.
7.  **Streaming UI:** Integrate your agent team with a web framework (like FastAPI, as shown in the ADK Streaming Quickstart) to create a real-time chat interface.

The Agent Development Kit provides a robust foundation for building sophisticated LLM-powered applications. By mastering the concepts covered in this tutorial – tools, state, delegation, and callbacks – you are well-equipped to tackle increasingly complex agentic systems.

Happy building!
