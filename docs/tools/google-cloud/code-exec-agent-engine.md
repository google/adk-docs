# Code Execution Tool with Agent Engine

The Agent Engine Code Execution ADK Tool provides a low-latency, highly
efficient method for running AI-generated code using the
[Google Cloud Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
service. This tool is designed for fast execution, tailored for agentic workflows,
and uses sandboxed environments for improved security. The Code Execution tool 
allows code and data to persist over multiple requests, enabling complex, 
multi-step coding tasks, including:

-   **Code development and debugging:** Create agent tasks that test and
    iterate on versions of code over multiple requests.
-   **Code with data analysis:** Upload data files up to 100MB, and run
    multiple code-based analyses without the need to reload data for each code run.

This code execution tool is part of the Agent Engine suite, however you do not
have to deploy your agent to Agent Engine to use it. You can run your agent
locally or with other services and use this tool. For more information about the
Code Execution feature in Agent Engine, see the
[Agent Engine Code Execution](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/overview)
documentation.

!!! example "Preview release"
    The Agent Engine Code Execution feature is a Preview release. For
    more information, see the
    [launch stage descriptions](https://cloud.google.com/products#product-launch-stages).

## Use the Tool

Using the Agent Engine Code Execution tool requires that you create a sandbox
environment with Google Cloud Agent Engine before using the tool with an ADK
agent.

To use the Code Execution tool with your ADK agent:

1.  Follow the instructions in the Agent Engine
    [Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart)
    to create a code execution sandbox environment.
1.  Create an ADK agent with settings to access the Google Cloud project
    where you created the sandbox environment.
1.  The following code example shows an agent configured to use the Code
    Executor tool. Replace `SANDBOX_RESOURCE_NAME` with the sandbox environment 
    resource name you created.

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

root_agent = Agent(
    model="gemini-2.5-flash",
    name="agent_engine_code_execution_agent",
    instruction="You are a helpful agent that can write and execute code to answer questions and solve problems.",
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
    ),
)
```

For details on the expected format of the `sandbox_resource_name` value, and the
alternative `agent_engine_resource_name` parameter, see [Configuration
parameters](#config-parameters). For a more advanced example, including
recommended system instructions for the tool, see the [Advanced
example](#advanced-example) or the full 
[agent code example](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution).

## How it works

The `AgentEngineCodeExecutor` Tool maintains a single sandbox throughout an
agent's task, meaning the sandbox's state persists across all operations within
an ADK workflow session.

1.  **Sandbox creation:** For multi-step tasks requiring code execution,
    the Agent Engine creates a sandbox with specified language and machine
    configurations, isolating the code execution environment. If no sandbox is
    pre-created, the code execution tool will automatically create one using
    default settings.
1.  **Code execution with persistence:** AI-generated code for a tool call
    is streamed to the sandbox and then executed within the isolated
    environment. After execution, the sandbox *remains active* for subsequent
    tool calls within the same session, preserving variables, imported modules,
    and file state for the next tool call from the same agent.
1.  **Result retrieval:** The standard output, and any captured error
    streams are collected and passed back to the calling agent.
1.  **Sandbox clean up:** Once the agent task or conversation concludes, the
    agent can explicitly delete the sandbox, or rely on the TTL feature of the
    sandbox specified when creating the sandbox.

## Key benefits

-   **Persistent state:** Solve complex tasks where data manipulation or
    variable context must carry over between multiple tool calls.
-   **Targeted Isolation:** Provides robust process-level isolation,
    ensuring that tool code execution is safe while remaining lightweight.
-   **Agent Engine integration:** Tightly integrated into the Agent Engine
    tool-use and orchestration layer.
-   **Low-latency performance:** Designed for speed, allowing agents to
    execute complex tool-use workflows efficiently without significant overhead.
-   **Flexible compute configurations:** Create sandboxes with specific
    programming language, processing power, and memory configurations.

## System requirements¶

The following requirements must be met to successfully use the Agent Engine
Code Execution tool with your ADK agents:

-   Google Cloud project with Vertex API enabled
-   Agent's service account requires **roles/aiplatform.user** role, which
    allow it to:
    -   Create, get, list and delete code execution sandboxes
    -   Execute code execution sandbox

## Configuration parameters {#config-parameters}

The Agent Engine Code Execution tool has the following parameters. You must set
one of the following resource parameters:

-   **`sandbox_resource_name`** : A sandbox resource path to an
    existing sandbox environment it uses for each tool call. The expected
string format is as follows:
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}/sandboxEnvironments/{$SANDBOX_ENVIRONMENT_ID}
    
    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172/sandboxEnvironments/6545148888889161728
    ```
-   **`agent_engine_resource_name`**: Agent Engine resource name where the tool
creates a sandbox environment. The expected string format is as follows:
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}
    
    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172
    ```

You can use Google Cloud Agent Engine's API to configure Agent Engine sandbox
environments separately using a Google Cloud client connection, including the
following settings:

-   **Programming languages,** including Python and JavaScript
-   **Compute environment**, including CPU and memory sizes

For more information on connecting to Google Cloud Agent Engine and configuring
sandbox environments, see the Agent Engine
[Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart#create_a_sandbox).

## Advanced example {#advanced-example}

The following example code shows how to implement use of the Code Executor tool
in an ADK agent. This example includes a `base_system_instruction` clause to set
the operating guidelines for code execution. This instruction clause is
optional, but strongly recommended for getting the best results from this tool.

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

def base_system_instruction():
  """Returns: data science agent system instruction."""

  return """
  # Guidelines

  **Objective:** Assist the user in achieving their data analysis goals, **with emphasis on avoiding assumptions and ensuring accuracy.** Reaching that goal can involve multiple steps. When you need to generate code, you **don't** need to solve the goal in one go. Only generate the next step at a time.

  **Code Execution:** All code snippets provided will be executed within the sandbox environment.

  **Statefulness:** All code snippets are executed and the variables stays in the environment. You NEVER need to re-initialize variables. You NEVER need to reload files. You NEVER need to re-import libraries.

  **Output Visibility:** Always print the output of code execution to visualize results, especially for data exploration and analysis. For example:
    - To look a the shape of a pandas.DataFrame do:
      ```tool_code
      print(df.shape)
      ```
      The output will be presented to you as:
      ```tool_outputs
      (49, 7)

      ```
    - To display the result of a numerical computation:
      ```tool_code
      x = 10 ** 9 - 12 ** 5
      print(f'{{x=}}')
      ```
      The output will be presented to you as:
      ```tool_outputs
      x=999751168

      ```
    - You **never** generate ```tool_outputs yourself.
    - You can then use this output to decide on next steps.
    - Print just variables (e.g., `print(f'{{variable=}}')`.

  **No Assumptions:** **Crucially, avoid making assumptions about the nature of the data or column names.** Base findings solely on the data itself. Always use the information obtained from `explore_df` to guide your analysis.

  **Available files:** Only use the files that are available as specified in the list of available files.

  **Data in prompt:** Some queries contain the input data directly in the prompt. You have to parse that data into a pandas DataFrame. ALWAYS parse all the data. NEVER edit the data that are given to you.

  **Answerability:** Some queries may not be answerable with the available data. In those cases, inform the user why you cannot process their query and suggest what type of data would be needed to fulfill their request.

  """

root_agent = Agent(
    model="gemini-2.5-flash",
    name="agent_engine_code_execution_agent",
    instruction=base_system_instruction() + """


You need to assist the user with their queries by looking at the data and the context in the conversation.
You final answer should summarize the code and code execution relevant to the user query.

You should include all pieces of data to answer the user query, such as the table from code execution results.
If you cannot answer the question directly, you should follow the guidelines above to generate the next step.
If the question can be answered directly with writing any code, you should do that.
If you doesn't have enough data to answer the question, you should ask for clarification from the user.

You should NEVER install any package on your own like `pip install ...`.
When plotting trends, you should make sure to sort and order the data by the x-axis.


""",
    code_executor=AgentEngineSandboxCodeExecutor(
        # Replace with your sandbox resource name if you already have one.
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
        # Replace with agent engine resource name used for creating sandbox if
        # sandbox_resource_name is not set:
        # agent_engine_resource_name="AGENT_ENGINE_RESOURCE_NAME",
    ),
)
```

For a complete version of an ADK agent using this example code, see the
[agent_engine_code_execution sample](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution).
