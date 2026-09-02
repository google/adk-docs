# Increase tool performance with parallel execution

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.10.0</span>
</div>

Starting with Agent Development Kit (ADK) version 1.10.0 for Python, the framework
attempts to run any agent-requested
[function tools](/tools-custom/function-tools/)
in parallel. This behavior can significantly improve the performance and
responsiveness of your agents, particularly for agents that rely on multiple
external APIs or long-running tasks. For example, if you have 3 tools that each
take 2 seconds, by running them in parallel, the total execution time will be
closer to 2 seconds, instead of 6 seconds. The ability to run tool functions
parallel can improve the performance of your agents, particularly in the
following scenarios:

-   **Research tasks:** Where the agent collects information from multiple
    sources before proceeding to the next stage of the workflow.
-   **API calls:** Where the agent accesses several APIs independently, such
    as searching for available flights using APIs from multiple airlines.
-   **Publishing and communication tasks:** When the agent needs to publish
    or communicate through multiple, independent channels or multiple recipients.

However, your custom tools must be built with asynchronous execution support to
enable this performance improvement. This guide explains how parallel tool
execution works in the ADK and how to build your tools to take full advantage of
this processing feature.

!!! warning
    Any ADK Tools that use synchronous processing in a set of tool function
    calls will block other tools from executing in parallel, even if the other
    tools allow for parallel execution.

## Build parallel-ready tools

Enable parallel execution of your tool functions by defining them as
asynchronous functions. In Python code, this means using `async def` and `await`
syntax which allows the ADK to run them concurrently in an `asyncio` event loop.
The following sections show examples of agent tools built for parallel
processing and asynchronous operations.

### Example of http web call

The following code example show how to modify the `get_weather()` function to
operate asynchronously and allow for parallel execution:

```python
--8<-- "examples/inline/python/tools-custom/performance/001-example-of-http-web-call.py"
```

### Example of database call

The following code example show how to write a database calling function to
operate asynchronously:

```python
--8<-- "examples/inline/python/tools-custom/performance/002-example-of-database-call.py"
```

### Example of yielding behavior for long loops

In cases where a tool is processing multiple requests or numerous long-running
requests, consider adding yielding code to allow other tools to execute, as
shown in the following code sample:

```python
--8<-- "examples/inline/python/tools-custom/performance/003-example-of-yielding-behavior-for-long-lo.py"
```

!!! tip "Important"
    Use the `asyncio.sleep()` function for pauses to avoid blocking
    execution of other functions.

### Example of thread pools for intensive operations

When performing processing-intensive functions, consider creating thread pools
for better management of available computing resources, as shown in the
following example:

```python
--8<-- "examples/inline/python/tools-custom/performance/004-example-of-thread-pools-for-intensive-op.py"
```

### Example of process chunking

When performing processes on long lists or large amounts of data, consider
combining a thread pool technique with dividing up processing into chunks of
data, and yielding processing time between the chunks, as shown in the following
example:

```python
--8<-- "examples/inline/python/tools-custom/performance/005-example-of-process-chunking.py"
```

## Write parallel-ready prompts and tool descriptions

When building prompts for AI models, consider explicitly specifying or hinting
that function calls be made in parallel. The following example of an AI prompt
directs the model to use tools in parallel:

```none
When users ask for multiple pieces of information, always call functions in
parallel.

  Examples:
  - "Get weather for London and currency rate USD to EUR" → Call both functions
    simultaneously
  - "Compare cities A and B" → Call get_weather, get_population, get_distance in
    parallel
  - "Analyze multiple stocks" → Call get_stock_price for each stock in parallel

  Always prefer multiple specific function calls over single complex calls.
```

The following example shows a tool function description that hints at more
efficient use through parallel execution:

```python
--8<-- "examples/inline/python/tools-custom/performance/006-write-parallel-ready-prompts-and-tool-de.py"
```

## Next steps

For more information on building Tools for agents and function calling, see
[Function Tools](/tools-custom/function-tools/). For
more detailed examples of tools that take advantage of parallel processing, see
the samples in the
[adk-python](https://github.com/google/adk-python/tree/main/contributing/samples/tools/parallel_functions)
repository.
