# Custom Tools for ADK

In an ADK agent workflow, Tools are programming functions with structured input
and output that can be called by an ADK Agent to perform actions. ADK Tools
function similarly to how you use a 
[Function Call](https://ai.google.dev/gemini-api/docs/function-calling) 
with Gemini or other generative AI models. You can perform various actions and
programming functions with an ADK Tool, such as:

*   Querying databases
*   Making API requests: getting weather data, booking systems
*   Searching the web
*   Executing code snippets
*   Retrieving information from documents (RAG)
*   Interacting with other software or services

!!! tip "[ADK Tools list](/adk-docs/tools/)"
    Before building your own Tools for ADK, check out the 
    **[ADK Tools list](/adk-docs/tools/)**
    for pre-built tools you can use with ADK Agents.

## What is a Tool?

In the context of ADK, a Tool represents a specific
capability provided to an AI agent, enabling it to perform actions and interact
with the world beyond its core text generation and reasoning abilities. What
distinguishes capable agents from basic language models is often their effective
use of tools.

Technically, a tool is typically a modular code component—**like a Python/ Java
function**, a class method, or even another specialized agent—designed to
execute a distinct, predefined task. These tasks often involve interacting with
external systems or data.

<img src="../assets/agent-tool-call.png" alt="Agent tool call">

### Key Characteristics

**Action-Oriented:** Tools perform specific actions for an agent, such as 
searching for information, calling an API, or performing calculations.

**Extends Agent capabilities:** They empower agents to access real-time information, affect external systems, and overcome the knowledge limitations inherent in their training data.

**Execute predefined logic:** Crucially, tools execute specific, developer-defined logic. They do not possess their own independent reasoning capabilities like the agent's core Large Language Model (LLM). The LLM reasons about which tool to use, when, and with what inputs, but the tool itself just executes its designated function.

## How Agents Use Tools

Agents leverage tools dynamically through mechanisms often involving function calling. The process generally follows these steps:

1. **Reasoning:** The agent's LLM analyzes its system instruction, conversation history, and user request.
2. **Selection:** Based on the analysis, the LLM decides on which tool, if any, to execute, based on the tools available to the agent and the docstrings that describes each tool.
3. **Invocation:** The LLM generates the required arguments (inputs) for the selected tool and triggers its execution.
4. **Observation:** The agent receives the output (result) returned by the tool.
5. **Finalization:** The agent incorporates the tool's output into its ongoing reasoning process to formulate the next response, decide the subsequent step, or determine if the goal has been achieved.

Think of the tools as a specialized toolkit that the agent's intelligent core (the LLM) can access and utilize as needed to accomplish complex tasks.

## Tool Types in ADK

ADK offers flexibility by supporting several types of tools:

1. **[Function Tools](../tools/function-tools.md):** Tools created by you, tailored to your specific application's needs.
    * **[Functions/Methods](../tools/function-tools.md#1-function-tool):** Define standard synchronous functions or methods in your code (e.g., Python def).
    * **[Agents-as-Tools](../tools/function-tools.md#3-agent-as-a-tool):** Use another, potentially specialized, agent as a tool for a parent agent.
    * **[Long Running Function Tools](../tools/function-tools.md#2-long-running-function-tool):** Support for tools that perform asynchronous operations or take significant time to complete.
2. **[Built-in Tools](../tools/built-in-tools.md):** Ready-to-use tools provided by the framework for common tasks.
        Examples: Google Search, Code Execution, Retrieval-Augmented Generation (RAG).
3. **[Third-Party Tools](../tools/third-party-tools.md):** Integrate tools seamlessly from popular external libraries.
        Examples: LangChain Tools, CrewAI Tools.

Navigate to the respective documentation pages linked above for detailed information and examples for each tool type.

## Referencing Tool in Agent’s Instructions

Within an agent's instructions, you can directly reference a tool by using its **function name.** If the tool's **function name** and **docstring** are sufficiently descriptive, your instructions can primarily focus on **when the Large Language Model (LLM) should utilize the tool**. This promotes clarity and helps the model understand the intended use of each tool.

It is **crucial to clearly instruct the agent on how to handle different return values** that a tool might produce. For example, if a tool returns an error message, your instructions should specify whether the agent should retry the operation, give up on the task, or request additional information from the user.

Furthermore, ADK supports the sequential use of tools, where the output of one tool can serve as the input for another. When implementing such workflows, it's important to **describe the intended sequence of tool usage** within the agent's instructions to guide the model through the necessary steps.

### Example

The following example showcases how an agent can use tools by **referencing their function names in its instructions**. It also demonstrates how to guide the agent to **handle different return values from tools**, such as success or error messages, and how to orchestrate the **sequential use of multiple tools** to accomplish a task.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/weather_sentiment.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/WeatherSentimentAgentApp.java:full_code"
    ```

## Tool Context

For more advanced scenarios, ADK allows you to access additional contextual information within your tool function by including the special parameter `tool_context: ToolContext`. By including this in the function signature, ADK will **automatically** provide an **instance of the ToolContext** class when your tool is called during agent execution.

The **ToolContext** provides access to several key pieces of information and control levers:

* `state: State`: Read and modify the current session's state. Changes made here are tracked and persisted.

* `actions: EventActions`: Influence the agent's subsequent actions after the tool runs (e.g., skip summarization, transfer to another agent).

* `function_call_id: str`: The unique identifier assigned by the framework to this specific invocation of the tool. Useful for tracking and correlating with authentication responses. This can also be helpful when multiple tools are called within a single model response.

* `function_call_event_id: str`: This attribute provides the unique identifier of the **event** that triggered the current tool call. This can be useful for tracking and logging purposes.

* `auth_response: Any`: Contains the authentication response/credentials if an authentication flow was completed before this tool call.

* Access to Services: Methods to interact with configured services like Artifacts and Memory.

Note that you shouldn't include the `tool_context` parameter in the tool function docstring. Since `ToolContext` is automatically injected by the ADK framework *after* the LLM decides to call the tool function, it is not relevant for the LLM's decision-making and including it can confuse the LLM.

### **State Management**

The `tool_context.state` attribute provides direct read and write access to the state associated with the current session. It behaves like a dictionary but ensures that any modifications are tracked as deltas and persisted by the session service. This enables tools to maintain and share information across different interactions and agent steps.

* **Reading State**: Use standard dictionary access (`tool_context.state['my_key']`) or the `.get()` method (`tool_context.state.get('my_key', default_value)`).

* **Writing State**: Assign values directly (`tool_context.state['new_key'] = 'new_value'`). These changes are recorded in the state_delta of the resulting event.

* **State Prefixes**: Remember the standard state prefixes:

    * `app:*`: Shared across all users of the application.

    * `user:*`: Specific to the current user across all their sessions.

    * (No prefix): Specific to the current session.

    * `temp:*`: Temporary, not persisted across invocations (useful for passing data within a single run call but generally less useful inside a tool context which operates between LLM calls).

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/user_preference.py"
    ```

=== "Java"

    ```java
    import com.google.adk.tools.FunctionTool;
    import com.google.adk.tools.ToolContext;

    // Updates a user-specific preference.
    public Map<String, String> updateUserThemePreference(String value, ToolContext toolContext) {
      String userPrefsKey = "user:preferences:theme";
  
      // Get current preferences or initialize if none exist
      String preference = toolContext.state().getOrDefault(userPrefsKey, "").toString();
      if (preference.isEmpty()) {
        preference = value;
      }
  
      // Write the updated dictionary back to the state
      toolContext.state().put("user:preferences", preference);
      System.out.printf("Tool: Updated user preference %s to %s", userPrefsKey, preference);
  
      return Map.of("status", "success", "updated_preference", toolContext.state().get(userPrefsKey).toString());
      // When the LLM calls updateUserThemePreference("dark"):
      // The toolContext.state will be updated, and the change will be part of the
      // resulting tool response event's actions.stateDelta.
    }
    ```

### **Controlling Agent Flow**

The `tool_context.actions` attribute (`ToolContext.actions()` in Java) holds an **EventActions** object. Modifying attributes on this object allows your tool to influence what the agent or framework does after the tool finishes execution.

* **`skip_summarization: bool`**: (Default: False) If set to True, instructs the ADK to bypass the LLM call that typically summarizes the tool's output. This is useful if your tool's return value is already a user-ready message.

* **`transfer_to_agent: str`**: Set this to the name of another agent. The framework will halt the current agent's execution and **transfer control of the conversation to the specified agent**. This allows tools to dynamically hand off tasks to more specialized agents.

* **`escalate: bool`**: (Default: False) Setting this to True signals that the current agent cannot handle the request and should pass control up to its parent agent (if in a hierarchy). In a LoopAgent, setting **escalate=True** in a sub-agent's tool will terminate the loop.

#### Example

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/customer_support_agent.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CustomerSupportAgentApp.java:full_code"
    ```

##### Explanation

* We define two agents: `main_agent` and `support_agent`. The `main_agent` is designed to be the initial point of contact.
* The `check_and_transfer` tool, when called by `main_agent`, examines the user's query.
* If the query contains the word "urgent", the tool accesses the `tool_context`, specifically **`tool_context.actions`**, and sets the transfer\_to\_agent attribute to `support_agent`.
* This action signals to the framework to **transfer the control of the conversation to the agent named `support_agent`**.
* When the `main_agent` processes the urgent query, the `check_and_transfer` tool triggers the transfer. The subsequent response would ideally come from the `support_agent`.
* For a normal query without urgency, the tool simply processes it without triggering a transfer.

This example illustrates how a tool, through EventActions in its ToolContext, can dynamically influence the flow of the conversation by transferring control to another specialized agent.

### **Authentication**

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python. Java support is planned/ coming soon."}

ToolContext provides mechanisms for tools interacting with authenticated APIs. If your tool needs to handle authentication, you might use the following:

* **`auth_response`**: Contains credentials (e.g., a token) if authentication was already handled by the framework before your tool was called (common with RestApiTool and OpenAPI security schemes).

* **`request_credential(auth_config: dict)`**: Call this method if your tool determines authentication is needed but credentials aren't available. This signals the framework to start an authentication flow based on the provided auth_config.

* **`get_auth_response()`**: Call this in a subsequent invocation (after request_credential was successfully handled) to retrieve the credentials the user provided.

For detailed explanations of authentication flows, configuration, and examples, please refer to the dedicated Tool Authentication documentation page.

### **Context-Aware Data Access Methods**

These methods provide convenient ways for your tool to interact with persistent data associated with the session or user, managed by configured services.

* **`list_artifacts()`** (or **`listArtifacts()`** in Java): Returns a list of filenames (or keys) for all artifacts currently stored for the session via the artifact_service. Artifacts are typically files (images, documents, etc.) uploaded by the user or generated by tools/agents.

* **`load_artifact(filename: str)`**: Retrieves a specific artifact by its filename from the **artifact_service**. You can optionally specify a version; if omitted, the latest version is returned. Returns a `google.genai.types.Part` object containing the artifact data and mime type, or None if not found.

* **`save_artifact(filename: str, artifact: types.Part)`**: Saves a new version of an artifact to the artifact_service. Returns the new version number (starting from 0).

* **`search_memory(query: str)`** ![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python. Java support is planned/ coming soon."}

       Queries the user's long-term memory using the configured `memory_service`. This is useful for retrieving relevant information from past interactions or stored knowledge. The structure of the **SearchMemoryResponse** depends on the specific memory service implementation but typically contains relevant text snippets or conversation excerpts.

#### Example

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/doc_analysis.py"
    ```

=== "Java"

    ```java
    // Analyzes a document using context from memory.
    // You can also list, load and save artifacts using Callback Context or LoadArtifacts tool.
    public static @NonNull Maybe<ImmutableMap<String, Object>> processDocument(
        @Annotations.Schema(description = "The name of the document to analyze.") String documentName,
        @Annotations.Schema(description = "The query for the analysis.") String analysisQuery,
        ToolContext toolContext) {
  
      // 1. List all available artifacts
      System.out.printf(
          "Listing all available artifacts %s:", toolContext.listArtifacts().blockingGet());
  
      // 2. Load an artifact to memory
      System.out.println("Tool: Attempting to load artifact: " + documentName);
      Part documentPart = toolContext.loadArtifact(documentName, Optional.empty()).blockingGet();
      if (documentPart == null) {
        System.out.println("Tool: Document '" + documentName + "' not found.");
        return Maybe.just(
            ImmutableMap.<String, Object>of(
                "status", "error", "message", "Document '" + documentName + "' not found."));
      }
      String documentText = documentPart.text().orElse("");
      System.out.println(
          "Tool: Loaded document '" + documentName + "' (" + documentText.length() + " chars).");
  
      // 3. Perform analysis (placeholder)
      String analysisResult =
          "Analysis of '"
              + documentName
              + "' regarding '"
              + analysisQuery
              + " [Placeholder Analysis Result]";
      System.out.println("Tool: Performed analysis.");
  
      // 4. Save the analysis result as a new artifact
      Part analysisPart = Part.fromText(analysisResult);
      String newArtifactName = "analysis_" + documentName;
  
      toolContext.saveArtifact(newArtifactName, analysisPart);
  
      return Maybe.just(
          ImmutableMap.<String, Object>builder()
              .put("status", "success")
              .put("analysis_artifact", newArtifactName)
              .build());
    }
    // FunctionTool processDocumentTool =
    //      FunctionTool.create(ToolContextArtifactExample.class, "processDocument");
    // In the Agent, include this function tool.
    // LlmAgent agent = LlmAgent().builder().tools(processDocumentTool).build();
    ```

By leveraging the **ToolContext**, developers can create more sophisticated and context-aware custom tools that seamlessly integrate with ADK's architecture and enhance the overall capabilities of their agents.

## Defining Effective Tool Functions

When using a method or function as an ADK Tool, how you define it significantly impacts the agent's ability to use it correctly. The agent's Large Language Model (LLM) relies heavily on the function's **name**, **parameters (arguments)**, **type hints**, and **docstring** / **source code comments** to understand its purpose and generate the correct call.

Here are key guidelines for defining effective tool functions:

* **Function Name:**
    * Use descriptive, verb-noun based names that clearly indicate the action (e.g., `get_weather`, `searchDocuments`, `schedule_meeting`).
    * Avoid generic names like `run`, `process`, `handle_data`, or overly ambiguous names like `doStuff`. Even with a good description, a name like `do_stuff` might confuse the model about when to use the tool versus, for example, `cancelFlight`.
    * The LLM uses the function name as a primary identifier during tool selection.

* **Parameters (Arguments):**
    * Your function can have any number of parameters.
    * Use clear and descriptive names (e.g., `city` instead of `c`, `search_query` instead of `q`).
    * **Provide type hints in Python**  for all parameters (e.g., `city: str`, `user_id: int`, `items: list[str]`). This is essential for ADK to generate the correct schema for the LLM.
    * Ensure all parameter types are **JSON serializable**. All java primitives as well as standard Python types like `str`, `int`, `float`, `bool`, `list`, `dict`, and their combinations are generally safe. Avoid complex custom class instances as direct parameters unless they have a clear JSON representation.
    * **Do not set default values** for parameters. E.g., `def my_func(param1: str = "default")`. Default values are not reliably supported or used by the underlying models during function call generation. All necessary information should be derived by the LLM from the context or explicitly requested if missing.
    * **`self` / `cls` Handled Automatically:** Implicit parameters like `self` (for instance methods) or `cls` (for class methods) are automatically handled by ADK and excluded from the schema shown to the LLM. You only need to define type hints and descriptions for the logical parameters your tool requires the LLM to provide.

* **Return Type:**
    * The function's return value **must be a dictionary (`dict`)** in Python or a **Map** in Java.
    * If your function returns a non-dictionary type (e.g., a string, number, list), the ADK framework will automatically wrap it into a dictionary/Map like `{'result': your_original_return_value}` before passing the result back to the model.
    * Design the dictionary/Map keys and values to be **descriptive and easily understood *by the LLM***. Remember, the model reads this output to decide its next step.
    * Include meaningful keys. For example, instead of returning just an error code like `500`, return `{'status': 'error', 'error_message': 'Database connection failed'}`.
    * It's a **highly recommended practice** to include a `status` key (e.g., `'success'`, `'error'`, `'pending'`, `'ambiguous'`) to clearly indicate the outcome of the tool execution for the model.

* **Docstring / Source Code Comments:**
    * **This is critical.** The docstring is the primary source of descriptive information for the LLM.
    * **Clearly state what the tool *does*.** Be specific about its purpose and limitations.
    * **Explain *when* the tool should be used.** Provide context or example scenarios to guide the LLM's decision-making.
    * **Describe *each parameter* clearly.** Explain what information the LLM needs to provide for that argument.
    * Describe the **structure and meaning of the expected `dict` return value**, especially the different `status` values and associated data keys.
    * **Do not describe the injected ToolContext parameter**. Avoid mentioning the optional `tool_context: ToolContext` parameter within the docstring description since it is not a parameter the LLM needs to know about. ToolContext is injected by ADK, *after* the LLM decides to call it. 

    **Example of a good definition:**

=== "Python"
    
    ```python
    def lookup_order_status(order_id: str) -> dict:
      """Fetches the current status of a customer's order using its ID.

      Use this tool ONLY when a user explicitly asks for the status of
      a specific order and provides the order ID. Do not use it for
      general inquiries.

      Args:
          order_id: The unique identifier of the order to look up.

      Returns:
          A dictionary indicating the outcome.
          On success, status is 'success' and includes an 'order' dictionary.
          On failure, status is 'error' and includes an 'error_message'.
          Example success: {'status': 'success', 'order': {'state': 'shipped', 'tracking_number': '1Z9...'}}
          Example error: {'status': 'error', 'error_message': 'Order ID not found.'}
      """
      # ... function implementation to fetch status ...
      if status_details := fetch_status_from_backend(order_id):
        return {
            "status": "success",
            "order": {
                "state": status_details.state,
                "tracking_number": status_details.tracking,
            },
        }
      else:
        return {"status": "error", "error_message": f"Order ID {order_id} not found."}

    ```

=== "Java"

    ```java
    /**
     * Retrieves the current weather report for a specified city.
     *
     * @param city The city for which to retrieve the weather report.
     * @param toolContext The context for the tool.
     * @return A dictionary containing the weather information.
     */
    public static Map<String, Object> getWeatherReport(String city, ToolContext toolContext) {
        Map<String, Object> response = new HashMap<>();
        if (city.toLowerCase(Locale.ROOT).equals("london")) {
            response.put("status", "success");
            response.put(
                    "report",
                    "The current weather in London is cloudy with a temperature of 18 degrees Celsius and a"
                            + " chance of rain.");
        } else if (city.toLowerCase(Locale.ROOT).equals("paris")) {
            response.put("status", "success");
            response.put("report", "The weather in Paris is sunny with a temperature of 25 degrees Celsius.");
        } else {
            response.put("status", "error");
            response.put("error_message", String.format("Weather information for '%s' is not available.", city));
        }
        return response;
    }
    ```

* **Simplicity and Focus:**
    * **Keep Tools Focused:** Each tool should ideally perform one well-defined task.
    * **Fewer Parameters are Better:** Models generally handle tools with fewer, clearly defined parameters more reliably than those with many optional or complex ones.
    * **Use Simple Data Types:** Prefer basic types (`str`, `int`, `bool`, `float`, `List[str]`, in **Python**, or `int`, `byte`, `short`, `long`, `float`, `double`, `boolean` and `char` in **Java**) over complex custom classes or deeply nested structures as parameters when possible.
    * **Decompose Complex Tasks:** Break down functions that perform multiple distinct logical steps into smaller, more focused tools. For instance, instead of a single `update_user_profile(profile: ProfileObject)` tool, consider separate tools like `update_user_name(name: str)`, `update_user_address(address: str)`, `update_user_preferences(preferences: list[str])`, etc. This makes it easier for the LLM to select and use the correct capability.

By adhering to these guidelines, you provide the LLM with the clarity and structure it needs to effectively utilize your custom function tools, leading to more capable and reliable agent behavior.

## Toolsets: Grouping and Dynamically Providing Tools ![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python. Java support is planned/coming soon."}

Beyond individual tools, ADK introduces the concept of a **Toolset** via the `BaseToolset` interface (defined in `google.adk.tools.base_toolset`). A toolset allows you to manage and provide a collection of `BaseTool` instances, often dynamically, to an agent.

This approach is beneficial for:

*   **Organizing Related Tools:** Grouping tools that serve a common purpose (e.g., all tools for mathematical operations, or all tools interacting with a specific API).
*   **Dynamic Tool Availability:** Enabling an agent to have different tools available based on the current context (e.g., user permissions, session state, or other runtime conditions). The `get_tools` method of a toolset can decide which tools to expose.
*   **Integrating External Tool Providers:** Toolsets can act as adapters for tools coming from external systems, like an OpenAPI specification or an MCP server, converting them into ADK-compatible `BaseTool` objects.

### The `BaseToolset` Interface

Any class acting as a toolset in ADK should implement the `BaseToolset` abstract base class. This interface primarily defines two methods:

*   **`async def get_tools(...) -> list[BaseTool]:`**
    This is the core method of a toolset. When an ADK agent needs to know its available tools, it will call `get_tools()` on each `BaseToolset` instance provided in its `tools` list.
    *   It receives an optional `readonly_context` (an instance of `ReadonlyContext`). This context provides read-only access to information like the current session state (`readonly_context.state`), agent name, and invocation ID. The toolset can use this context to dynamically decide which tools to return.
    *   It **must** return a `list` of `BaseTool` instances (e.g., `FunctionTool`, `RestApiTool`).

*   **`async def close(self) -> None:`**
    This asynchronous method is called by the ADK framework when the toolset is no longer needed, for example, when an agent server is shutting down or the `Runner` is being closed. Implement this method to perform any necessary cleanup, such as closing network connections, releasing file handles, or cleaning up other resources managed by the toolset.

### Using Toolsets with Agents

You can include instances of your `BaseToolset` implementations directly in an `LlmAgent`'s `tools` list, alongside individual `BaseTool` instances.

When the agent initializes or needs to determine its available capabilities, the ADK framework will iterate through the `tools` list:

*   If an item is a `BaseTool` instance, it's used directly.
*   If an item is a `BaseToolset` instance, its `get_tools()` method is called (with the current `ReadonlyContext`), and the returned list of `BaseTool`s is added to the agent's available tools.

### Example: A Simple Math Toolset

Let's create a basic example of a toolset that provides simple arithmetic operations.

```py
--8<-- "examples/python/snippets/tools/overview/toolset_example.py:init"
```

In this example:

*   `SimpleMathToolset` implements `BaseToolset` and its `get_tools()` method returns `FunctionTool` instances for `add_numbers` and `subtract_numbers`. It also customizes their names using a prefix.
*   The `calculator_agent` is configured with both an individual `greet_tool` and an instance of `SimpleMathToolset`.
*   When `calculator_agent` is run, ADK will call `math_toolset_instance.get_tools()`. The agent's LLM will then have access to `greet_user`, `calculator_add_numbers`, and `calculator_subtract_numbers` to handle user requests.
*   The `add_numbers` tool demonstrates writing to `tool_context.state`, and the agent's instruction mentions reading this state.
*   The `close()` method is called to ensure any resources held by the toolset are released.

Toolsets offer a powerful way to organize, manage, and dynamically provide collections of tools to your ADK agents, leading to more modular, maintainable, and adaptable agentic applications.
