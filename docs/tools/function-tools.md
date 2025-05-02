# Function tools

## What are function tools?

When out-of-the-box tools don't fully meet specific requirements, developers can create custom function tools. This allows for **tailored functionality**, such as connecting to proprietary databases or implementing unique algorithms.

*For example,* a function tool, "myfinancetool", might be a function that calculates a specific financial metric. ADK also supports long running functions, so if that calculation takes a while, the agent can continue working on other tasks.

ADK offers several ways to create functions tools, each suited to different levels of complexity and control:

1. Function Tool
2. Long Running Function Tool
3. Agents-as-a-Tool

## 1. Function Tool

Transforming a function into a tool is a straightforward way to integrate custom logic into your agents. In fact, when you assign a Python function to an agent’s tools list, the framework will automatically wrap it as a Function Tool for you. This approach offers flexibility and quick integration.

### Parameters

Define your function parameters using standard **JSON-serializable types** (e.g., string, integer, list, dictionary). It's important to avoid setting default values for parameters, as the language model (LLM) does not currently support interpreting them.

### Return Type

The preferred return type for a Python Function Tool is a **dictionary**. This allows you to structure the response with key-value pairs, providing context and clarity to the LLM. If your function returns a type other than a dictionary, the framework automatically wraps it into a dictionary with a single key named **"result"**.

Strive to make your return values as descriptive as possible. *For example,* instead of returning a numeric error code, return a dictionary with an "error\_message" key containing a human-readable explanation. **Remember that the LLM**, not a piece of code, needs to understand the result. As a best practice, include a "status" key in your return dictionary to indicate the overall outcome (e.g., "success", "error", "pending"), providing the LLM with a clear signal about the operation's state.

### Docstring

The docstring of your function serves as the tool's description and is sent to the LLM. Therefore, a well-written and comprehensive docstring is crucial for the LLM to understand how to use the tool effectively. Clearly explain the purpose of the function, the meaning of its parameters, and the expected return values.

??? "Example"

    This tool is a python function which obtains the Stock price of a given Stock ticker/ symbol.

    <u>Note</u>: You need to `pip install yfinance` library before using this tool.

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/func_tool.py"
    ```

    The return value from this tool will be wrapped into a dictionary.

    ```json
    {"result": "$123"}
    ```

### Best Practices

While you have considerable flexibility in defining your function, remember that simplicity enhances usability for the LLM. Consider these guidelines:

* **Fewer Parameters are Better:** Minimize the number of parameters to reduce complexity.  
* **Simple Data Types:** Favor primitive data types like `str` and `int` over custom classes whenever possible.  
* **Meaningful Names:** The function's name and parameter names significantly influence how the LLM interprets and utilizes the tool. Choose names that clearly reflect the function's purpose and the meaning of its inputs. Avoid generic names like `do_stuff()`.  

## 2. Long Running Function Tool

Designed for tasks that require a significant amount of processing time without blocking the agent's execution. This tool is a subclass of `FunctionTool`.

When using a `LongRunningFunctionTool`, your Python function can initiate the long-running operation and optionally return an **intermediate result** to keep the model and user informed about the progress. The agent can then continue with other tasks. An example is the human-in-the-loop scenario where the agent needs human approval before proceeding with a task.

### How it Works

You wrap a Python *generator* function (a function using `yield`) with `LongRunningFunctionTool`.

1. **Initiation:** When the LLM calls the tool, your generator function starts executing.

2. **Intermediate Updates (`yield`):** Your function should yield intermediate Python objects (typically dictionaries) periodically to report progress. The ADK framework takes each yielded value and sends it back to the LLM packaged within a `FunctionResponse`. This allows the LLM to inform the user (e.g., status, percentage complete, messages).

3. **Completion (`return`):** When the task is finished, the generator function uses `return` to provide the final Python object result.

4. **Framework Handling:** The ADK framework manages the execution. It sends each yielded value back as an intermediate `FunctionResponse`. When the generator completes, the framework sends the returned value as the content of the final `FunctionResponse`, signaling the end of the long-running operation to the LLM.

### Creating the Tool

Define your generator function and wrap it using the `LongRunningFunctionTool` class:

```py
from google.adk.tools import LongRunningFunctionTool

