# Function tools

When pre-built ADK tools don't meet your requirements, you can create custom *function tools*. Building function tools allows you to create tailored functionality, such as connecting to proprietary databases or implementing unique algorithms.
For example, a function tool, `myfinancetool`, might be a function that calculates a specific financial metric. ADK also supports long running functions, so if that calculation takes a while, the agent can continue working on other tasks.

ADK offers several ways to create functions tools, each suited to different levels of complexity and control:

*  [Function Tools](#function-tool)
*  [Long Running Function Tools](#long-run-tool)
*  [Agents-as-a-Tool](#agent-tool)

## Function Tools {#function-tool}

Transforming a Python function into a tool is a straightforward way to integrate custom logic into your agents. When you assign a function to an agent’s `tools` list, the framework automatically wraps it as a `FunctionTool`.

### How it Works

The ADK framework automatically inspects your Python function's signature—including its name, docstring, parameters, type hints, and default values—to generate a schema. This schema is what the LLM uses to understand the tool's purpose, when to use it, and what arguments it requires.

### Defining Function Signatures

A well-defined function signature is crucial for the LLM to use your tool correctly.

#### Parameters

You can define functions with required parameters, optional parameters, and variadic arguments. Here’s how each is handled:

##### Required Parameters
A parameter is considered **required** if it has a type hint but **no default value**. The LLM must provide a value for this argument when it calls the tool.

???+ "Example: Required Parameters"
    
    In this example, both `city` and `unit` are mandatory. If the LLM tries to call `get_weather` without one of them, the ADK will return an error to the LLM, prompting it to correct the call.

##### Optional Parameters with Default Values
A parameter is considered **optional** if you provide a **default value**. This is the standard Python way to define optional arguments. The ADK correctly interprets these and does not list them in the `required` field of the tool schema sent to the LLM.

???+ "Example: Optional Parameter with Default Value"
    
    Here, `flexible_days` is optional. The LLM can choose to provide it, but it's not required.

##### Optional Parameters with `typing.Optional`
You can also mark a parameter as optional using `typing.Optional[SomeType]` or the `| None` syntax (Python 3.10+). This signals that the parameter can be `None`. When combined with a default value of `None`, it behaves as a standard optional parameter.

???+ "Example: `typing.Optional`"
    

##### Variadic Parameters (`*args` and `**kwargs`)
While you can include `*args` (variable positional arguments) and `**kwargs` (variable keyword arguments) in your function signature for other purposes, they are **ignored by the ADK framework** when generating the tool schema for the LLM. The LLM will not be aware of them and cannot pass arguments to them. It's best to rely on explicitly defined parameters for all data you expect from the LLM.

#### Return Type

The preferred return type for a Function Tool is a **dictionary**. This allows you to structure the response with key-value pairs, providing context and clarity to the LLM. If your function returns a type other than a dictionary, the framework automatically wraps it into a dictionary with a single key named **"result"**.

Strive to make your return values as descriptive as possible. *For example,* instead of returning a numeric error code, return a dictionary with an "error_message" key containing a human-readable explanation. **Remember that the LLM**, not a piece of code, needs to understand the result. As a best practice, include a "status" key in your return dictionary to indicate the overall outcome (e.g., "success", "error", "pending"), providing the LLM with a clear signal about the operation's state.

#### Docstrings

The docstring of your function serves as the tool's **description** and is sent to the LLM. Therefore, a well-written and comprehensive docstring is crucial for the LLM to understand how to use the tool effectively. Clearly explain the purpose of the function, the meaning of its parameters, and the expected return values.

### Passing Data Between Tools

When an agent calls multiple tools in a sequence, you might need to pass data from one tool to another. The recommended way to do this is by using the `temp:` prefix in the session state.

A tool can write data to a `temp:` variable, and a subsequent tool can read it. This data is only available for the current invocation and is discarded afterwards.

!!! note "Shared Invocation Context"
    All tool calls within a single agent turn share the same `InvocationContext`. This means they also share the same temporary (`temp:`) state, which is how data can be passed between them.

### Example

??? "Example"

    This tool is a python function which obtains the Stock price of a given Stock ticker/ symbol.

    <u>Note</u>: You need to `pip install yfinance` library before using this tool.

    
    The return value from this tool will be wrapped into a dictionary.

    ```json
    {"result": "$123"}
    ```

### Best Practices

While you have considerable flexibility in defining your function, remember that simplicity enhances usability for the LLM. Consider these guidelines:

* **Fewer Parameters are Better:** Minimize the number of parameters to reduce complexity.  
* **Simple Data Types:** Favor primitive data types like `str` and `int` over custom classes whenever possible.  
* **Meaningful Names:** The function's name and parameter names significantly influence how the LLM interprets and utilizes the tool. Choose names that clearly reflect the function's purpose and the meaning of its inputs. Avoid generic names like `do_stuff()` or `beAgent()`.
* **Build for Parallel Execution:** Improve function calling performance when multiple tools are run by building for asynchronous operation. For information on enabling parallel execution for tools, see
[Increase tool performance with parallel execution](/adk-docs/tools/performance/).

## Long Running Function Tools {#long-run-tool}

This tool is designed to help you start and manage tasks that are handled outside the operation of your agent workflow, and require a significant amount of processing time, without blocking the agent's execution. This tool is a subclass of `FunctionTool`.

When using a `LongRunningFunctionTool`, your function can initiate a long-running operation and signal the agent to pause. The agent client can then resume the agent's run with an intermediate or final response. This is particularly useful for scenarios like human-in-the-loop, where an agent needs to wait for human approval before proceeding.

!!! warning "Warning: Execution handling"
    Long Running Function Tools are designed to help you start and *manage* long running
    tasks as part of your agent workflow, but ***not perform*** the actual, long task.
    For tasks that require significant time to complete, you should implement a separate
    server to do the task.

### How it Works

1.  **Initiation and Pausing:** When the LLM calls a `LongRunningFunctionTool`, your function starts the long-running operation and returns a result indicating that the operation is pending. The ADK framework detects this and pauses the agent's invocation.

2.  **Resuming:** The agent client is responsible for monitoring the long-running operation. Once the operation is complete (or has an intermediate update), the client can resume the agent's run by sending the result back to the agent.

3.  **Framework Handling:** The ADK framework receives the result from the client and resumes the agent's execution. The result is passed back to the LLM as a `FunctionResponse`, allowing the agent to continue its work.

### Creating the Tool

To create a long-running function tool, you define a function and wrap it with the `LongRunningFunctionTool` class.

=== "Python"

    ```python
    from google.adk.tools import LongRunningFunctionTool

    # Define a function that initiates a long-running task
    def ask_for_approval(purpose: str, amount: float) -> dict:
      """Ask for approval for the reimbursement."""
      # In a real application, this would trigger an external process,
      # like creating a ticket in an approval system.
      return {
          'status': 'pending',
          'amount': amount,
          'ticketId': 'reimbursement-ticket-001',
      }

    # Wrap the function with LongRunningFunctionTool
    approval_tool = LongRunningFunctionTool(func=ask_for_approval)

    # Include the tool in your agent's tool list
    my_agent = LlmAgent(
        # ... other agent configuration
        tools=[approval_tool],
    )
    ```

### Resuming the Invocation

After the `ask_for_approval` tool is called, the agent's invocation will be paused. The agent client will receive an event indicating that a function call has been made and is pending. The client can then wait for the external process (e.g., the manager's approval) to complete.

Once the result is available, the client can resume the invocation by running the agent again with the result of the long-running operation. The result should be formatted as a `FunctionResponse`.

```python
# Assume 'runner' is your configured Runner instance and 'session_id' is the
# ID of the session that was paused.

# The manager approves the request.
approval_result = {
    'status': 'approved',
    'ticketId': 'reimbursement-ticket-001',
}

# Create a FunctionResponse with the result.
# The 'id' of the FunctionResponse must match the 'id' of the original
# FunctionCall event.
function_response = types.FunctionResponse(
    name='ask_for_approval',
    id='<function_call_id_from_event>',
    response=approval_result
)

# Resume the agent's run with the FunctionResponse.
events = runner.run(
    session_id=session_id,
    new_message=types.Content(parts=[types.Part(function_response=function_response)])
)

# The agent will now continue its execution with the result of the approval.
```

## Agent-as-a-Tool {#agent-tool}

This powerful feature allows you to leverage the capabilities of other agents within your system by calling them as tools. The Agent-as-a-Tool enables you to invoke another agent to perform a specific task, effectively **delegating responsibility**. This is conceptually similar to creating a Python function that calls another agent and uses the agent's response as the function's return value.

### Key difference from sub-agents

It's important to distinguish an Agent-as-a-Tool from a Sub-Agent.

* **Agent-as-a-Tool:** When Agent A calls Agent B as a tool (using Agent-as-a-Tool), Agent B's answer is **passed back** to Agent A, which then summarizes the answer and generates a response to the user. Agent A retains control and continues to handle future user input.  

* **Sub-agent:** When Agent A calls Agent B as a sub-agent, the responsibility of answering the user is completely **transferred to Agent B**. Agent A is effectively out of the loop. All subsequent user input will be answered by Agent B.

### Usage

To use an agent as a tool, wrap the agent with the AgentTool class.

=== "Python"

    ```python
    tools=[AgentTool(agent=agent_b)]
    ```



### Customization

The `AgentTool` class provides the following attributes for customizing its behavior:

* **skip\_summarization: bool:** If set to True, the framework will **bypass the LLM-based summarization** of the tool agent's response. This can be useful when the tool's response is already well-formatted and requires no further processing.

??? "Example"

    

### How it works

1. When the `main_agent` receives the long text, its instruction tells it to use the 'summarize' tool for long texts.  
2. The framework recognizes 'summarize' as an `AgentTool` that wraps the `summary_agent`.  
3. Behind the scenes, the `main_agent` will call the `summary_agent` with the long text as input.  
4. The `summary_agent` will process the text according to its instruction and generate a summary.  
5. **The response from the `summary_agent` is then passed back to the `main_agent`.**  
6. The `main_agent` can then take the summary and formulate its final response to the user (e.g., "Here's a summary of the text: ...")