# Define your generator function (see example below)
def my_long_task_generator(*args, **kwargs):
    # ... setup ...
    yield {"status": "pending", "message": "Starting task..."} # Framework sends this as FunctionResponse
    # ... perform work incrementally ...
    yield {"status": "pending", "progress": 50}               # Framework sends this as FunctionResponse
    # ... finish work ...
    return {"status": "completed", "result": "Final outcome"} # Framework sends this as final FunctionResponse

# Wrap the function
my_tool = LongRunningFunctionTool(func=my_long_task_generator)
```

### Intermediate Updates

Yielding structured Python objects (like dictionaries) is crucial for providing meaningful updates. Include keys like:

* status: e.g., "pending", "running", "waiting_for_input"

* progress: e.g., percentage, steps completed

* message: Descriptive text for the user/LLM

* estimated_completion_time: If calculable

Each value you yield is packaged into a FunctionResponse by the framework and sent to the LLM.

### Final Result

The Python object your generator function returns is considered the final result of the tool execution. The framework packages this value (even if it's None) into the content of the final `FunctionResponse` sent back to the LLM, indicating the tool execution is complete.

??? "Example: File Processing Simulation"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/file_processor.py"
    ```

#### Key aspects of this example

* **process_large_file**: This generator simulates a lengthy operation, yielding intermediate status/progress dictionaries.

* **`LongRunningFunctionTool`**: Wraps the generator; the framework handles sending yielded updates and the final return value as sequential FunctionResponses.

* **Agent instruction**: Directs the LLM to use the tool and understand the incoming FunctionResponse stream (progress vs. completion) for user updates.

* **Final return**: The function returns the final result dictionary, which is sent in the concluding FunctionResponse to indicate completion.

## 3. Agent-as-a-Tool

This powerful feature allows you to leverage the capabilities of other agents within your system by calling them as tools. The Agent-as-a-Tool enables you to invoke another agent to perform a specific task, effectively **delegating responsibility**. This is conceptually similar to creating a Python function that calls another agent and uses the agent's response as the function's return value.

### Key difference from sub-agents

It's important to distinguish an Agent-as-a-Tool from a Sub-Agent.

* **Agent-as-a-Tool:** When Agent A calls Agent B as a tool (using Agent-as-a-Tool), Agent B's answer is **passed back** to Agent A, which then summarizes the answer and generates a response to the user. Agent A retains control and continues to handle future user input.  

* **Sub-agent:** When Agent A calls Agent B as a sub-agent, the responsibility of answering the user is completely **transferred to Agent B**. Agent A is effectively out of the loop. All subsequent user input will be answered by Agent B.

### Usage

To use an agent as a tool, wrap the agent with the AgentTool class.

```py
tools=[AgentTool(agent=agent_b)]
```

### Customization

The `AgentTool` class provides the following attributes for customizing its behavior:

* **skip\_summarization: bool:** If set to True, the framework will **bypass the LLM-based summarization** of the tool agent's response. This can be useful when the tool's response is already well-formatted and requires no further processing.

??? "Example"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/summarizer.py"
    ```

### How it works

1. When the `main_agent` receives the long text, its instruction tells it to use the 'summarize' tool for long texts.  
2. The framework recognizes 'summarize' as an `AgentTool` that wraps the `summary_agent`.  
3. Behind the scenes, the `main_agent` will call the `summary_agent` with the long text as input.  
4. The `summary_agent` will process the text according to its instruction and generate a summary.  
5. **The response from the `summary_agent` is then passed back to the `main_agent`.**  
6. The `main_agent` can then take the summary and formulate its final response to the user (e.g., "Here's a summary of the text: ...")
